from kivyx.core.text.fontfinder import find_fonts_from_text

sample_texts = {
    'zh-Hant': '經傳說',
    'zh-Hans': '经传说',
    'ko': '안녕',
    'ja': '経伝説',
}

for lang, text in sample_texts.items():
    print(f"\n---- list of fonts that support '{lang}' ----")
    for font in find_fonts_from_text(text):
        print(font.name)
