import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

class AcikKuranGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AçıkKuran Araştırmacısı")
        self.df = None  # Şu anki veri DataFrame’i

        # Menü
        menubar = tk.Menu(self.root)
        dosya_menu = tk.Menu(menubar, tearoff=0)
        dosya_menu.add_command(label="Meali Yükle", command=self.meal_yukle)
        menubar.add_cascade(label="Dosya", menu=dosya_menu)
        self.root.config(menu=menubar)

        # Tablo alanı
        self.table = tk.Text(self.root, height=20, width=120)
        self.table.pack()

    def meal_yukle(self):
        yol = filedialog.askopenfilename(
            filetypes=[("CSV Dosyaları", "*.csv")]
        )
        if not yol:
            return
        try:
            self.df = pd.read_csv(yol, encoding="utf-8")
            self.table.delete(1.0, tk.END)
            self.table.insert(tk.END, self.df.head(10).to_string(index=False))
        except Exception as e:
            messagebox.showerror("Hata", f"Meali yüklerken hata: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AcikKuranGUI(root)
    root.mainloop()
