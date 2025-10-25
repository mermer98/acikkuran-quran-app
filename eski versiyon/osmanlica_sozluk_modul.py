import customtkinter as ctk
import pandas as pd
import os
import datetime
from tkinter import filedialog
import json

SOZLUK_DOSYA = "osmanlica_sozluk.txt"
EK_ALANLAR = ["favori", "etiket", "aciklama", "kaynak"]
ARAP_HARFLER = [
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ',
    'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص',
    'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق',
    'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'ء', 'ى', 'ة'
]

# --- KUR'AN DOSYALARINI BAŞTA YÜKLE ---
def kuran_json_yukle(dosya):
    with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)

QURAN_ARAPCA = kuran_json_yukle("quran_arabic_6236.json")
QURAN_TURKCE = kuran_json_yukle("kuran_meali_mustafa_ozturk_6236.json")

def sozluk_yukle(dosya=SOZLUK_DOSYA):
    cols = ["kelime", "arapca", "anlam"] + EK_ALANLAR
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(dosya, delimiter=",", names=cols, dtype=str)
    df = df.fillna("")
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    df["arapca"] = df["arapca"].astype(str).str.replace(r"\s+", "", regex=True)
    return df

def sozluk_kaydet(df, dosya=SOZLUK_DOSYA):
    df.to_csv(dosya, sep="\t", header=False, index=False, encoding="utf-8")

def kok_bul(aranan):
    return aranan[:3] if len(aranan) >= 3 else aranan

def sozluk_ara(df, aranan, arama_modu="içeren", arapca_oto_kok=True):
    aranan = str(aranan).strip().replace(" ", "")
    df1 = df.copy()
    df1["kelime"] = df1["kelime"].astype(str).str.strip().str.lower()
    df1["anlam"] = df1["anlam"].astype(str).str.strip().str.lower()
    df1["arapca"] = df1["arapca"].astype(str).str.replace(r"\s+", "", regex=True)
    aranan_arapca = aranan if any('\u0600' <= c <= '\u06FF' for c in aranan) else aranan.lower()

    if arama_modu == "içeren":
        mask = (
            df1["kelime"].str.contains(aranan.lower(), na=False) |
            df1["arapca"].str.contains(aranan_arapca, na=False) |
            df1["anlam"].str.contains(aranan.lower(), na=False)
        )
    elif arama_modu == "tam":
        mask = (
            (df1["kelime"] == aranan.lower()) |
            (df1["arapca"] == aranan_arapca) |
            (df1["anlam"] == aranan.lower())
        )
    elif arama_modu == "başlayan":
        mask = (
            df1["kelime"].str.startswith(aranan.lower(), na=False) |
            df1["arapca"].str.startswith(aranan_arapca, na=False) |
            df1["anlam"].str.startswith(aranan.lower(), na=False)
        )
    else:
        mask = pd.Series([True] * len(df1))
    sonuc = df1[mask]
    # Kök bulucu
    if sonuc.empty and arapca_oto_kok and any('\u0600' <= c <= '\u06FF' for c in aranan_arapca):
        kok = kok_bul(aranan_arapca)
        sonuc = df1[df1["arapca"].str.contains(kok, na=False)]
    return sonuc

class SozlukApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Osmanlıca-Türkçe Lugât | Gelişmiş Sürüm")
        self.geometry("1200x630")
        self.df = sozluk_yukle()
        self.filtered_df = self.df.copy()
        self.undo_stack = []
        self.arama_modu = "içeren"
        self.siralama = "Varsayılan"
        self.secili_index = None

        # ÜST PANEL: DIŞA/İÇE AKTAR, GERİ AL, SIRALAMA
        ctk.CTkButton(self, text="Dışa Aktar (CSV)", command=self.export_csv, width=120).place(x=8, y=8)
        ctk.CTkButton(self, text="Favori Ekle/Çıkar", command=self.favori_degistir, width=100, fg_color="#ffbe2f").place(x=1080, y=380)
        ctk.CTkButton(self, text="Sadece Favoriler", command=self.sadece_favorileri_goster, width=120, fg_color="#ffd900").place(x=900, y=8)

        ctk.CTkButton(self, text="Veri İçe Aktar", command=self.import_data, width=120).place(x=138, y=8)
        ctk.CTkButton(self, text="Geri Al", command=self.undo, width=80, fg_color="#e8d100").place(x=268, y=8)
        ctk.CTkLabel(self, text="Sırala:", font=("Arial", 12)).place(x=370, y=12)
        self.cmb_siralama = ctk.CTkComboBox(self, values=["Varsayılan", "Alfabetik", "Arapça", "Köke Göre", "Anlama Göre", "Favori Öncelikli"], width=160, command=self.siralamayi_degistir)
        self.cmb_siralama.place(x=420, y=8)

        # ARAMA ALANI
        ctk.CTkLabel(self, text="Arama (Türkçe/Arapça/kök):", font=("Arial", 13, "bold")).place(x=8, y=48)
        self.entry_search = ctk.CTkEntry(self, font=("Arial", 16), width=260)
        self.entry_search.place(x=200, y=45)
        self.entry_search.bind("<KeyRelease>", lambda e: self.ara())
        self.entry_search.bind("<Return>", lambda e: self.ara())
        ctk.CTkButton(self, text="Ara", command=self.ara, width=80).place(x=470, y=45)
        ctk.CTkButton(self, text="Tümü", command=self.tumunu_goster, width=80).place(x=560, y=45)
        ctk.CTkLabel(self, text="Arama modu:", font=("Arial", 11)).place(x=660, y=48)
        self.cmb_arama = ctk.CTkComboBox(self, values=["içeren", "tam", "başlayan"], width=100, command=self.arama_modunu_degistir)
        self.cmb_arama.place(x=750, y=45)
        self.cmb_arama.set("içeren")

        # Etiket Arama Kutusu ve Butonu
        self.entry_etiket_arama = ctk.CTkEntry(self, font=("Arial", 13), width=90)
        self.entry_etiket_arama.place(x=870, y=45)
        ctk.CTkButton(self, text="Etiketle Ara", command=self.etiketle_ara, width=90).place(x=970, y=45)

        # --- KUR’ANDA ARA BUTONU ---
        ctk.CTkButton(self, text="Kur’anda Ara", command=self.kuranda_ara_popup, width=120, fg_color="#05a2e6").place(x=1080, y=45)

        # LİSTE
        self.listbox = ctk.CTkTextbox(self, font=("Consolas", 12), width=1050, height=240, wrap="none")
        self.listbox.place(x=8, y=88)
        self.listbox.configure(state="disabled")
        self.listbox.bind("<Double-Button-1>", self.liste_cift_tik)
        self.listbox.bind("<Button-1>", self.liste_secildi)

        # EKLEME ALANI
        ctk.CTkLabel(self, text="Yeni Kelime Ekle:", font=("Arial", 12, "bold")).place(x=8, y=340)
        self.entry_kelime = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.entry_kelime.place(x=130, y=340)
        self.entry_arapca = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.entry_arapca.place(x=240, y=340)
        self.entry_anlam = ctk.CTkEntry(self, font=("Arial", 13), width=220)
        self.entry_anlam.place(x=350, y=340)
        self.entry_etiket = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.entry_etiket.place(x=580, y=340)
        self.entry_aciklama = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.entry_aciklama.place(x=690, y=340)
        self.entry_kaynak = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.entry_kaynak.place(x=800, y=340)
        ctk.CTkButton(self, text="Ekle", command=self.kelime_ekle, width=60).place(x=910, y=340)

        # DÜZENLEME ALANI
        ctk.CTkLabel(self, text="Seçili (Düzenle/Sil):", font=("Arial", 12, "bold")).place(x=8, y=380)
        self.sel_kelime = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.sel_kelime.place(x=130, y=380)
        self.sel_arapca = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.sel_arapca.place(x=240, y=380)
        self.sel_anlam = ctk.CTkEntry(self, font=("Arial", 13), width=220)
        self.sel_anlam.place(x=350, y=380)
        self.sel_etiket = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.sel_etiket.place(x=580, y=380)
        self.sel_aciklama = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.sel_aciklama.place(x=690, y=380)
        self.sel_kaynak = ctk.CTkEntry(self, font=("Arial", 13), width=100)
        self.sel_kaynak.place(x=800, y=380)
        ctk.CTkButton(self, text="Düzenle", command=self.kelime_duzenle, width=80).place(x=910, y=380)
        ctk.CTkButton(self, text="Sil", command=self.kelime_sil, width=60, fg_color="#db4444").place(x=995, y=380)

        # SANAL ARAPÇA KLAVYE (sadece __init__ içinde!)
        ctk.CTkLabel(self, text="Arapça Klavye:", font=("Arial", 10, "bold")).place(x=10, y=520)
        self.klavye_target = None
        ctk.CTkButton(self, text="Arama Kutusu", width=80, height=22, command=lambda: self.klavye_hedefi(self.entry_search)).place(x=110, y=520)
        ctk.CTkButton(self, text="Yeni Arapça", width=80, height=22, command=lambda: self.klavye_hedefi(self.entry_arapca)).place(x=200, y=520)
        for i, harf in enumerate(ARAP_HARFLER):
            x = 300 + (i % 15) * 32
            y = 520 + (i // 15) * 32
            ctk.CTkButton(self, text=harf, width=30, height=30, command=lambda h=harf: self.klavyeye_yaz(h)).place(x=x, y=y)

        self.tumunu_goster()

    # --- KUR’ANDA ARA FONKSİYONU ---
    def kuranda_ara_popup(self):
        kelime = ""
        if self.sel_arapca.get().strip():
            kelime = self.sel_arapca.get().strip()
            arapca_mi = True
        elif self.sel_kelime.get().strip():
            kelime = self.sel_kelime.get().strip()
            arapca_mi = False
        elif self.entry_search.get().strip():
            kelime = self.entry_search.get().strip()
            arapca_mi = any('\u0600' <= c <= '\u06FF' for c in kelime)
        else:
            self.popup_mesaj("Önce arama kutusundan veya listedeki bir kayıttan kelime seçin!")
            return

        bulunanlar = []
        for ayt_ar, ayt_tr in zip(QURAN_ARAPCA, QURAN_TURKCE):
            if arapca_mi:
                if kelime in ayt_ar.get("metin", ""):
                    bulunanlar.append((ayt_ar, ayt_tr))
            else:
                if kelime.lower() in ayt_tr.get("metin", "").lower():
                    bulunanlar.append((ayt_ar, ayt_tr))

        win = ctk.CTkToplevel(self)
        win.title("Kur’anda Ara Sonuçları")
        win.geometry("900x450")
        ctk.CTkLabel(win, text=f"Kur’an’da '{kelime}' için bulunan ayetler: {len(bulunanlar)}", font=("Arial", 13, "bold")).pack(pady=8)
        tb = ctk.CTkTextbox(win, width=870, height=370, font=("Arial", 13), wrap="word")
        tb.pack(padx=10, pady=10)
        if not bulunanlar:
            tb.insert("end", "Sonuç bulunamadı.")
        else:
            for ayt_ar, ayt_tr in bulunanlar:
                satir = (f"[{ayt_ar['sure']}:{ayt_ar['ayet']}] "
                         f"{ayt_ar['metin']}\n"
                         f"{ayt_tr['metin']}\n\n")
                tb.insert("end", satir)
        tb.configure(state="disabled")
        ctk.CTkButton(win, text="Kapat", command=win.destroy).pack(pady=8)

    # --- KISA FONKSİYONLAR ---
    def etiketle_ara(self):
        aranan_etiket = self.entry_etiket_arama.get().strip()
        if not aranan_etiket:
            self.tumunu_goster()
            return
        etikete_gore = self.df[self.df["etiket"].str.contains(aranan_etiket, na=False, case=False)]
        self.filtered_df = etikete_gore.reset_index(drop=True)
        self.listele(self.filtered_df)

    def klavye_hedefi(self, kutu):
        self.klavye_target = kutu

    def klavyeye_yaz(self, harf):
        if self.klavye_target:
            self.klavye_target.insert(ctk.INSERT, harf)

    def tumunu_goster(self):
        df = self.df.copy()
        if self.siralama == "Alfabetik":
            df = df.sort_values("kelime")
        elif self.siralama == "Arapça":
            df = df.sort_values("arapca")
        elif self.siralama == "Köke Göre":
            df["kok"] = df["arapca"].apply(lambda x: kok_bul(x))
            df = df.sort_values("kok")
        elif self.siralama == "Anlama Göre":
            df = df.sort_values("anlam")
        elif self.siralama == "Favori Öncelikli":
            df = df.sort_values("favori", ascending=False)
        self.filtered_df = df.reset_index(drop=True)
        self.listele(self.filtered_df)

    def siralamayi_degistir(self, mode):
        self.siralama = mode
        self.tumunu_goster()

    def arama_modunu_degistir(self, mode):
        self.arama_modu = mode
        self.ara()

    def ara(self):
        aranan = self.entry_search.get().strip()
        if not aranan:
            self.tumunu_goster()
            return
        self.filtered_df = sozluk_ara(self.df, aranan, arama_modu=self.arama_modu)
        self.listele(self.filtered_df)

    def listele(self, df):
        self.listbox.configure(state="normal")
        self.listbox.delete(0.0, ctk.END)
        aranan = self.entry_search.get().strip()
        if df.empty:
            self.listbox.insert(ctk.END, "Sonuç bulunamadı.")
        else:
            for i, row in df.iterrows():
                favori = "★ " if row.get("favori", "") == "1" else "  "
                etiket = f"[{row['etiket']}]" if row.get("etiket") else ""
                acik = f" ({row['aciklama']})" if row.get("aciklama") else ""
                kaynak = f" <{row['kaynak']}>" if row.get("kaynak") else ""
                satirda_var = False
                for field in [row['kelime'], row['arapca'], row['anlam']]:
                    if aranan and aranan in str(field):
                        satirda_var = True
                        break
                simge = "🟨 " if satirda_var and aranan else ""
                satir = f"{simge}{favori}{row['kelime']:15} | {row['arapca']:15} | {row['anlam']:20} {etiket}{acik}{kaynak}\n"
                self.listbox.insert(ctk.END, satir)
        self.listbox.configure(state="disabled")
        self.secili_index = None
        self.sel_kelime.delete(0, ctk.END)
        self.sel_arapca.delete(0, ctk.END)
        self.sel_anlam.delete(0, ctk.END)
        self.sel_etiket.delete(0, ctk.END)
        self.sel_aciklama.delete(0, ctk.END)
        self.sel_kaynak.delete(0, ctk.END)

    def liste_secildi(self, event):
        try:
            index = int(float(self.listbox.index("@%s,%s" % (event.x, event.y)).split('.')[0])) - 1
            if index < 0 or index >= len(self.filtered_df): return
            row = self.filtered_df.iloc[index]
            self.secili_index = self.filtered_df.index[index]
            self.sel_kelime.delete(0, ctk.END)
            self.sel_arapca.delete(0, ctk.END)
            self.sel_anlam.delete(0, ctk.END)
            self.sel_etiket.delete(0, ctk.END)
            self.sel_aciklama.delete(0, ctk.END)
            self.sel_kaynak.delete(0, ctk.END)
            self.sel_kelime.insert(0, row['kelime'])
            self.sel_arapca.insert(0, row['arapca'])
            self.sel_anlam.insert(0, row['anlam'])
            self.sel_etiket.insert(0, row.get("etiket", ""))
            self.sel_aciklama.insert(0, row.get("aciklama", ""))
            self.sel_kaynak.insert(0, row.get("kaynak", ""))
        except Exception:
            pass

    def liste_cift_tik(self, event):
        self.liste_secildi(event)
        self.sel_kelime.focus_set()

    def push_undo(self):
        self.undo_stack.append(self.df.copy())
        if len(self.undo_stack) > 10:
            self.undo_stack = self.undo_stack[-10:]

    def undo(self):
        if self.undo_stack:
            self.df = self.undo_stack.pop()
            sozluk_kaydet(self.df)
            self.tumunu_goster()
            self.popup_mesaj("Geri alındı.")

    def export_csv(self):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        fname = f"osmanlica_sozluk_{now}.csv"
        self.df.to_csv(fname, index=False, encoding="utf-8-sig")
        self.popup_mesaj(f"CSV dosyası kaydedildi: {fname}")

    def import_data(self):
        fname = filedialog.askopenfilename(
            filetypes=[("Sözlük Dosyası", "*.txt *.csv *.json"), ("Tüm Dosyalar", "*.*")]
        )
        if fname:
            try:
                df_new = sozluk_yukle(fname)
                self.push_undo()
                self.df = pd.concat([self.df, df_new], ignore_index=True).drop_duplicates(subset=["kelime", "arapca", "anlam"])
                sozluk_kaydet(self.df)
                self.tumunu_goster()
                self.popup_mesaj(f"Veri başarıyla içe aktarıldı: {fname}")
            except Exception as e:
                self.popup_mesaj(f"HATA: Dosya okunamadı!\n\n{e}")

    def popup_mesaj(self, msg):
        win = ctk.CTkToplevel(self)
        win.title("Bilgi")
        ctk.CTkLabel(win, text=msg, font=("Arial", 14)).pack(padx=18, pady=18)
        ctk.CTkButton(win, text="Tamam", command=win.destroy).pack(pady=8)

    # --- EKLE/DÜZENLE/SİL ---
    def kelime_ekle(self):
        kelime = self.entry_kelime.get().strip()
        arapca = self.entry_arapca.get().strip()
        anlam = self.entry_anlam.get().strip()
        etiket = self.entry_etiket.get().strip()
        aciklama = self.entry_aciklama.get().strip()
        kaynak = self.entry_kaynak.get().strip()
        favori = ""
        if not (kelime or arapca):
            self.popup_mesaj("Kelime veya Arapça kısmı zorunlu!")
            return
        self.push_undo()
        yeni = {"kelime": kelime, "arapca": arapca, "anlam": anlam,
                "favori": favori, "etiket": etiket, "aciklama": aciklama, "kaynak": kaynak}
        self.df = pd.concat([self.df, pd.DataFrame([yeni])], ignore_index=True)
        sozluk_kaydet(self.df)
        self.tumunu_goster()
        self.entry_kelime.delete(0, ctk.END)
        self.entry_arapca.delete(0, ctk.END)
        self.entry_anlam.delete(0, ctk.END)
        self.entry_etiket.delete(0, ctk.END)
        self.entry_aciklama.delete(0, ctk.END)
        self.entry_kaynak.delete(0, ctk.END)

    def kelime_duzenle(self):
        if self.secili_index is None:
            self.popup_mesaj("Düzenlenecek kayıt seçili değil.")
            return
        kelime = self.sel_kelime.get().strip()
        arapca = self.sel_arapca.get().strip()
        anlam = self.sel_anlam.get().strip()
        etiket = self.sel_etiket.get().strip()
        aciklama = self.sel_aciklama.get().strip()
        kaynak = self.sel_kaynak.get().strip()
        favori = self.df.loc[self.secili_index, "favori"] if "favori" in self.df.columns else ""
        self.push_undo()
        self.df.loc[self.secili_index, ["kelime", "arapca", "anlam", "etiket", "aciklama", "kaynak", "favori"]] = \
            [kelime, arapca, anlam, etiket, aciklama, kaynak, favori]
        sozluk_kaydet(self.df)
        self.tumunu_goster()

    def kelime_sil(self):
        if self.secili_index is None:
            self.popup_mesaj("Silinecek kayıt seçili değil.")
            return
        self.push_undo()
        self.df = self.df.drop(self.secili_index).reset_index(drop=True)
        sozluk_kaydet(self.df)
        self.tumunu_goster()

    def favori_degistir(self):
        if self.secili_index is None:
            self.popup_mesaj("Favori eklemek için önce kayıt seçin.")
            return
        mevcut = self.df.loc[self.secili_index, "favori"]
        yeni = "0" if mevcut == "1" else "1"
        self.push_undo()
        self.df.loc[self.secili_index, "favori"] = yeni
        sozluk_kaydet(self.df)
        self.tumunu_goster()

    def sadece_favorileri_goster(self):
        favs = self.df[self.df["favori"] == "1"].reset_index(drop=True)
        self.filtered_df = favs
        self.listele(favs)

if __name__ == "__main__":
    app = SozlukApp()
    app.mainloop()
