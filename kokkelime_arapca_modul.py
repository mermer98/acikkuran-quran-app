import pandas as pd
import customtkinter as ctk

# === KÖK ve KELİME VERİSİ YÜKLEME ===
kok_df = pd.read_csv("kokkelime.csv", header=None, names=["kelime", "frekans"])
kok_df = kok_df.dropna()

# === ARAPÇA HARFLERİ ===
ARAP_HARFLER = [
    'ا','ب','ت','ث','ج','ح','خ','د','ذ','ر','ز','س','ش','ص',
    'ض','ط','ظ','ع','غ','ف','ق','ك','ل','م','ن','ه','و','ي','ء','ى'
]

def harf_ekle(harf):
    arama_entry.insert(ctk.END, harf)

def arama_fonksiyonu(event=None):
    aranan = arama_entry.get().strip()
    if not aranan:
        # En çok geçen 10 kökü göster
        top = kok_df.sort_values("frekans", ascending=False).head(10)
        sonuc = "\n".join([f"{row.kelime} : {row.frekans}" for row in top.itertuples()])
        sonuc_textbox.delete(0.0, ctk.END)
        sonuc_textbox.insert(ctk.END, "En çok geçen kök/kelime:\n" + sonuc)
        return
    # Doğrudan eşleşen kelimeler
    matched = kok_df[kok_df["kelime"].astype(str).str.contains(aranan)]
    if matched.empty:
        sonuc = "Sonuç bulunamadı."
    else:
        sonuc = "\n".join([f"{row.kelime} : {row.frekans}" for row in matched.itertuples()])
    sonuc_textbox.delete(0.0, ctk.END)
    sonuc_textbox.insert(ctk.END, sonuc)

# === ARAYÜZ ===
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("AçıkKuran Arapça Kök/Kelime Ara + Sanal Klavye")
root.geometry("640x500")

# Arama kutusu
arama_entry = ctk.CTkEntry(root, font=("Arial", 18), width=400)
arama_entry.place(x=20, y=30)
arama_entry.bind("<Return>", arama_fonksiyonu)

# Ara butonu
ara_buton = ctk.CTkButton(root, text="ARA", command=arama_fonksiyonu, width=120)
ara_buton.place(x=440, y=30)

# Sanal Klavye
klavye_frame = ctk.CTkFrame(root, width=600, height=70)
klavye_frame.place(x=20, y=80)
row, col = 0, 0
for harf in ARAP_HARFLER:
    btn = ctk.CTkButton(klavye_frame, text=harf, width=38, height=38, command=lambda h=harf: harf_ekle(h))
    btn.grid(row=row, column=col, padx=2, pady=2)
    col += 1
    if col > 14:
        col = 0
        row += 1

# Sonuç kutusu
sonuc_textbox = ctk.CTkTextbox(root, font=("Arial", 15), width=600, height=340, wrap="word")
sonuc_textbox.place(x=20, y=160)

root.mainloop()
