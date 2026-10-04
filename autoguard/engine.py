"""Coordinates scanners and triggers the block action."""
import logging
import threading
import time

from . import actions
from .visual_detector import VisualScanner
from .window_monitor import TitleScanner


class Guard:
    def __init__(self, settings, ui_log):
        self.settings = settings
        self.ui_log = ui_log
        self._threads = []
        self._lock = threading.Lock()
        self._last_action = 0.0
        self.running = False

    def log(self, msg: str):
        logging.info(msg)
        self.ui_log(msg)

    def start(self):
        if self.running:
            return
        self.running = True
        self._threads = [
            TitleScanner(self.settings, self._trigger),
            VisualScanner(self.settings, self._trigger, self.log),
        ]
        for t in self._threads:
            t.start()
        self.log("Protection started")

    def stop(self):
        if not self.running:
            return
        self.running = False
        for t in self._threads:
            t.stop()
        self._threads = []
        self.log("Protection stopped")

    def _trigger(self, source: str, detail: str):
        with self._lock:
            now = time.time()
            if not self.running or now - self._last_action < self.settings.cooldown:
                return
            self._last_action = now
        self.log(f"BLOCKED [{source}] {detail}")
        try:
            self.log("  -> " + actions.block(self.settings.kill_browser))
        except Exception as exc:
            self.log(f"  -> action failed: {exc}")
