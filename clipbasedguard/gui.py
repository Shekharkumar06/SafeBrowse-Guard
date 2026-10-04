"""customtkinter GUI."""
import queue
import time

import customtkinter as ctk

from .engine import Guard
from .tray import Tray


class App(ctk.CTk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._q: queue.Queue = queue.Queue()
        self.guard = Guard(settings, lambda m: self._q.put(("log", m)))
        self.tray = Tray(
            on_show=lambda: self._q.put(("call", self.show_window)),
            on_toggle=lambda: self._q.put(("call", self.toggle_from_tray)),
            on_quit=lambda: self._q.put(("call", self.quit_app)),
            is_running=lambda: self.guard.running,
        )

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("AutoGuard")
        self.geometry("460x520")
        self.minsize(420, 480)
        self._build()

        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.bind("<Unmap>", self._on_unmap)
        self.tray.start()
        self.after(150, self._pump)
        self.switch_var.set(1)
        self.toggle()  # auto-start protection

    # ---------- UI ----------
    def _build(self):
        ctk.CTkLabel(self, text="AutoGuard", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(18, 2))
        self.status = ctk.CTkLabel(self, text="Protection: OFF", text_color="gray")
        self.status.pack()

        self.switch_var = ctk.IntVar(value=0)
        ctk.CTkSwitch(self, text="Enable protection", variable=self.switch_var,
                      command=self.toggle).pack(pady=14)

        box = ctk.CTkFrame(self)
        box.pack(fill="x", padx=20, pady=4)
        self.th_label = ctk.CTkLabel(box, text="")
        self.th_label.pack(pady=(10, 0))
        self.slider = ctk.CTkSlider(box, from_=0.20, to=0.95, number_of_steps=75,
                                    command=self._on_threshold)
        self.slider.set(self.settings.threshold)
        self.slider.pack(fill="x", padx=16, pady=(4, 2))
        self.slider.bind("<ButtonRelease-1>", lambda _e: self.settings.save())
        ctk.CTkLabel(box, text="Left = more sensitive  |  Right = stricter (fewer false alarms)",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))
        self._on_threshold(self.settings.threshold)

        self.cb_title = ctk.CTkCheckBox(self, text="Monitor window titles", command=self._opts)
        self.cb_vis = ctk.CTkCheckBox(self, text="Monitor screen (CLIP)", command=self._opts)
        self.cb_kill = ctk.CTkCheckBox(self, text="Kill browser process instead of closing tab",
                                       command=self._opts)
        for cb, val in ((self.cb_title, self.settings.title_monitor),
                        (self.cb_vis, self.settings.visual_monitor),
                        (self.cb_kill, self.settings.kill_browser)):
            cb.pack(anchor="w", padx=26, pady=3)
            cb.select() if val else cb.deselect()

        self.logbox = ctk.CTkTextbox(self, height=150, state="disabled")
        self.logbox.pack(fill="both", expand=True, padx=20, pady=(10, 16))

    def _on_threshold(self, value):
        self.settings.threshold = round(float(value), 2)
        self.th_label.configure(text=f"Bikini/lingerie probability threshold: {self.settings.threshold:.2f}")

    def _opts(self):
        self.settings.title_monitor = bool(self.cb_title.get())
        self.settings.visual_monitor = bool(self.cb_vis.get())
        self.settings.kill_browser = bool(self.cb_kill.get())
        self.settings.save()

    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")

    # ---------- control ----------
    def toggle(self):
        if self.switch_var.get():
            self.guard.start()
        else:
            self.guard.stop()
        self._refresh_status()

    def toggle_from_tray(self):
        self.switch_var.set(0 if self.guard.running else 1)
        self.toggle()

    def _refresh_status(self):
        on = self.guard.running
        self.status.configure(text=f"Protection: {'ON' if on else 'OFF'}",
                              text_color="#2ecc71" if on else "gray")

    # ---------- window / tray ----------
    def _on_unmap(self, _event):
        if self.state() == "iconic":
            self.after(50, self.hide_window)

    def hide_window(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()

    def quit_app(self):
        self.settings.save()
        self.guard.stop()
        self.tray.stop()
        self.destroy()

    def _pump(self):
        try:
            while True:
                kind, payload = self._q.get_nowait()
                self.log(payload) if kind == "log" else payload()
        except queue.Empty:
            pass
        self.after(150, self._pump)
