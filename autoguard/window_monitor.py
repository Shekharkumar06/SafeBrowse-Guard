"""Active-window title monitor (keyword/pattern based)."""
import re
import threading

from .actions import foreground_info
from .config import TITLE_KEYWORDS


class TitleScanner(threading.Thread):
    def __init__(self, settings, on_detect):
        super().__init__(daemon=True, name="TitleScanner")
        self.settings = settings
        self.on_detect = on_detect
        self._stop_evt = threading.Event()
        self._cache_key = None
        self._pattern = None

    def _get_pattern(self):
        words = tuple(TITLE_KEYWORDS) + tuple(self.settings.extra_keywords or [])
        if words != self._cache_key:
            self._pattern = re.compile(
                r"\b(?:" + "|".join(re.escape(w) for w in words) + r")", re.IGNORECASE
            )
            self._cache_key = words
        return self._pattern

    def stop(self):
        self._stop_evt.set()

    def run(self):
        while not self._stop_evt.wait(0.5):
            if not self.settings.title_monitor:
                continue
            title, _ = foreground_info()
            if title:
                m = self._get_pattern().search(title)
                if m:
                    self.on_detect("title", f"matched '{m.group(0)}' in \"{title[:60]}\"")
