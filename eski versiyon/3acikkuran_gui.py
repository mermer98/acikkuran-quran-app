import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os

DEFAULT_MEAL = "Mehmet_Okuyan.csv"     # varsayılan dosya adı (klasörde olmalı)
MEAL_FOLDER = "tum_mealler"
MEKKI_MEDENI_FILE = "mekki_medeni.csv" # sure ve tipi

# GUI için temel renk ve font ayarları
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class KuranGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Açık Kur'an Araştırmacısı")
        self.geometry("1000x650")

        # DataFrame'ler
        self.meal_df = None  # seçili hocanın meali
        self.mekki_medeni_df = None  # sure-tipi

        # Yükleme
        self.load_mekki_medeni()
        self.load_meal(os.path.join(MEAL_FOLDER, DEFAULT_MEAL))

        # ---- ARAYÜZ ----
        # SOL PANEL (hoca seçimi, dosya açma, sure/ayet)
        self.left_panel = ctk.CTkFrame(self, width=220)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)
        self.left_panel.pack_propagate(0)

        ctk.CTkLabel(self.left_panel, text="Meâl Seç/Dosya Aç:", font=("Arial", 13, "bold")).pack(pady=(5, 0))
        self.hoca_combo = ctk.CTkComboBox(self.left_panel, command=self.change_meal)
        self.hoca_combo.pack(pady=4, fill="x")
        self.update_hoca_list()
        ctk.CTkButton(self.left_panel, text="Yeni Meâl Yükle", command=self.open_meal).pack(pady=2, fill="x")

        ctk.CTkLabel(self.left_panel, text="Ayete Git (2/255 veya 300):", font=("Arial", 11)).pack(pady=(14, 0))
        self.goto_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Sure/Ayet veya Sıra")
        self.goto_entry.pack(pady=2, fill="x")
        self.goto_entry.bind("<Return>", self.goto_ayet)

        self.mekki_label = ctk.CTkLabel(self.left_panel, text="", font=("Arial", 11, "italic"), text_color="#888")
        self.mekki_label.pack(pady=5)

        # SAĞ PANEL (arama ve sonuçlar)
        right_panel = ctk.CTkFrame(self)
        right_panel.pack(side="left", fill="both", expand=True, padx=(0,10), pady=10)

        search_frame = ctk.CTkFrame(right_panel)
        search_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(search_frame, text="Ayet/Kelime Ara:", font=("Arial", 13, "bold")).pack(side="left", padx=4)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Kelime veya ifade")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.search_entry.bind("<Return>", self.search)

        # Sonuç kutusu
        self.result_box = ctk.CTkTextbox(right_panel, font=("Consolas", 13), wrap="word")
        self.result_box.pack(fill="both", expand=True, pady=7)
        self.result_box.bind("<Double-1>", self.show_all_meals_for_ayet)

        # İlk açılışta varsayılan meal ve ayet listesini göster
        self.update_results(self.meal_df.head(20))
        self.mekki_label.configure(text="")

    def load_mekki_medeni(self):
        try:
            self.mekki_medeni_df = pd.read_csv(MEKKI_MEDENI_FILE)
        except Exception:
            self.mekki_medeni_df = None

    def load_meal(self, file_path):
        try:
            self.meal_df = pd.read_csv(file_path, dtype=str)
            self.current_meal_file = file_path
            # hoca adını bul
            if "hoca" in self.meal_df.columns:
                self.current_hoca = self.meal_df["hoca"].iloc[0]
            else:
                self.current_hoca = os.path.basename(file_path).replace(".csv", "")
            return True
        except Exception as e:
            messagebox.showerror("Yükleme Hatası", f"Meâl dosyası açılamadı:\n{e}")
            return False

    def update_hoca_list(self):
        # Klasördeki tüm mealleri listeler
        try:
            files = [f for f in os.listdir(MEAL_FOLDER) if f.endswith(".csv")]
        except:
            files = []
        self.hoca_combo.configure(values=files)
        # Default'u seçili yap
        if DEFAULT_MEAL in files:
            self.hoca_combo.set(DEFAULT_MEAL)
        elif files:
            self.hoca_combo.set(files[0])
        else:
            self.hoca_combo.set("")

    def open_meal(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not file_path:
            return
        filename = os.path.basename(file_path)
        dest = os.path.join(MEAL_FOLDER, filename)
        # Farklı klasörden seçildiyse mealler klasörüne kopyala
        if not os.path.exists(dest):
            import shutil
            shutil.copy(file_path, dest)
        self.update_hoca_list()
        self.hoca_combo.set(filename)
        self.load_meal(dest)
        self.update_results(self.meal_df.head(20))

    def change_meal(self, filename):
        path = os.path.join(MEAL_FOLDER, filename)
        if self.load_meal(path):
            self.update_results(self.meal_df.head(20))

    def search(self, event=None):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.update_results(self.meal_df.head(20))
            return
        # Arama: metin sütununda ara (büyük/küçük duyarsız)
        df = self.meal_df[self.meal_df["metin"].str.contains(keyword, case=False, na=False)]
        self.update_results(df, keyword=keyword)

    def goto_ayet(self, event=None):
        val = self.goto_entry.get().strip()
        if not val:
            return
        df = self.meal_df
        found = None
        if "/" in val:  # örn: 2/255
            sure, ayet = val.split("/", 1)
            found = df[(df["sure"].astype(str) == sure.strip()) & (df["ayet"].astype(str) == ayet.strip())]
        else:  # doğrudan sıra numarası
            found = df[df["sira"].astype(str) == val]
        if found is not None and not found.empty:
            self.update_results(found)
        else:
            messagebox.showinfo("Bulunamadı", "Aradığınız ayet bulunamadı.")
            self.update_results(df.head(20))

    def update_results(self, df, keyword=None):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        if df is None or df.empty:
            self.result_box.insert("end", "Kayıt bulunamadı.")
            self.mekki_label.configure(text="")
            return
        lines = []
        for idx, row in df.iterrows():
            ayet_line = f"[{row['sira']}] {row['sure']}/{row['ayet']} — {row['metin']}"
            if keyword and keyword.lower() in row['metin'].lower():
                # Basit vurgulama: yıldız içine al
                ayet_line = ayet_line.replace(keyword, f"*{keyword}*")
            lines.append(ayet_line)
        self.result_box.insert("end", "\n\n".join(lines))
        self.result_box.configure(state="disabled")

        # İlk kaydın sure/ayet bilgisinden Mekki/Medeni yazısı
        try:
            sure = df.iloc[0]['sure']
            tipi = ""
            if self.mekki_medeni_df is not None:
                tipi = self.mekki_medeni_df[self.mekki_medeni_df["sure"].astype(str) == str(sure)]["tip"].values
                if len(tipi): tipi = tipi[0]
            self.mekki_label.configure(text=f"{sure}. Sure: {tipi if tipi else ''}")
        except:
            self.mekki_label.configure(text="")

    def show_all_meals_for_ayet(self, event):
        # Sonuç kutusundan tıklanan ayetin sıra/sure/ayetini bul
        try:
            index = self.result_box.index("@%s,%s linestart" % (event.x, event.y))
            line = self.result_box.get(index, f"{index} lineend")
            # Satırdan sure ve ayet bul
            import re
            m = re.match(r"\[(\d+)\] (\d+)/(\d+)", line)
            if not m: return
            sira, sure, ayet = m.groups()
            # Tüm meallerde bu ayeti ara
            meal_texts = []
            files = [f for f in os.listdir(MEAL_FOLDER) if f.endswith(".csv")]
            for fname in files:
                try:
                    df = pd.read_csv(os.path.join(MEAL_FOLDER, fname), dtype=str)
                    fnd = df[(df["sure"].astype(str) == sure) & (df["ayet"].astype(str) == ayet)]
                    if not fnd.empty:
                        hoca = fnd["hoca"].iloc[0] if "hoca" in fnd.columns else fname.replace(".csv", "")
                        meal = fnd["metin"].iloc[0]
                        meal_texts.append(f"[{hoca}]\n{meal}\n")
                except Exception as e:
                    continue
            # Popup göster
            popup = ctk.CTkToplevel(self)
            popup.title(f"{sure}/{ayet} - Tüm Mealler")
            textbox = ctk.CTkTextbox(popup, font=("Consolas", 13), wrap="word", width=540, height=400)
            textbox.pack(fill="both", expand=True, padx=12, pady=12)
            textbox.insert("end", "\n\n".join(meal_texts) if meal_texts else "Diğer meallerde ayet bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

if __name__ == "__main__":
    app = KuranGUI()
    app.mainloop()
