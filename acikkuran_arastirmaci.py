import pandas as pd
import os
from collections import Counter
import re

# 1- Dosya Yükleme (Başlangıçta sadece CSV, istersek kolayca genişler)
def dosya_sec():
    print("\nKlasördeki mealler dosya listesini gösteriyorum:\n")
    dosya_listesi = [f for f in os.listdir('tum_mealler') if f.endswith('.csv')]
    for i, dosya in enumerate(dosya_listesi):
        print(f"{i+1}: {dosya}")
    secim = input("\nAçmak istediğin dosya no (örn: 1): ")
    secili = dosya_listesi[int(secim)-1]
    print(f"\n[+] {secili} yüklendi.\n")
    return pd.read_csv(os.path.join('tum_mealler', secili)), secili

# 2- Anahtar Kelime / Kök Arama (Hem metin hem Arapça kök için)
def anahtar_kelime_arama(df):
    aranan = input("Aranacak kelime/kök: ").strip()
    print(f"\nSonuçlar:\n")
    for idx, row in df.iterrows():
        if aranan in str(row['metin']) or aranan in str(row.get('kök', '')):
            print(f"{row['sıra']} | {row['sure']}:{row['ayet']} | {row['hoca']}\n{row['metin']}\n")
    print("-"*60)

# 3- Sure/Ayet numarasıyla ayet bul
def sure_ayet_bul(df):
    kod = input("Şu formatta yaz (örn: 2/255): ").replace('.', '/')
    try:
        sure, ayet = kod.split('/')
        sonuc = df[(df['sure'].astype(str)==sure.strip()) & (df['ayet'].astype(str)==ayet.strip())]
        for idx, row in sonuc.iterrows():
            print(f"{row['sıra']} | {row['sure']}:{row['ayet']} | {row['hoca']}\n{row['metin']}\n")
    except:
        print("Format hatası! 2/255 şeklinde olmalı.")

# 4- Genel sıra numarasıyla ayet bul
def sira_no_bul(df):
    sira = input("Ayet sıra no (örn: 2524): ").strip()
    sonuc = df[df['sıra'].astype(str)==sira]
    if not sonuc.empty:
        for idx, row in sonuc.iterrows():
            print(f"{row['sıra']} | {row['sure']}:{row['ayet']} | {row['hoca']}\n{row['metin']}\n")
    else:
        print("Bulunamadı.")

# 5- Tematik/Semantik arama (çoklu anahtar kelime ile)
def tematik_arama(df):
    kelimeler = input("Birden fazla kelime/kök (virgüllü): ")
    kelime_liste = [k.strip() for k in kelimeler.split(',')]
    for idx, row in df.iterrows():
        if any(k in str(row['metin']) for k in kelime_liste):
            print(f"{row['sıra']} | {row['sure']}:{row['ayet']} | {row['hoca']} | {row['metin']}")

# 6- Kelime frekansı ve istatistik
def kelime_frekans_istatistik(df):
    tum_metin = " ".join(str(m) for m in df['metin'])
    kelimeler = re.findall(r'\w+', tum_metin.lower())
    frekans = Counter(kelimeler)
    print("\nEn sık geçen 20 kelime:")
    for kelime, adet in frekans.most_common(20):
        print(f"{kelime}: {adet}")
    print("-"*40)

# 7- Çapraz kavram karşılaştırması (örn: gece-gündüz, gün-ay)
def capraz_kavram(df):
    kavram1 = input("1. kelime/kök: ").strip()
    kavram2 = input("2. kelime/kök: ").strip()
    print(f"\n-- Sadece {kavram1} geçen ayetler --")
    for idx, row in df.iterrows():
        m = str(row['metin'])
        if kavram1 in m and kavram2 not in m:
            print(f"{row['sure']}:{row['ayet']} | {m}")
    print(f"\n-- Sadece {kavram2} geçen ayetler --")
    for idx, row in df.iterrows():
        m = str(row['metin'])
        if kavram2 in m and kavram1 not in m:
            print(f"{row['sure']}:{row['ayet']} | {m}")
    print(f"\n-- Her ikisi de geçen ayetler --")
    for idx, row in df.iterrows():
        m = str(row['metin'])
        if kavram1 in m and kavram2 in m:
            print(f"{row['sure']}:{row['ayet']} | {m}")
    print("-"*40)

