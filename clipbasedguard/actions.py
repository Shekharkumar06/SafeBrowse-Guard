"""Windows actions: close tab, kill browser, show desktop."""
import time

import psutil
import pyautogui
import win32gui
import win32process

from .config import BROWSER_PROCESSES

pyautogui.FAILSAFE = False  # don't raise when mouse is in a screen corner


def foreground_info():
    """Return (window_title, process_name_lower) of the active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd) or ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return title, psutil.Process(pid).name().lower()
    except Exception:
        return "", ""


def close_active_tab() -> None:
    pyautogui.hotkey("ctrl", "w")


def show_desktop() -> None:
    pyautogui.hotkey("win", "d")


def kill_browsers() -> int:
    killed = 0
    for p in psutil.process_iter(["name"]):
        try:
            if (p.info["name"] or "").lower() in BROWSER_PROCESSES:
                p.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed


def block(kill_browser: bool = False) -> str:
    """Close offending content, then show the desktop. Returns a short summary."""
    _, proc = foreground_info()
    summary = []
    if proc in BROWSER_PROCESSES:
        if kill_browser:
            summary.append(f"killed {kill_browsers()} browser process(es)")
        else:
            close_active_tab()
            summary.append("Ctrl+W sent")
        time.sleep(0.15)
    else:
        # Never send Ctrl+W to non-browser apps (could close documents).
        summary.append(f"foreground '{proc or '?'}' is not a browser")
    show_desktop()
    summary.append("Win+D sent")
    return ", ".join(summary)
