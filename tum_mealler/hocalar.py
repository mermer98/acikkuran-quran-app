import requests
import csv
import json
import time
import os

def get_authors():
    url = "https://api.acikkuran.com/authors"
    data = requests.get(url, timeout=10).json()["data"]
    return [{"id": a["id"], "name": a["name"]} for a in data]

def get_sureler():
    url = "https://api.acikkuran.com/surahs"
    return requests.get(url, timeout=10).json()["data"]

def download_meal_for_author(author):
    author_id, hoca_adi = author["id"], author["name"]
    sureler = get_sureler()
    veriler, sira = [], 1

    for sure in sureler:
        sure_id = sure["id"]
        url = f"https://api.acikkuran.com/surah/{sure_id}?author={author_id}"
        try:
            r = requests.get(url, timeout=20)
            d = r.json().get("data", {})
            verses = d.get("verses", [])
            for v in verses:
                metin = ""
                if v.get("translation") and v["translation"].get("text"):
                    metin = v["translation"]["text"].replace("\n", " ").replace("\r", " ").strip()
                veriler.append({
                    "sira": sira,
                    "sure": sure_id,
                    "ayet": v.get("verse_number"),
                    "metin": metin,
                    "hoca": hoca_adi
                })
                sira += 1
        except Exception as ex:
            print(f"HATA: {hoca_adi} - Sure {sure_id} alınamadı: {ex}")
        time.sleep(0.1)

    # Dosya isimleri
    dosya_adi = hoca_adi.replace(" ", "_").replace(".", "").replace("’", "").replace("'", "").replace(",", "")
    os.makedirs("tum_mealler", exist_ok=True)
    csv_path = f"tum_mealler/{dosya_adi}.csv"
    json_path = f"tum_mealler/{dosya_adi}.json"

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sira", "sure", "ayet", "metin", "hoca"])
        writer.writeheader()
        writer.writerows(veriler)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

    print(f"✔ {hoca_adi} ({author_id}) tamamlandı. ({len(veriler)} ayet)")

def main():
    authors = get_authors()
    print("Tespit edilen hoca listesi:")
    for a in authors:
        print(f"{a['id']}: {a['name']}")

    for author in authors:
        download_meal_for_author(author)
        print("---")

if __name__ == "__main__":
    main()
