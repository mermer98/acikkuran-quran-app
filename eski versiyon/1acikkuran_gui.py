import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
from collections import Counter
import re
import os

class QuranResearcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AçıkKuran Araştırmacısı")
        self.df = None
        self.file_path = ""
        self.create_widgets()

    def create_widgets(self):
        # Menü
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Meal Dosyası Aç", command=self.load_file)
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        self.root.config(menu=menubar)

        # Sekmeli arayüz
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # --- 1. Arama Sekmesi ---
        self.tab_search = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_search, text="Arama")

        frm_search = ttk.Frame(self.tab_search)
        frm_search.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm_search, text="Kelime/Kök Ara:").pack(side="left")
        self.entry_search = ttk.Entry(frm_search, width=30)
        self.entry_search.pack(side="left", padx=5)
        ttk.Button(frm_search, text="Ara", command=self.search_keyword).pack(side="left", padx=5)

        frm_sure_ayet = ttk.Frame(self.tab_search)
        frm_sure_ayet.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm_sure_ayet, text="Sure/Ayet No (örn: 2/255):").pack(side="left")
        self.entry_sure_ayet = ttk.Entry(frm_sure_ayet, width=10)
        self.entry_sure_ayet.pack(side="left", padx=5)
        ttk.Button(frm_sure_ayet, text="Git", command=self.search_sure_ayet).pack(side="left", padx=5)

        frm_sira = ttk.Frame(self.tab_search)
        frm_sira.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm_sira, text="Genel Ayet Sıra No:").pack(side="left")
        self.entry_sira = ttk.Entry(frm_sira, width=10)
        self.entry_sira.pack(side="left", padx=5)
        ttk.Button(frm_sira, text="Git", command=self.search_sira_no).pack(side="left", padx=5)

        # Sonuç tablosu
        self.tree = ttk.Treeview(self.tab_search, columns=("sıra", "sure", "ayet", "hoca", "metin"), show="headings")
        for col in ("sıra", "sure", "ayet", "hoca", "metin"):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=60 if col!="metin" else 550)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 2. Çapraz Kavram Sekmesi ---
        self.tab_cross = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cross, text="Çapraz Kavram")

        frm_cross = ttk.Frame(self.tab_cross)
        frm_cross.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm_cross, text="Kavram 1:").pack(side="left")
        self.entry_cross1 = ttk.Entry(frm_cross, width=15)
        self.entry_cross1.pack(side="left", padx=3)
        ttk.Label(frm_cross, text="Kavram 2:").pack(side="left")
        self.entry_cross2 = ttk.Entry(frm_cross, width=15)
        self.entry_cross2.pack(side="left", padx=3)
        ttk.Button(frm_cross, text="Karşılaştır", command=self.cross_compare).pack(side="left", padx=5)

        self.text_cross = tk.Text(self.tab_cross, wrap="word", height=18)
        self.text_cross.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 3. İstatistik Sekmesi ---
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="İstatistik")

        ttk.Button(self.tab_stats, text="Kelime Frekansı Analiz Et", command=self.word_stats).pack(pady=10)
        self.text_stats = tk.Text(self.tab_stats, wrap="word", height=22)
        self.text_stats.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 4. Not/Ek Açıklama Sekmesi ---
        self.tab_note = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_note, text="Not/Ek Açıklama")

        frm_note = ttk.Frame(self.tab_note)
        frm_note.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm_note, text="Ayet sıra no:").pack(side="left")
        self.entry_note_sira = ttk.Entry(frm_note, width=10)
        self.entry_note_sira.pack(side="left", padx=5)
        ttk.Label(frm_note, text="Not:").pack(side="left")
        self.entry_note = ttk.Entry(frm_note, width=40)
        self.entry_note.pack(side="left", padx=5)
        ttk.Button(frm_note, text="Kaydet", command=self.save_note).pack(side="left", padx=5)

        self.text_note = tk.Text(self.tab_note, wrap="word", height=22)
        self.text_note.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 5. Dışa Aktar Sekmesi ---
        self.tab_export = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_export, text="Dışa Aktar")
        ttk.Button(self.tab_export, text="Görünen Tabloyu CSV Kaydet", command=self.export_csv).pack(pady=20)
        self.label_export = ttk.Label(self.tab_export, text="")
        self.label_export.pack()

    # ==== Fonksiyonlar ====
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Dosyaları", "*.csv")])
        if not file_path: return
        self.df = pd.read_csv(file_path)
        self.file_path = file_path
        self.update_table(self.df)
        messagebox.showinfo("Başarılı", f"{os.path.basename(file_path)} yüklendi.")

    def update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=(row['sıra'], row['sure'], row['ayet'], row['hoca'], str(row['metin'])[:400]))

    def search_keyword(self):
        if self.df is None: return
        aranan = self.entry_search.get().strip()
        results = self.df[self.df['metin'].str.contains(aranan, case=False, na=False)]
        self.update_table(results)

    def search_sure_ayet(self):
        if self.df is None: return
        kod = self.entry_sure_ayet.get().replace('.', '/')
        try:
            sure, ayet = kod.split('/')
            results = self.df[(self.df['sure'].astype(str)==sure.strip()) & (self.df['ayet'].astype(str)==ayet.strip())]
            self.update_table(results)
        except:
            messagebox.showerror("Hata", "Format 2/255 şeklinde olmalı.")

    def search_sira_no(self):
        if self.df is None: return
        sira = self.entry_sira.get().strip()
        results = self.df[self.df['sıra'].astype(str)==sira]
        self.update_table(results)

    def cross_compare(self):
        if self.df is None: return
        k1 = self.entry_cross1.get().strip().lower()
        k2 = self.entry_cross2.get().strip().lower()
        t = ""
        t += f"-- Sadece {k1} geçen ayetler --\n"
        for _, row in self.df.iterrows():
            m = str(row['metin']).lower()
            if k1 in m and k2 not in m:
                t += f"{row['sure']}:{row['ayet']} | {row['metin']}\n"
        t += f"\n-- Sadece {k2} geçen ayetler --\n"
        for _, row in self.df.iterrows():
            m = str(row['metin']).lower()
            if k2 in m and k1 not in m:
                t += f"{row['sure']}:{row['ayet']} | {row['metin']}\n"
        t += f"\n-- Her ikisi de geçen ayetler --\n"
        for _, row in self.df.iterrows():
            m = str(row['metin']).lower()
            if k1 in m and k2 in m:
                t += f"{row['sure']}:{row['ayet']} | {row['metin']}\n"
        self.text_cross.delete(1.0, "end")
        self.text_cross.insert("end", t)

    def word_stats(self):
        if self.df is None: return
        metin = " ".join(str(m) for m in self.df['metin'])
        kelimeler = re.findall(r'\w+', metin.lower())
        frekans = Counter(kelimeler)
        t = "\nEn sık geçen 30 kelime:\n\n"
        for kelime, adet in frekans.most_common(30):
            t += f"{kelime}: {adet}\n"
        self.text_stats.delete(1.0, "end")
        self.text_stats.insert("end", t)

    def save_note(self):
        if self.df is None: return
        ayet_no = self.entry_note_sira.get().strip()
        not_metni = self.entry_note.get().strip()
        if not ayet_no or not not_metni:
            messagebox.showerror("Eksik", "Sıra no ve not giriniz!")
            return
        self.df.loc[self.df['sıra'].astype(str)==ayet_no, 'not'] = not_metni
        self.text_note.insert("end", f"{ayet_no} için not eklendi: {not_metni}\n")

    def export_csv(self):
        if self.df is None: return
        out_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dosyası", "*.csv")])
        if not out_path: return
        self.df.to_csv(out_path, index=False)
        self.label_export.config(text=f"Kaydedildi: {out_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuranResearcherGUI(root)
    root.mainloop()
