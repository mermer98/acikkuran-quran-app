import pandas as pd
import tkinter as tk
from tkinter import font
import arabic_reshaper
from bidi.algorithm import get_display

# Arapça ayetler dosyasını oku
df = pd.read_csv('arapca_ayetler.csv', dtype=str)

# Örnek: 3/7 ayetini bul
row = df[(df['sure'] == '3') & (df['ayet'] == '7')].iloc[0]
arapca_text = row['metin']

# Arapça metni şekillendir ve RTL olarak göster
reshaped_text = arabic_reshaper.reshape(arapca_text)
bidi_text = get_display(reshaped_text)

root = tk.Tk()
root.title('Arapça Ayet Label RTL Test')

# Uygun bir Arapça font varsa kullan (ör: Arial, Noto Naskh Arabic)
try:
    arapca_font = font.Font(family='Arial', size=18)
except:
    arapca_font = None

label = tk.Label(root, text=bidi_text, font=arapca_font, anchor='e', justify='right', bg='white', fg='black')
label.pack(fill='x', padx=20, pady=20)

root.mainloop()
