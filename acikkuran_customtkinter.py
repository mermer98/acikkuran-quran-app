import sqlite3

DB_PATH = r"C:\Users\abdul\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbs5n2kfra8p0\LocalCache\Roaming\camel_tools\data\morphology\calima-msa-r13\morphology.db"

def analiz_cek(kelime):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("PRAGMA table_info(analyses)")
    kolonlar = [c[1] for c in cur.fetchall()]
    cur.execute("SELECT * FROM analyses WHERE word=?", (kelime,))
    rows = cur.fetchall()
    con.close()
    for row in rows:
        for col, val in zip(kolonlar, row):
            print(f"{col}: {val}")
        print("-"*40)
    if not rows:
        print("Sonuç bulunamadı.")
