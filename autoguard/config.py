"""Settings, constants and built-in detection patterns."""
import json
import os
from dataclasses import asdict, dataclass, field

APP_NAME = "AutoGuard"
DATA_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_PATH = os.path.join(DATA_DIR, "settings.json")
LOG_PATH = os.path.join(DATA_DIR, "guard.log")

BROWSER_PROCESSES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe",
    "opera.exe", "vivaldi.exe", "iexplore.exe", "arc.exe",
}

# NudeNet v3 labels that count as explicit content.
EXPLICIT_CLASSES = {
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "BUTTOCKS_EXPOSED",
    "ANUS_EXPOSED",
}

# Built-in title patterns (matched at word start, case-insensitive).
# You can add more in settings.json -> "extra_keywords".
TITLE_KEYWORDS = [
    "porn", "xxx", "nsfw", "hentai", "xvideos", "xnxx", "xhamster",
    "redtube", "youporn", "onlyfans", "brazzers", "spankbang",
    "chaturbate", "stripchat", "livejasmin", "bangbros", "rule34",
    "sex video", "sex cam", "nude", "erotic", "camgirl",
]


@dataclass
class Settings:
    threshold: float = 0.60        # higher = fewer detections (less sensitive)
    scan_interval: float = 1.0     # seconds between screen scans
    consecutive_hits: int = 2      # frames in a row required (cuts false positives)
    cooldown: float = 3.0          # seconds between block actions
    kill_browser: bool = False     # True = kill browser process instead of Ctrl+W
    title_monitor: bool = True
    visual_monitor: bool = True
    extra_keywords: list = field(default_factory=list)

    @classmethod
    def load(cls) -> "Settings":
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()

    def save(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception:
            pass
