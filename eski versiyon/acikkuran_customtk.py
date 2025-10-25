import customtkinter as ctk
import pandas as pd
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Mekki/Medeni bilgisini sure numarasına göre ekle
sure_tipi = {
    1: "Mekki", 2: "Medeni", 3: "Medeni", 4: "Medeni", 5: "Medeni", 6: "Mekki",
    7: "Mekki", 8: "Medeni", 9: "Medeni", 10: "Mekki", 11: "Mekki", 12: "Mekki",
    13: "Mekki", 14: "Mekki", 15: "Mekki", 16: "Mekki", 17: "Mekki", 18: "Mekki",
    19: "Mekki", 20: "Mekki", 21: "Medeni", 22: "Medeni", 23: "Medeni", 24: "Medeni",
    25: "Medeni", 26: "Medeni", 27: "Medeni", 28: "Medeni", 29: "Medeni", 30: "Mekki",
    31: "Medeni", 32: "Medeni", 33: "Medeni", 34: "Medeni", 35: "Mekki", 36: "Mekki",
    37: "Mekki", 38: "Mekki", 39: "Mekki", 40: "Medeni", 41: "Mekki", 42: "Mekki",
    43: "Mekki", 44: "Mekki", 45: "Mekki", 46: "Mekki", 47: "Medeni", 48: "Medeni",
    49: "Medeni", 50: "Medeni", 51: "Mekki", 52: "Mekki", 53: "Medeni", 54: "Medeni",
    55: "Mekki", 56: "Mekki", 57: "Medeni", 58: "Medeni", 59: "Medeni", 60: "Medeni",
    61: "Mekki", 62: "Medeni", 63: "Medeni", 64: "Medeni", 65: "Medeni", 66: "Mekki",
    67: "Mekki", 68: "Mekki", 69: "Mekki", 70: "Mekki", 71: "Mekki", 72: "Mekki",
    73: "Mekki", 74: "Mekki", 75: "Mekki", 76: "Medeni", 77: "Medeni", 78: "Mekki",
    79: "Mekki", 80: "Mekki", 81: "Mekki", 82: "Mekki", 83: "Mekki", 84: "Mekki",
    85: "Mekki", 86: "Mekki", 87: "Mekki", 88: "Mekki", 89: "Mekki", 90: "Mekki",
    91: "Mekki", 92: "Mekki", 93: "Mekki", 94: "Mekki", 95: "Mekki", 96: "Mekki",
    97: "Mekki", 98: "Medeni", 99: "Mekki", 100: "Mekki", 101: "Mekki", 102: "Mekki",
    103: "Mekki", 104: "Medeni", 105: "Mekki", 106: "Mekki", 107: "Mekki", 108: "Mekki",
    109: "Mekki", 110: "Medeni", 111: "Mekki", 112: "Mekki", 113: "Mekki", 114: "Mekki"
}

class KuranApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AçıkKuran Araştırmacısı v1")
        self.geometry("1200x700")
        self.resizable(False, False)

        # Sol menü
        self.side_bar = ctk.CTkFrame(self, width=220, corner_radius=10)
        self.side_bar.pack(side="left", fill="y", padx=10, pady=10)
        self.logo = ctk.CTkLabel(self.side_bar, text="AçıkKuran\nAraştırmacısı", font=("Arial", 19, "bold"))
        self.logo.pack(pady=16)
        self.btn_ara = ctk.CTkButton(self.side_bar, text="Kelime Ara", command=self.kelime_ara_ui)
        self.btn_ara.pack(fill="x", pady=5)
        self.btn_ayet = ctk.CTkButton(self.side_bar, text="Sırayla Ayet Bul", command=self.ayet_ara_ui)
        self.btn_ayet.pack(fill="x", pady=5)
        self.btn_istatistik = ctk.CTkButton(self.side_bar, text="İstatistik", command=self.istatistik_ui)
        self.btn_istatistik.pack(fill="x", pady=5)

        # Ana panel
        self.main_panel = ctk.CTkFrame(self, fg_color="#f5f7fa", corner_radius=12)
        self.main_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.arama_entry = ctk.CTkEntry(self.main_panel, placeholder_text="Kelime veya ayet ara…", width=500)
        self.arama_entry.pack(pady=14)
        self.arama_entry.bind("<Return>", lambda e: self.kelime_ara())
        self.arama_btn = ctk.CTkButton(self.main_panel, text="ARA", command=self.kelime_ara)
        self.arama_btn.pack()

        # Sonuç paneli (tablo gibi)
        self.result_table = ctk.CTkTextbox(self.main_panel, width=900, height=420, font=("Consolas", 12), wrap="none")
        self.result_table.pack(pady=20)

        # Başlangıçta Mehmet_Okuyan.csv otomatik yükle
        self.data_file = "Mehmet_Okuyan.csv"
        if not os.path.exists(self.data_file):
            self.result_table.insert("end", "Mehmet_Okuyan.csv bulunamadı, lütfen dosyayı aynı klasöre ekle.")
            self.df = None
        else:
            self.df = pd.read_csv(self.data_file, encoding="utf-8", on_bad_lines="skip")
            self.df["mekki_medeni"] = self.df["sure"].apply(lambda x: sure_tipi.get(int(x), "?"))
            self.show_table(self.df.head(10))

    def kelime_ara_ui(self):
        self.arama_entry.delete(0, "end")
        self.arama_entry.focus()

    def ayet_ara_ui(self):
        self.result_table.delete("0.0", "end")
        self.result_table.insert("end", "Burada sırayla ayet bulma fonksiyonu gelecek.\n")

    def istatistik_ui(self):
        self.result_table.delete("0.0", "end")
        if self.df is not None:
            toplam = len(self.df)
            hoca_sayisi = self.df["hoca"].nunique() if "hoca" in self.df else "?"
            self.result_table.insert("end", f"Toplam ayet: {toplam}\nHoca sayısı: {hoca_sayisi}\n")
        else:
            self.result_table.insert("end", "Veri dosyası yüklenemedi.")

    def kelime_ara(self):
        if self.df is None:
            self.result_table.delete("0.0", "end")
            self.result_table.insert("end", "Mehmet_Okuyan.csv yüklenemedi!")
            return
        aranan = self.arama_entry.get().strip().lower()
        self.result_table.delete("0.0", "end")
        if not aranan:
            self.result_table.insert("end", "Lütfen bir kelime girin!\n")
            return
        # Sonuçları bul
        sonuclar = self.df[self.df["metin"].str.lower().str.contains(aranan, na=False)]
        if sonuclar.empty:
            self.result_table.insert("end", "Sonuç bulunamadı.")
        else:
            self.show_table(sonuclar.head(30), vurgula=aranan)

    def show_table(self, df, vurgula=None):
        self.result_table.delete("0.0", "end")
        # Kolon isimleri
        header = "{:<5}{:<6}{:<6}{:<10}{:<10}{}\n".format("Sıra", "Sure", "Ayet", "Hoca", "Tip", "Metin")
        self.result_table.insert("end", header + "-"*95 + "\n")
        for _, row in df.iterrows():
            # Metin içinde aranan kelimeyi vurgula
            metin = str(row["metin"])
            if vurgula and vurgula.lower() in metin.lower():
                # Büyük/küçük harf duyarsız vurgulama
                kelime = vurgula
                start = 0
                metin_vurgulu = ""
                text_lower = metin.lower()
                while True:
                    idx = text_lower.find(kelime.lower(), start)
                    if idx == -1:
                        metin_vurgulu += metin[start:]
                        break
                    metin_vurgulu += metin[start:idx] + "⟦" + metin[idx:idx+len(kelime)] + "⟧"
                    start = idx + len(kelime)
                metin = metin_vurgulu
            line = "{:<5}{:<6}{:<6}{:<10}{:<10}{}\n".format(
                row["sira"], row["sure"], row["ayet"], row["hoca"][:9], row["mekki_medeni"], metin
            )
            self.result_table.insert("end", line)

if __name__ == "__main__":
    app = KuranApp()
    app.mainloop()
