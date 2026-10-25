import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import os
from datetime import datetime
from collections import Counter

class KuranArastirmaciGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AçıkKuran Araştırmacısı v2")
        self.root.geometry("1200x800")
        self.data = None
        self.current_file = None
        self.create_ui()

    def create_ui(self):
        menubar = tk.Menu(self.root)

        # Dosya Menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="CSV Aç", command=lambda: self.load_file('csv'))
        file_menu.add_command(label="JSON Aç", command=lambda: self.load_file('json'))
        file_menu.add_command(label="Excel Aç", command=lambda: self.load_file('xlsx'))
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)

        # Arama Menüsü
        search_menu = tk.Menu(menubar, tearoff=0)
        search_menu.add_command(label="Anahtar Kelime/Kök Ara", command=self.anahtar_kelime_arama)
        search_menu.add_command(label="Sure/Ayet ile Ara (örn: 2/255)", command=self.sure_ayet_arama)
        search_menu.add_command(label="Sıra No ile Ara", command=self.sira_no_arama)
        search_menu.add_command(label="Tematik/Semantik Ara", command=self.tematik_arama)
        search_menu.add_command(label="Çapraz Kavram Analizi", command=self.capraz_kavram)
        search_menu.add_command(label="Bilimsel Bağlantı Analizi", command=self.bilimsel_baglanti)
        search_menu.add_command(label="Arapça Kök Analizi (CAMeL)", command=self.arapca_kok_analiz)
        menubar.add_cascade(label="Araştırma", menu=search_menu)

        # Not/Ekstra Menüsü
        note_menu = tk.Menu(menubar, tearoff=0)
        note_menu.add_command(label="Ayete Not Ekle", command=self.not_ekle)
        note_menu.add_command(label="Kelime Frekansı/İstatistik", command=self.kelime_frekans_istatistik)
        note_menu.add_command(label="Sonuçları Dışa Aktar", command=self.disari_aktar)
        menubar.add_cascade(label="Ekstralar", menu=note_menu)

        self.root.config(menu=menubar)

        # Ana Panel
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.status_bar = ttk.Label(self.root, text="Hazır", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X)

    # DOSYA YÜKLEME
    def load_file(self, file_format):
        file_types = {
            'csv': [('CSV Dosyaları', '*.csv')],
            'json': [('JSON Dosyaları', '*.json')],
            'xlsx': [('Excel Dosyaları', '*.xlsx')],
        }
        file_path = filedialog.askopenfilename(filetypes=file_types[file_format])
        if not file_path:
            return
        self.current_file = file_path
        if file_format == 'csv':
            self.data = pd.read_csv(file_path)
        elif file_format == 'json':
            self.data = pd.read_json(file_path)
        elif file_format == 'xlsx':
            self.data = pd.read_excel(file_path)
        if 'not' not in self.data.columns:
            self.data['not'] = ''
        self.display_data(self.data)
        self.status_bar.config(text=f"Yüklendi: {os.path.basename(file_path)}")

    # VERİ GÖRÜNTÜLEME
    def display_data(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in df.columns:
            self.tree.column(col, anchor=tk.W, width=100)
            self.tree.heading(col, text=col, anchor=tk.W)
        for i, row in df.iterrows():
            self.tree.insert("", tk.END, iid=i, values=list(row))

    # ANAHTAR KELİME/KÖK ARAMA
    def anahtar_kelime_arama(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        keyword = simpledialog.askstring("Anahtar Kelime/Kök", "Aranacak kelime veya kök:")
        if not keyword:
            return
        result = self.data[self.data.apply(lambda row: keyword in str(row.get('metin', '')) or keyword in str(row.get('kök', '')), axis=1)]
        self.display_data(result)
        self.status_bar.config(text=f"{len(result)} sonuç bulundu.")

    # SURE/AYET ARAMA
    def sure_ayet_arama(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        kod = simpledialog.askstring("Sure/Ayet", "Örn: 2/255 veya 36.38")
        if not kod:
            return
        kod = kod.replace('.', '/')
        try:
            sure, ayet = kod.split('/')
            result = self.data[(self.data['sure'].astype(str)==sure.strip()) & (self.data['ayet'].astype(str)==ayet.strip())]
            self.display_data(result)
            self.status_bar.config(text=f"{len(result)} sonuç bulundu.")
        except:
            messagebox.showerror("Hata", "Format yanlış! 2/255 veya 36.38 gibi olmalı.")

    # SIRA NO İLE ARA
    def sira_no_arama(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        sira = simpledialog.askstring("Sıra Numarası", "Ayet sıra no (örn: 2524):")
        if not sira:
            return
        result = self.data[self.data['sıra'].astype(str)==sira]
        self.display_data(result)
        self.status_bar.config(text=f"{len(result)} sonuç bulundu.")

    # TEMATİK ARAMA
    def tematik_arama(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        kelimeler = simpledialog.askstring("Tematik Arama", "Birden fazla kelime (virgüllü):")
        if not kelimeler:
            return
        kelime_liste = [k.strip() for k in kelimeler.split(',')]
        result = self.data[self.data['metin'].apply(lambda x: any(k in str(x) for k in kelime_liste))]
        self.display_data(result)
        self.status_bar.config(text=f"{len(result)} sonuç bulundu.")

    # ÇAPRAZ KAVRAM
    def capraz_kavram(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        kavram1 = simpledialog.askstring("Çapraz Kavram 1", "1. kelime/kök:")
        kavram2 = simpledialog.askstring("Çapraz Kavram 2", "2. kelime/kök:")
        if not kavram1 or not kavram2:
            return
        # Sadece 1.geçenler
        result1 = self.data[self.data['metin'].apply(lambda x: kavram1 in str(x) and kavram2 not in str(x))]
        # Sadece 2.geçenler
        result2 = self.data[self.data['metin'].apply(lambda x: kavram2 in str(x) and kavram1 not in str(x))]
        # Her ikisi geçenler
        result_both = self.data[self.data['metin'].apply(lambda x: kavram1 in str(x) and kavram2 in str(x))]
        # Sonuçları ayrı pencerede göster:
        self.display_data(result_both)
        self.status_bar.config(text=f"Her ikisi geçen: {len(result_both)} | Sadece {kavram1}: {len(result1)} | Sadece {kavram2}: {len(result2)}")

    # BİLİMSEL BAĞLANTI
    def bilimsel_baglanti(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        kelime = simpledialog.askstring("Bilimsel Kavram", "Bilimsel kelime/kavram:")
        if not kelime:
            return
        result = self.data[self.data['metin'].apply(lambda x: kelime in str(x))]
        self.display_data(result)
        self.status_bar.config(text=f"{len(result)} sonuç bulundu.")

    # ARAPÇA KÖK ANALİZİ (Opsiyonel, CAMeL Tools kuruluysa çalışır)
    def arapca_kok_analiz(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        try:
            from camel_tools.morphology.analyzer import Analyzer
            analyzer = Analyzer.builtin_analyzer()
            results = []
            for idx, row in self.data.iterrows():
                arapca = str(row.get('arapca', ''))
                if arapca:
                    analiz = analyzer.analyze(arapca)
                    results.append((row['sure'], row['ayet'], arapca, analiz[:1]))
            # Sonuçları pencerede göster
            top = tk.Toplevel(self.root)
            top.title("Arapça Kök Analizi Sonuçları")
            text = tk.Text(top)
            text.pack()
            for r in results:
                text.insert(tk.END, f"{r}\n")
        except Exception as e:
            messagebox.showerror("CAMeL Hatası", str(e))

    # KELİME FREKANS İSTATİSTİK
    def kelime_frekans_istatistik(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        metin = " ".join(self.data['metin'].astype(str).tolist())
        kelimeler = metin.split()
        frekans = Counter(kelimeler)
        top = tk.Toplevel(self.root)
        top.title("Kelime Frekansı")
        text = tk.Text(top)
        text.pack()
        for kelime, adet in frekans.most_common(100):
            text.insert(tk.END, f"{kelime}: {adet}\n")

    # NOT EKLE
    def not_ekle(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        ayet_no = simpledialog.askstring("Ayet Sıra No", "Not eklenecek sıra no:")
        notunuz = simpledialog.askstring("Not", "Notunuzu girin:")
        if ayet_no and notunuz:
            self.data.loc[self.data['sıra'].astype(str)==ayet_no, 'not'] = notunuz
            self.display_data(self.data)
            self.status_bar.config(text="Not eklendi.")

    # SONUÇ DIŞA AKTAR
    def disari_aktar(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce dosya yükleyin.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV Dosyası", "*.csv"), ("Metin Dosyası", "*.txt")])
        if not file_path:
            return
        if file_path.endswith('.csv'):
            self.data.to_csv(file_path, index=False)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                for idx, row in self.data.iterrows():
                    f.write(f"{row['sıra']}, {row['sure']}, {row['ayet']}, {row['hoca']}, {row['metin']}\n")
        messagebox.showinfo("Başarılı", f"{file_path} olarak kaydedildi.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KuranArastirmaciGUI(root)
    root.mainloop()
