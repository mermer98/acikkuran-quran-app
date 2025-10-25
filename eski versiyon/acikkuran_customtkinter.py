import customtkinter as ctk
import pandas as pd

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- Mekki/Medeni: KuranMeali.com'dan alınan tabloya göre ---
mekki_medeni_list = [
    ("1", "Mekki"), ("2", "Medeni"), ("3", "Medeni"), ("4", "Medeni"), ("5", "Medeni"), ("6", "Mekki"),
    ("7", "Mekki"), ("8", "Medeni"), ("9", "Medeni"), ("10", "Mekki"), ("11", "Mekki"), ("12", "Mekki"),
    # ... devamı tam tabloya göre eklenecek ...
    ("114", "Mekki")
]
sure_tip = {int(num): tip for num, tip in mekki_medeni_list}

class AcikKuranApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AçıkKuran Masaüstü v2")
        self.geometry("1280x800")
        self.df = pd.read_csv("Mehmet_Okuyan.csv", encoding="utf-8")
        
        # Ana çerçeve
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- ÜST Panel: Arama Kutusu ---
        self.entry_arama = ctk.CTkEntry(self, placeholder_text="Kelime, ayet, sure ara…", width=540, font=("Arial", 18))
        self.entry_arama.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=30, sticky="n")
        self.entry_arama.bind("<Return>", lambda e: self.kelime_ara())
        
        # --- Ortada: Sonuç Paneli ---
        self.result_frame = ctk.CTkFrame(self, fg_color="#f7fafd", corner_radius=12)
        self.result_frame.grid(row=1, column=0, padx=(40, 10), pady=(10, 10), sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_text = ctk.CTkTextbox(self.result_frame, height=500, width=900, font=("Arial", 15))
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        
        # --- Sağ Panel: Ayete Git, Hoca Seç, Kelime Ara ---
        self.side_frame = ctk.CTkFrame(self, width=320, fg_color="#e7f1fc", corner_radius=8)
        self.side_frame.grid(row=1, column=1, padx=(10, 40), pady=(10, 10), sticky="n")
        
        ctk.CTkLabel(self.side_frame, text="Ayete Direkt Erişim", font=("Arial", 14, "bold")).pack(pady=(20, 2))
        self.sure_entry = ctk.CTkEntry(self.side_frame, placeholder_text="Sure No", width=80)
        self.ayet_entry = ctk.CTkEntry(self.side_frame, placeholder_text="Ayet No", width=80)
        self.git_btn = ctk.CTkButton(self.side_frame, text="GIT", command=self.ayete_git)
        self.sure_entry.pack(pady=5)
        self.ayet_entry.pack(pady=5)
        self.git_btn.pack(pady=10)
        
        # Hoca seçici
        ctk.CTkLabel(self.side_frame, text="Meali Seç:", font=("Arial", 12)).pack(pady=6)
        self.hoca_combobox = ctk.CTkComboBox(self.side_frame, values=sorted(self.df["hoca"].unique()))
        self.hoca_combobox.set(self.df["hoca"].unique()[0])
        self.hoca_combobox.pack(pady=5)
        
        # --- İlk yüklemede örnek bir ayeti göster
        self.show_ayet(sure=91, ayet=1, hoca=self.df["hoca"].unique()[0])
        
    def show_ayet(self, sure, ayet, hoca):
        self.result_text.delete("0.0", "end")
        ayetler = self.df[(self.df["sure"] == sure) & (self.df["ayet"] == ayet) & (self.df["hoca"] == hoca)]
        if ayetler.empty:
            self.result_text.insert("end", "Ayet bulunamadı.")
            return
        row = ayetler.iloc[0]
        tip = sure_tip.get(int(sure), "?")
        self.result_text.insert("end", f"{row['sure']}. Sure  /  {row['ayet']}. Ayet  [{tip}]\n", "header")
        self.result_text.insert("end", f"\n{row['metin']}\n\n")
        self.result_text.insert("end", f"(Hoca: {row['hoca']})", "footer")

    def kelime_ara(self):
        kelime = self.entry_arama.get().strip().lower()
        if not kelime:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("end", "Kelime giriniz…")
            return
        self.result_text.delete("0.0", "end")
        sonuclar = self.df[self.df["metin"].str.lower().str.contains(kelime, na=False)]
        if sonuclar.empty:
            self.result_text.insert("end", "Sonuç yok!")
            return
        for i, row in sonuclar.head(5).iterrows():
            tip = sure_tip.get(int(row["sure"]), "?")
            self.result_text.insert("end", f"{row['sure']}/{row['ayet']} [{tip}] {row['hoca']}\n", "header")
            metin = row["metin"].replace(kelime, f"⟦{kelime}⟧")
            self.result_text.insert("end", f"{metin}\n\n")

    def ayete_git(self):
        try:
            sure = int(self.sure_entry.get())
            ayet = int(self.ayet_entry.get())
        except:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("end", "Geçerli sure/ayet giriniz.")
            return
        hoca = self.hoca_combobox.get()
        self.show_ayet(sure, ayet, hoca)

if __name__ == "__main__":
    app = AcikKuranApp()
    app.mainloop()
