"""Speech-to-Text UI with friendly error messages."""
import customtkinter as ctk
import threading
from core.recorder import AudioRecorder
from core.transcriber import Transcriber
from core.translator import Translator
from ui.styles import COLORS, FONTS


class SpeechApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Speech to Text - English / Urdu")
        self.geometry("900x650")
        self.configure(fg_color=COLORS["bg"])

        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(model_size="large-v3")
        self.translator = Translator()
        self.target_lang = ctk.StringVar(value="ur")

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Speech to Text - English / Urdu",
                     font=FONTS["title"], text_color=COLORS["text"]).pack(pady=(20, 10))

        self.record_btn = ctk.CTkButton(
            self, text="Start Recording",
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=50, width=220, command=self.toggle_recording,
        )
        self.record_btn.pack(pady=10)

        lf = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=12)
        lf.pack(pady=15, padx=30, fill="x")
        ctk.CTkLabel(lf, text="Output Language:", font=FONTS["body"],
                     text_color=COLORS["text"]).pack(side="left", padx=20, pady=15)
        ctk.CTkRadioButton(lf, text="English", variable=self.target_lang, value="en",
                           font=FONTS["body"], text_color=COLORS["text"],
                           fg_color=COLORS["accent"]).pack(side="left", padx=10)
        ctk.CTkRadioButton(lf, text="Urdu", variable=self.target_lang, value="ur",
                           font=FONTS["body"], text_color=COLORS["text"],
                           fg_color=COLORS["accent"]).pack(side="left", padx=10)

        self.status = ctk.CTkLabel(self, text="Ready", font=FONTS["body"],
                                   text_color=COLORS["muted"])
        self.status.pack(pady=5)

        self.output_box = ctk.CTkTextbox(self, font=FONTS["urdu"],
                                         fg_color=COLORS["card"],
                                         text_color=COLORS["text"],
                                         wrap="word", corner_radius=12)
        self.output_box.pack(padx=30, pady=15, fill="both", expand=True)

        ctk.CTkButton(self, text="Clear",
                      fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                      font=FONTS["body"], width=120, height=38,
                      command=lambda: self.output_box.delete("1.0", "end")).pack(pady=(0, 20))

    def toggle_recording(self):
        if not self.recorder.is_recording():
            try:
                self.recorder.start()
                self.record_btn.configure(text="Stop Recording",
                                          fg_color=COLORS["danger"],
                                          hover_color=COLORS["danger_hover"])
                self.status.configure(text="Recording... Speak now!",
                                      text_color=COLORS["danger"])
            except Exception as e:
                self.status.configure(text=f"Mic error: {e}",
                                      text_color=COLORS["danger"])
        else:
            self.record_btn.configure(text="Start Recording",
                                      fg_color=COLORS["accent"],
                                      hover_color=COLORS["accent_hover"])
            self.status.configure(text="Processing...", text_color=COLORS["muted"])
            self.update()
            threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            path = self.recorder.stop()
            if not path:
                self._set_status("No valid audio captured. Hold record longer and speak clearly.",
                                 COLORS["danger"])
                return

            text, detected = self.transcriber.transcribe(path)
            if not text.strip():
                self._set_status("Whisper could not hear anything. Try again closer to mic.",
                                 COLORS["danger"])
                return

            target = self.target_lang.get()
            translated = self.translator.translate(text, target=target, source=detected)

            self.after(0, self._append_output, text, translated, detected, target)

        except Exception as e:
            self._set_status(f"Error: {e}", COLORS["danger"])

    def _append_output(self, original, translated, detected, target):
        label = "English" if target == "en" else "Urdu"
        block = (
            f"\n{'-' * 60}\n"
            f"Original ({detected}): {original}\n"
            f"{label}: {translated}\n"
        )
        self.output_box.insert("end", block)
        self.output_box.see("end")
        self._set_status("Done - ready for next recording.", COLORS["success"])

    def _set_status(self, msg, color):
        self.after(0, lambda: self.status.configure(text=msg, text_color=color))
