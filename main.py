import ctypes
import logging
import os

from autoguard.config import DATA_DIR, LOG_PATH, Settings

os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(message)s")

try:  # correct screen-capture coordinates on scaled displays
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

from autoguard.gui import App  # noqa: E402

if __name__ == "__main__":
    App(Settings.load()).mainloop()
