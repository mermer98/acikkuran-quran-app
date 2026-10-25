import pandas as pd
import tkinter as tk
from tkinter import font

# Arapça ayetler dosyasını oku
df = pd.read_csv('arapca_ayetler.csv', dtype=str)

# Örnek: 3/7 ayetini bul
row = df[(df['sure'] == '3') & (df['ayet'] == '7')].iloc[0]
arapca_text = row['metin']

# Tkinter ile RTL ve uygun font ile göster
root = tk.Tk()
root.title('Arapça Ayet RTL Test')

# Uygun bir Arapça font varsa kullan (ör: Arial, Noto Naskh Arabic)
try:
    arapca_font = font.Font(family='Arial', size=18)
except:
    arapca_font = None

label = tk.Label(root, text=arapca_text, font=arapca_font, anchor='e', justify='right')
label.pack(fill='x', padx=20, pady=20)

root.mainloop()
