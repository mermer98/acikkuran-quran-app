import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import os
from datetime import datetime

class KuranArastirmaci:
    def __init__(self, root):
        self.root = root
        self.root.title("Kur'an Araştırmacısı v1")
        self.root.geometry("1200x800")
        self.data = None
        self.current_file = None
        self.current_format = None

        self.create_ui()

    def create_ui(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="CSV Aç", command=lambda: self.load_file('csv'))
        file_menu.add_command(label="JSON Aç", command=lambda: self.load_file('json'))
        file_menu.add_command(label="Excel Aç", command=lambda: self.load_file('xlsx'))
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)

        ara_menu = tk.Menu(menubar, tearoff=0)
        ara_menu.add_command(label="Kelime/Ayet/Sure Ara", command=self.search_keyword)
        ara_menu.add_command(label="Sıra No ile Ayet Bul", command=self.search_by_row)
        ara_menu.add_command(label="İstatistik (Kelime Frekansı)", command=self.word_frequency)
        menubar.add_cascade(label="Ara", menu=ara_menu)

        menubar.add_command(label="Farklı Kaydet (CSV)", command=lambda: self.save_file('csv'))

        self.root.config(menu=menubar)

        self.main_panel = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True)

        self.left_panel = ttk.Frame(self.main_panel, width=200)
        self.main_panel.add(self.left_panel)

        self.right_panel = ttk.Frame(self.main_panel)
        self.main_panel.add(self.right_panel)

        ttk.Label(self.left_panel, text="Veri İşlemleri", font=('Arial', 12, 'bold')).pack(pady=10)
        self.btn_add = ttk.Button(self.left_panel, text="Satır Ekle", command=self.add_row)
        self.btn_add.pack(pady=5, fill=tk.X)
        self.btn_delete = ttk.Button(self.left_panel, text="Satır Sil", command=self.delete_row)
        self.btn_delete.pack(pady=5, fill=tk.X)
        self.btn_edit = ttk.Button(self.left_panel, text="Satır Düzenle", command=self.edit_row)
        self.btn_edit.pack(pady=5, fill=tk.X)

        self.tree_frame = ttk.Frame(self.right_panel)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)

        self.status_bar = ttk.Label(self.root, text="Hazır", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X)

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
        self.current_format = file_format
        try:
            if file_format == 'csv':
                self.data = pd.read_csv(file_path)
            elif file_format == 'json':
                self.data = pd.read_json(file_path)
            elif file_format == 'xlsx':
                self.data = pd.read_excel(file_path)
            self.display_data(self.data)
            self.status_bar.config(text=f"Yüklendi: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenirken hata oluştu:\n{str(e)}")

    def display_data(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in df.columns:
            self.tree.column(col, anchor=tk.W, width=100)
            self.tree.heading(col, text=col, anchor=tk.W)
        for i, row in df.iterrows():
            self.tree.insert("", tk.END, iid=i, values=list(row))

    def add_row(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        add_window = tk.Toplevel(self.root)
        add_window.title("Yeni Satır Ekle")
        columns = self.data.columns
        entries = {}
        for i, col in enumerate(columns):
            ttk.Label(add_window, text=col).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(add_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[col] = entry
        def save_new_row():
            new_data = {col: entry.get() for col, entry in entries.items()}
            try:
                self.data = self.data.append(new_data, ignore_index=True)
                self.display_data(self.data)
                add_window.destroy()
                messagebox.showinfo("Başarılı", "Yeni satır başarıyla eklendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Satır eklenirken hata oluştu:\n{str(e)}")
        ttk.Button(add_window, text="Kaydet", command=save_new_row).grid(row=len(columns), columnspan=2, pady=10)

    def delete_row(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir satır seçin")
            return
        try:
            index = int(selected_item[0])
            self.data = self.data.drop(index).reset_index(drop=True)
            self.display_data(self.data)
            messagebox.showinfo("Başarılı", "Satır başarıyla silindi")
        except Exception as e:
            messagebox.showerror("Hata", f"Satır silinirken hata oluştu:\n{str(e)}")

    def edit_row(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir satır seçin")
            return
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Satır Düzenle")
        columns = self.data.columns
        row_data = self.data.iloc[int(selected_item[0])]
        entries = {}
        for i, col in enumerate(columns):
            ttk.Label(edit_window, text=col).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(edit_window)
            entry.insert(0, str(row_data[col]))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[col] = entry
        def save_edited_row():
            edited_data = {col: entry.get() for col, entry in entries.items()}
            try:
                index = int(selected_item[0])
                for col in columns:
                    self.data.at[index, col] = edited_data[col]
                self.display_data(self.data)
                edit_window.destroy()
                messagebox.showinfo("Başarılı", "Satır başarıyla güncellendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Satır güncellenirken hata oluştu:\n{str(e)}")
        ttk.Button(edit_window, text="Kaydet", command=save_edited_row).grid(row=len(columns), columnspan=2, pady=10)

    def save_file(self, file_format):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        file_types = {
            'csv': [('CSV Dosyaları', '*.csv')]
        }
        default_name = f"kuran_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=file_types[file_format],
            initialfile=default_name
        )
        if not file_path:
            return
        try:
            if file_format == 'csv':
                self.data.to_csv(file_path, index=False)
            messagebox.showinfo("Başarılı", f"Dosya başarıyla kaydedildi:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

    # ---- Araştırmacı Fonksiyonlar ---- #
    def search_keyword(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        keyword = simpledialog.askstring("Kelime Ara", "Aranacak kelime/ifade:")
        if not keyword:
            return
        matches = self.data[self.data.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        if matches.empty:
            messagebox.showinfo("Sonuç", "Hiçbir kayıt bulunamadı.")
        else:
            self.display_data(matches)

    def search_by_row(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        row_num = simpledialog.askinteger("Ayet Sırası", "Kaçıncı ayeti istiyorsun? (Örn: 300, 2524, 6236)")
        if not row_num:
            return
        # Sıra sütunu ismi "sıra" ya da "Sıra" olabilir, kontrol et:
        if 'sıra' in self.data.columns:
            matches = self.data[self.data['sıra'] == row_num]
        elif 'Sıra' in self.data.columns:
            matches = self.data[self.data['Sıra'] == row_num]
        else:
            messagebox.showerror("Hata", "Veride 'sıra' sütunu bulunamadı.")
            return
        if matches.empty:
            messagebox.showinfo("Sonuç", "Hiçbir kayıt bulunamadı.")
        else:
            self.display_data(matches)

    def word_frequency(self):
        if self.data is None:
            messagebox.showwarning("Uyarı", "Önce bir dosya yükleyin")
            return
        col_name = simpledialog.askstring("Kelime Sıklığı", "Hangi sütunda kelime sıklığı istiyorsun? (örn: 'metin')")
        if not col_name or col_name not in self.data.columns:
            messagebox.showerror("Hata", "Geçerli bir sütun adı girilmedi.")
            return
        from collections import Counter
        all_text = " ".join(self.data[col_name].astype(str).tolist())
        words = all_text.split()
        freq = Counter(words)
        freq_window = tk.Toplevel(self.root)
        freq_window.title("Kelime Frekansı")
        freq_list = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        text_widget = tk.Text(freq_window, width=60, height=30)
        text_widget.pack()
        for kelime, adet in freq_list[:200]:  # ilk 200 kelimeyi göster
            text_widget.insert(tk.END, f"{kelime}: {adet}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = KuranArastirmaci(root)
    root.mainloop()
