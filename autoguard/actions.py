"""Windows actions: close tab, kill browser, show desktop."""
import ctypes
import time

import psutil
import win32gui
import win32process

from .config import BROWSER_PROCESSES

_user32 = ctypes.windll.user32
KEYUP = 0x0002
VK_CTRL, VK_W, VK_LWIN, VK_D = 0x11, 0x57, 0x5B, 0x44


def _hotkey(*vks: int) -> None:
    for vk in vks:
        _user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.03)
    for vk in reversed(vks):
        _user32.keybd_event(vk, 0, KEYUP, 0)


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
    _hotkey(VK_CTRL, VK_W)


def show_desktop() -> None:
    _hotkey(VK_LWIN, VK_D)


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
