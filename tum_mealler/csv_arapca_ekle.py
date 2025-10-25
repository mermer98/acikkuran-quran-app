import pandas as pd
import json
import os

csv_path = "Mehmet_Okuyan.csv"
json_path = "arapca_ayetler.json"
output_path = "Mehmet_Okuyan_arapca.csv"

# Dosya yollarını tam klasör ile birleştir
csv_path = os.path.join(os.path.dirname(__file__), csv_path)
json_path = os.path.join(os.path.dirname(__file__), json_path)
output_path = os.path.join(os.path.dirname(__file__), output_path)

# CSV oku
df = pd.read_csv(csv_path, dtype=str)

# JSON oku
with open(json_path, "r", encoding="utf-8") as f:
    arapca_data = json.load(f)

# Arapça metinleri sira numarasına göre eşleştir
arapca_dict = {str(item["sira"]): item["arapca"] for item in arapca_data}

# Yeni sütun ekle
if "arapca" not in df.columns:
    df["arapca"] = df["sira"].map(arapca_dict)

# Yeni dosyaya kaydet
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Yeni dosya oluşturuldu: {output_path}")
