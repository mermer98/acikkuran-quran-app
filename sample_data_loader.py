import pandas as pd

# Örnek Türkçe meal dosyası
meal_data = [
    {'sira': 1, 'sure': 1, 'ayet': 1, 'metin': "Rahmân, Rahîm olan Allah'ın adıyla.", 'hoca': 'Mehmet Okuyan'},
    {'sira': 2, 'sure': 1, 'ayet': 2, 'metin': "Hamd, âlemlerin Rabbi Allah'a mahsustur.", 'hoca': 'Mehmet Okuyan'},
    {'sira': 3, 'sure': 3, 'ayet': 7, 'metin': "Sana Kitabı indiren O'dur. Onun bazı ayetleri muhkemdir...", 'hoca': 'Mehmet Okuyan'}
]

# Örnek Arapça ayetler dosyası
arapca_data = [
    {'sira': 1, 'sure': 1, 'ayet': 1, 'metin': "بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّح۪يمِ"},
    {'sira': 2, 'sure': 1, 'ayet': 2, 'metin': "اَلْحَمْدُ لِلّٰهِ رَبِّ الْعَالَم۪ينَۙ"},
    {'sira': 3, 'sure': 3, 'ayet': 7, 'metin': "هُوَ الَّـذ۪ٓي اَنْزَلَ عَلَيْكَ الْكِتَابَ ..."}
]

pd.DataFrame(meal_data).to_csv('Mehmet_Okuyan_arapca.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(arapca_data).to_csv('arapca_ayetler.csv', index=False, encoding='utf-8-sig')
print('Örnek veri dosyaları oluşturuldu.')
