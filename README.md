# AutoGuard - automatic adult-content blocker (Windows)

## Install
1. Install Python 3.10-3.12 (64-bit) from python.org (tick "Add to PATH").
2. In this folder:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```
   (Or just double-click `run.bat`.)

## How it works
- Title monitor: foreground window title checked every 0.5s against built-in patterns
  (add more in %APPDATA%\AutoGuard\settings.json -> "extra_keywords").
- Visual monitor: mss captures every monitor each second; NudeNet scans it. Needs
  2 consecutive hits at/above the threshold to fire (fewer false alarms).
- On detection: Ctrl+W (or kill browser process), then Win+D.
  Ctrl+W is only sent when the active app is a browser.
- Closing/minimizing the window sends it to the tray. Quit from tray menu.
- Logs: %APPDATA%\AutoGuard\guard.log

## Tuning
- Too many false alarms -> move slider right (0.7+).
- Missing content -> move slider left (0.4-0.5).
- Startup with Windows: put a shortcut to run.bat in shell:startup.

## Notes
- Not tamper-proof: anyone with access can quit it from the tray or Task Manager.
- Everything runs locally; no screenshots are saved or sent anywhere.
