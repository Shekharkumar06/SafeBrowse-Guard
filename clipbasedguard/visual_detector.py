"""Background screen capture (mss) + CLIP zero-shot detection."""
import threading
import time

from .config import CLIP_MODEL_ID, CLIP_PROMPTS


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
            import mss
            import torch
            from PIL import Image
            from transformers import CLIPModel, CLIPProcessor

            self.on_status("Loading CLIP model (first run downloads it)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(device).eval()
            processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
            self.on_status(f"Visual scanner ready ({device})")
        except Exception as exc:
            self.on_status(f"Visual scanner failed to start: {exc}")
            return

        def bikini_prob(img: "Image.Image") -> float:
            # Squash the whole screen to 224x224 so nothing is cropped away.
            img = img.resize((224, 224), Image.BICUBIC)
            inputs = processor(text=CLIP_PROMPTS, images=img,
                               return_tensors="pt", padding=True).to(device)
            with torch.inference_mode():
                probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
            return float(probs[0])  # index 0 = bikini / lingerie prompt

        hits = 0
        with mss.mss() as sct:
            while not self._stop_evt.is_set():
                started = time.time()
                if self.settings.visual_monitor:
                    try:
                        best = 0.0
                        for mon in sct.monitors[1:]:  # every physical monitor
                            shot = sct.grab(mon)
                            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                            best = max(best, bikini_prob(img))
                        hits = hits + 1 if best >= self.settings.threshold else 0
                        if hits >= self.settings.consecutive_hits:
                            hits = 0
                            self.on_detect("visual", f"CLIP bikini/lingerie p={best:.2f}")
                    except Exception as exc:
                        self.on_status(f"Scan error: {exc}")
                elapsed = time.time() - started
                self._stop_evt.wait(max(0.05, self.settings.scan_interval - elapsed))
