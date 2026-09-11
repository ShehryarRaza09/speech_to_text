from core.translator import Translator
t = Translator()

tests = [
    ("안녕하세요. 제 이름은 철수입니다.", "ko"),
    ("你好，我吃饭了。", "zh"),
    ("नमस्ते, आप कैसे हैं?", "hi"),
    ("مرحبا كيف حالك؟", "ar"),
    ("Hello, how are you?", "en"),
]

for text, src in tests:
    print(f"\n[{src}] {text}")
    print(f"  -> en: {t.translate(text, target='en', source=src)}")
    print(f"  -> ur: {t.translate(text, target='ur', source=src)}")
