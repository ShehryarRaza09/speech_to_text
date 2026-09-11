"""Distilled large-v3 - best CPU compromise."""
from faster_whisper import WhisperModel


CUSTOM_VOCAB = (
    "Sherry, Shahryar, Shehryar, Pakistan, Karachi, Lahore, Islamabad"
)


class Transcriber:
    def __init__(self, model_size="distil-large-v3", initial_prompt=None):
        print(f"[Transcriber] Loading Whisper '{model_size}' ...")
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            cpu_threads=8,
            num_workers=2,
        )
        self.initial_prompt = initial_prompt or CUSTOM_VOCAB
        print("[Transcriber] Ready.")

    def transcribe(self, audio_path, language=None):
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=1,
            best_of=1,
            temperature=0.0,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
            condition_on_previous_text=False,
            word_timestamps=False,
            initial_prompt=self.initial_prompt,
        )
        text = " ".join(s.text.strip() for s in segments).strip()
        return text, info.language
