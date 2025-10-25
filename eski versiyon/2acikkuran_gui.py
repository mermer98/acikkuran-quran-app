import os
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MEAL_DIR = os.path.join(APP_DIR, "tum_mealler")
MEKKI_MEDENI_PATH = os.path.join(APP_DIR, "mekki_medeni.csv")

def load_mekki_medeni():
    try:
        df = pd.read_csv(MEKKI_MEDENI_PATH)
        sure_bilgi = {}
        for _, row in df.iterrows():
            sure_bilgi[str(row['sure'])] = row['tur'].strip()
        return sure_bilgi
    except Exception as e:
        print(f"Mekki/Medeni CSV okunamadı: {e}")
        return {}

mekki_medeni_dict = load_mekki_medeni()

def highlight_text(text, keyword):
    if not keyword: return text
    try:
        return re.sub(f'({re.escape(keyword)})', r'[\1]', text, flags=re.IGNORECASE)
    except Exception:
        return text

class KuranGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AçıkKuran Araştırmacısı v2")
        self.geometry("1000x650")
        self.meal_files = self.list_meal_files()
        self.mekki_medeni = mekki_medeni_dict
        self.meal_file = os.path.join(MEAL_DIR, "Mehmet_Okuyan.csv")
        self.df = None
        self.keyword = ""
        self.init_ui()
        self.load_meal(self.meal_file)
        
    def list_meal_files(self):
        if not os.path.exists(MEAL_DIR):
            os.makedirs(MEAL_DIR)
        return [f for f in os.listdir(MEAL_DIR) if f.endswith(".csv")]

    def init_ui(self):
        # Sol menü
        self.sidebar = ctk.CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text="AçıkKuran\nAraştırmacısı", font=("Arial", 18, "bold")).pack(pady=10)
        self.meal_select = ctk.CTkComboBox(self.sidebar, values=self.list_meal_files(), command=self.meal_selected)
        self.meal_select.pack(pady=5, padx=10)
        self.meal_select.set("Mehmet_Okuyan.csv")
        self.load_btn = ctk.CTkButton(self.sidebar, text="Başka Meal Yükle", command=self.load_new_meal)
        self.load_btn.pack(pady=5, padx=10)
        ctk.CTkLabel(self.sidebar, text="").pack(pady=10)

        # Orta panel
        self.main_panel = ctk.CTkFrame(self)
        self.main_panel.pack(side="right", expand=True, fill="both")
        self.search_entry = ctk.CTkEntry(self.main_panel, width=420, font=("Arial", 15))
        self.search_entry.pack(pady=10)
        self.search_entry.bind("<Return>", lambda e: self.search())
        self.search_btn = ctk.CTkButton(self.main_panel, text="ARA", command=self.search)
        self.search_btn.pack(pady=5)
        self.results_box = ctk.CTkTextbox(self.main_panel, wrap="word", width=800, height=400, font=("Consolas", 13))
        self.results_box.pack(padx=10, pady=10, expand=True, fill="both")

        # Sağdan ayet erişim paneli
        self.right_panel = ctk.CTkFrame(self.main_panel, width=160)
        self.right_panel.place(x=700, y=60)
        ctk.CTkLabel(self.right_panel, text="Ayete Direkt Erişim", font=("Arial", 13, "bold")).pack(pady=2)
        self.sure_no_entry = ctk.CTkEntry(self.right_panel, width=50, placeholder_text="Sure")
        self.sure_no_entry.pack(pady=1)
        self.ayet_no_entry = ctk.CTkEntry(self.right_panel, width=50, placeholder_text="Ayet")
        self.ayet_no_entry.pack(pady=1)
        self.goto_btn = ctk.CTkButton(self.right_panel, text="Git", command=self.goto_ayet)
        self.goto_btn.pack(pady=3)

    def load_meal(self, file_path):
        try:
            self.df = pd.read_csv(file_path, dtype=str)
            self.df = self.df.fillna("")
            self.meal_file = file_path
            self.update_results(self.df.head(10))
            self.meal_select.set(os.path.basename(file_path))
        except Exception as e:
            messagebox.showerror("Hata", f"Meal yüklenemedi:\n{e}")

    def load_new_meal(self):
        file_path = filedialog.askopenfilename(title="CSV meal dosyası seçin", filetypes=[("CSV dosyası", "*.csv")])
        if file_path:
            self.load_meal(file_path)
            if os.path.dirname(file_path) != MEAL_DIR:
                # Kopyala
                import shutil
                shutil.copy(file_path, MEAL_DIR)
                self.meal_select.configure(values=self.list_meal_files())

    def meal_selected(self, meal_name):
        file_path = os.path.join(MEAL_DIR, meal_name)
        self.load_meal(file_path)

    def search(self):
        if self.df is None:
            return
        self.keyword = self.search_entry.get().strip()
        if not self.keyword:
            self.update_results(self.df.head(10))
            return
        df_result = self.df[self.df['metin'].str.contains(self.keyword, case=False, na=False)]
        self.update_results(df_result)

    def goto_ayet(self):
        sure = self.sure_no_entry.get().strip()
        ayet = self.ayet_no_entry.get().strip()
        if not sure or not ayet: return
        try:
            df_result = self.df[(self.df['sure'] == str(sure)) & (self.df['ayet'] == str(ayet))]
            self.update_results(df_result)
        except Exception as e:
            messagebox.showerror("Hata", f"Ayet bulunamadı:\n{e}")

    def update_results(self, df):
        self.results_box.configure(state="normal")
        self.results_box.delete("1.0", "end")
        if df.empty:
            self.results_box.insert("end", "Sonuç bulunamadı.")
            self.results_box.configure(state="disabled")
            return
        for idx, row in df.iterrows():
            mekki_medeni = self.mekki_medeni.get(str(row['sure']), "")
            metin = row['metin']
            if self.keyword:
                metin = highlight_text(metin, self.keyword)
            satir = f"{row['sure']}. Sure ({mekki_medeni}) / {row['ayet']}. Ayet\n{metin}\n(Hoca: {row.get('hoca', '')})\n\n"
            self.results_box.insert("end", satir)
        self.results_box.configure(state="disabled")
        # Bind click
        self.results_box.bind("<Double-Button-1>", self.show_all_meals_for_ayet)

    def show_all_meals_for_ayet(self, event):
        # Seçili satırı bul
        index = self.results_box.index("@%d,%d" % (event.x, event.y))
        line = self.results_box.get(f"{index} linestart", f"{index} lineend")
        import re
        m = re.match(r"(\d+)\. Sure.*\/ (\d+)\. Ayet", line)
        if not m: return
        sure, ayet = m.groups()
        ayet_mealler = []
        for meal_file in self.list_meal_files():
            fpath = os.path.join(MEAL_DIR, meal_file)
            try:
                df = pd.read_csv(fpath, dtype=str).fillna("")
                match = df[(df['sure'] == sure) & (df['ayet'] == ayet)]
                for _, row in match.iterrows():
                    ayet_mealler.append(f"{meal_file.replace('.csv','')}: {row['metin']}")
            except: continue
        popup = ctk.CTkToplevel(self)
        popup.title(f"Tüm Mealler - {sure}/{ayet}")
        popup.geometry("640x400")
        txt = ctk.CTkTextbox(popup, font=("Consolas", 13), wrap="word")
        txt.pack(expand=True, fill="both", padx=10, pady=10)
        txt.insert("end", "\n\n".join(ayet_mealler))
        txt.configure(state="disabled")

if __name__ == "__main__":
    app = KuranGUI()
    app.mainloop()
