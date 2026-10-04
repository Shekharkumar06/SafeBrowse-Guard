"""Background screen capture (mss) + NudeNet NSFW detection."""
import threading
import time

from .config import EXPLICIT_CLASSES


class VisualScanner(threading.Thread):
    def __init__(self, settings, on_detect, on_status):
        super().__init__(daemon=True, name="VisualScanner")
        self.settings = settings
        self.on_detect = on_detect
        self.on_status = on_status
        self._stop_evt = threading.Event()

    def stop(self):
        self._stop_evt.set()

    def run(self):
        try:
            import cv2
            import mss
            import numpy as np
            from nudenet import NudeDetector

            self.on_status("Loading NudeNet model...")
            detector = NudeDetector()
            self.on_status("Visual scanner ready")
        except Exception as exc:  # missing deps / model failure
            self.on_status(f"Visual scanner failed to start: {exc}")
            return

        hits = 0
        with mss.mss() as sct:
            while not self._stop_evt.is_set():
                started = time.time()
                if self.settings.visual_monitor:
                    try:
                        best, label = 0.0, ""
                        for mon in sct.monitors[1:]:  # every physical monitor
                            frame = cv2.cvtColor(np.array(sct.grab(mon)), cv2.COLOR_BGRA2BGR)
                            for d in detector.detect(frame):
                                if d["class"] in EXPLICIT_CLASSES and d["score"] > best:
                                    best, label = d["score"], d["class"]
                        if best >= self.settings.threshold:
                            hits += 1
                        else:
                            hits = 0
                        if hits >= self.settings.consecutive_hits:
                            hits = 0
                            self.on_detect("visual", f"{label} ({best:.2f})")
                    except Exception as exc:
                        self.on_status(f"Scan error: {exc}")
                elapsed = time.time() - started
                self._stop_evt.wait(max(0.05, self.settings.scan_interval - elapsed))
