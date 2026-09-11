from core.translator import Translator
t = Translator()
print(t.translate("안녕하세요. 제 이름은 철수입니다.", target="en", source="ko"))
print(t.translate("안녕하세요. 제 이름은 철수입니다.", target="ur", source="ko"))
