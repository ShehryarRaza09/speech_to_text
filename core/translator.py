"""
Offline translator using Meta's NLLB-200 (200 languages, direct translation).
- No API keys, no billing, no network after first model download.
- Supports Korean, Chinese, Hindi, Arabic, Urdu, English, + 190 more.
"""
import re
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "facebook/nllb-200-distilled-1.3B"   # ~600MB, good balance

# Whisper ISO codes -> NLLB BCP-47 codes
NLLB_LANG = {
    "en": "eng_Latn",
    "ur": "urd_Arab",
    "hi": "hin_Deva",
    "ko": "kor_Hang",
    "zh": "zho_Hans",
    "ja": "jpn_Jpan",
    "ar": "arb_Arab",
    "fa": "pes_Arab",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "ru": "rus_Cyrl",
    "tr": "tur_Latn",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "bn": "ben_Beng",
    "pa": "pan_Guru",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "ur_roman": "urd_Latn",
    "id": "ind_Latn",
    "vi": "vie_Latn",
    "th": "tha_Thai",
    "he": "heb_Hebr",
    "pl": "pol_Latn",
    "nl": "nld_Latn",
    "uk": "ukr_Cyrl",
    "sw": "swh_Latn",
    "ms": "zsm_Latn",
    "tl": "tgl_Latn",
}


class Translator:
    def __init__(self):
        self.cache = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Translator] Loading NLLB on {self.device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()
        print("[Translator] Ready.")

    def _clean(self, text):
        if not text:
            return ""
        text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _code(self, iso):
        return NLLB_LANG.get(iso, "eng_Latn")

    def _translate_chunk(self, text, src_code, tgt_code):
        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_code),
                max_length=512,
                num_beams=4,
            )
        return self.tokenizer.batch_decode(out, skip_special_tokens=True)[0]

    def _chunk(self, text, size=400):
        if len(text) <= size:
            return [text]
        parts = re.split(r"(?<=[.!?\u3002\u06d4\n])\s+", text)
        chunks, buf = [], ""
        for p in parts:
            if len(buf) + len(p) + 1 <= size:
                buf = (buf + " " + p).strip()
            else:
                if buf:
                    chunks.append(buf)
                buf = p
        if buf:
            chunks.append(buf)
        return chunks

    def translate(self, text, target="ur", source=None):
        text = self._clean(text)
        if not text:
            return ""

        source = source or "en"
        if source == target:
            return text

        key = (text, source, target)
        if key in self.cache:
            return self.cache[key]

        src_code = self._code(source)
        tgt_code = self._code(target)

        try:
            parts = self._chunk(text)
            results = [self._translate_chunk(p, src_code, tgt_code) for p in parts]
            out = " ".join(results).strip()
            self.cache[key] = out
            return out
        except Exception as e:
            return f"{text}  [translation error: {e}]"
