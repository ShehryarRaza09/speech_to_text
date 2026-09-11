from core.recorder import AudioRecorder
import time

r = AudioRecorder()
print("=" * 60)
print("TEST: Recording for 5 seconds. Speak now!")
print("=" * 60)
r.start()
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)
path = r.stop()
print(f"\nSaved: {path}")

if path:
    from core.transcriber import Transcriber
    t = Transcriber("distil-large-v3")
    text, lang = t.transcribe(path)
    print(f"\nDetected language: {lang}")
    print(f"Transcribed: '{text}'")