# 8- Bilimsel/sayısal bağlantı analizi (ör: demir ve 26. sure gibi)
def bilimsel_baglanti(df):
    kelime = input("Bilimsel kavram (örn: demir): ").strip()
    print("\nBu kelimenin geçtiği sure/ayetler ve sıra numaraları:")
    for idx, row in df.iterrows():
        if kelime in str(row['metin']):
            print(f"Sıra: {row['sıra']} | {row['sure']}:{row['ayet']} | {row['metin']}")
    # (Buraya özel sayısal analizler/bağlantılar eklenebilir)

# 9- Arapça kök analizi (CAMeL Tools için hazırlık, dışa aktarım)
def arapca_kok_analiz(df):
    try:
        from camel_tools.morphology.analyzer import Analyzer
        analyzer = Analyzer.builtin_analyzer()
        for idx, row in df.iterrows():
            arapca = str(row.get('arapca', ''))
            if arapca:
                analiz = analyzer.analyze(arapca)
                print(f"{row['sure']}:{row['ayet']} | {arapca} | {analiz[:1]}")
    except Exception as e:
        print("CAMeL Tools kurulu değil veya Arapça metin yok.")

# 10- Sonuçları dışa aktar (CSV/TXT)
def disari_aktar(df):
    dosya = input("Kaydedilecek dosya adı (örn: cikti.csv): ")
    if dosya.endswith('.csv'):
        df.to_csv(dosya, index=False)
    else:
        with open(dosya, 'w', encoding='utf-8') as f:
            for idx, row in df.iterrows():
                f.write(f"{row['sıra']}, {row['sure']}, {row['ayet']}, {row['hoca']}, {row['metin']}\n")
    print(f"{dosya} olarak kaydedildi.")

# 11- Kullanıcı not/etiket (basit örnek)
def not_ekle(df):
    ayet_no = input("Not eklenecek sıra no: ")
    notunuz = input("Notunuz: ")
    df.loc[df['sıra'].astype(str)==ayet_no, 'not'] = notunuz
    print("Not kaydedildi.")

# Ana Menü
def main():
    df, dosya_adi = dosya_sec()
    if 'not' not in df.columns:
        df['not'] = ''
    while True:
        print(f"""
=== AçıkKuran Araştırmacısı === [{dosya_adi}]
1- Anahtar kelime/kök arama
2- Sure/ayet numarasıyla ayet bul
3- Genel sıra numarasıyla ayet bul
4- Tematik/semantik arama
5- Kelime frekansı & istatistik
6- Çapraz kavram analizi
7- Bilimsel/sayısal bağlantı analizi
8- Arapça kök analizi (CAMeL Tools)
9- Ayete not/etiket ekle
10- Sonuçları dışa aktar
0- Çıkış
""")
        secim = input("Seçim: ")
        if secim == "1":
            anahtar_kelime_arama(df)
        elif secim == "2":
            sure_ayet_bul(df)
        elif secim == "3":
            sira_no_bul(df)
        elif secim == "4":
            tematik_arama(df)
        elif secim == "5":
            kelime_frekans_istatistik(df)
        elif secim == "6":
            capraz_kavram(df)
        elif secim == "7":
            bilimsel_baglanti(df)
        elif secim == "8":
            arapca_kok_analiz(df)
        elif secim == "9":
            not_ekle(df)
        elif secim == "10":
            disari_aktar(df)
        elif secim == "0":
            print("Çıkılıyor...")
            break
        else:
            print("Hatalı seçim!")

if __name__ == "__main__":
    main()
