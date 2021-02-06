from kivyx.utils import fontfinder
from kivy.core.window import Window

sample_texts = {
    'zh-Hant': '經傳說',
    'zh-Hans': '经传说',
    'ko': '안녕',
    'ja': 'あ伝説',
}

for lang, text in sample_texts.items():
    print(f"\n---- list of fonts that support '{lang}' ----")
    for font in fontfinder.find_fonts_from_text(text):
        print(font.name)
