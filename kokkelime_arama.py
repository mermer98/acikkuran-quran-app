import pandas as pd

# CSV'de başlık yoksa:
df = pd.read_csv('kokkelime.csv', names=['kelime', 'frekans'], encoding='utf-8')

def kok_frekans_arama():
    print("Arapça kök/kelime girin (ör: حمد) veya ENTER ile en çok geçenleri gör:")
    kok = input("Kelime: ").strip()
    if kok:
        satir = df[df['kelime'] == kok]
        if satir.empty:
            print(f"'{kok}' bulunamadı.")
        else:
            tekrar = int(satir['frekans'].values[0])
            print(f"'{kok}' Kur’an’da {tekrar} kez geçiyor.")
    else:
        print("En çok geçen ilk 10 kök/kelime:")
        print(df.sort_values('frekans', ascending=False).head(10).to_string(index=False))

if __name__ == "__main__":
    kok_frekans_arama()
