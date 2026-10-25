from farasa.segmenter import FarasaSegmenter
segmenter = FarasaSegmenter(interactive=True)
text = "فالكتاب على المكتبة"
print(segmenter.segment(text))  # Çıktı: "ف+ال+كتاب على ال+مكتبة"