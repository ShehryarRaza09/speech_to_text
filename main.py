"""
Real-Time Speech → Text → Urdu/English Translation
Entry point.
"""
import os
import sys

# Auto-install missing packages
REQUIRED = ["faster_whisper", "sounddevice", "numpy", "soundfile", "deep_translator", "customtkinter"]

def _bootstrap():
    import subprocess
    missing = []
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"📦 Installing missing: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

_bootstrap()

from ui.app import SpeechApp


def main():
    os.makedirs("output", exist_ok=True)
    app = SpeechApp()
    app.mainloop()


if __name__ == "__main__":
    main()