"""Bulletproof recorder - never rejects audio, always saves, auto-amplifies."""
import sounddevice as sd
import numpy as np
import soundfile as sf
import os


class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1, device=None):
        self.samplerate = samplerate
        self.channels = channels
        self.device = device
        self.recording = False
        self.frames = []
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if self.recording:
            self.frames.append(indata.copy())

    def start(self):
        self.frames = []
        self.recording = True
        try:
            self._stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                callback=self._callback,
                dtype="float32",
                device=self.device,
            )
            self._stream.start()
            print("[Recorder] Recording started. Speak now.")
        except Exception as e:
            self.recording = False
            print(f"[Recorder] Failed to start mic: {e}")
            raise

    def stop(self, save_path="output/recording.wav"):
        self.recording = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        # If nothing captured, create a tiny silent fallback so app doesn't crash
        if not self.frames:
            print("[Recorder] No frames captured - creating empty fallback.")
            audio = np.zeros(int(1.0 * self.samplerate), dtype="float32")
        else:
            try:
                audio = np.concatenate(self.frames, axis=0)
            except Exception as e:
                print(f"[Recorder] Merge failed: {e}")
                audio = np.zeros(int(1.0 * self.samplerate), dtype="float32")

        duration = len(audio) / self.samplerate
        peak_before = float(np.max(np.abs(audio))) if audio.size else 0.0
        print(f"[Recorder] Captured {duration:.2f}s, peak={peak_before:.6f}")

        # ── NORMALIZE: auto-amplify to healthy level ──
        if peak_before > 0.0001:
            target_peak = 0.85
            gain = target_peak / peak_before
            gain = min(gain, 500.0)   # cap gain
            audio = audio * gain
            peak_after = float(np.max(np.abs(audio))) if audio.size else 0.0
            print(f"[Recorder] Amplified x{gain:.1f} -> new peak={peak_after:.4f}")
        else:
            print("[Recorder] Signal is essentially silent - passing to Whisper anyway.")

        # ── ALWAYS SAVE ──
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            sf.write(save_path, audio, self.samplerate)
            print(f"[Recorder] Saved -> {save_path}")
            return save_path
        except Exception as e:
            print(f"[Recorder] Save failed: {e}")
            return None

    def is_recording(self):
        return self.recording
