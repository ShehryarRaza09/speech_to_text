"""Speech-to-Text entry point."""
import os
import sys

# MUST be first — sets offline mode + performance env vars
import bootstrap_offline  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import SpeechApp


def main():
    os.makedirs("output", exist_ok=True)
    app = SpeechApp()
    app.mainloop()


if __name__ == "__main__":
    main()
