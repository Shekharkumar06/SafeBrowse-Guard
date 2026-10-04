"""System-tray icon (pystray)."""
import pystray
from PIL import Image, ImageDraw


def _make_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(32, 4), (58, 14), (54, 40), (32, 60), (10, 40), (6, 14)], fill=(30, 136, 229, 255))
    d.line([(20, 32), (29, 41), (45, 22)], fill="white", width=6)
    return img


class Tray:
    def __init__(self, on_show, on_toggle, on_quit, is_running):
        menu = pystray.Menu(
            pystray.MenuItem("Open", lambda *_: on_show(), default=True),
            pystray.MenuItem("Protection ON", lambda *_: on_toggle(),
                             checked=lambda _item: is_running()),
            pystray.MenuItem("Quit", lambda *_: on_quit()),
        )
        self.icon = pystray.Icon("AutoGuard", _make_icon(), "AutoGuard", menu)

    def start(self):
        self.icon.run_detached()

    def stop(self):
        try:
            self.icon.stop()
        except Exception:
            pass
