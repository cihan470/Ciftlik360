import sqlite3

# 1. Veritabanına bağlan (Klasörde yoksa otomatik olarak 'ciftlik.db' adında bir dosya oluşturur)
conn = sqlite3.connect('ciftlik.db')
cursor = conn.cursor()

# 2. Hayvanlar (Buzağı) tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS buzagilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kupe_no TEXT NOT NULL,
    dogum_tarihi TEXT,
    cinsiyet TEXT
)
''')

# 3. İşlemi kaydet ve bağlantıyı hazır tut
conn.commit()
print("Kral, veritabanı bağlandı ve buzağılar tablosu hazır!")
# --- YENİ EKLENEN TABLOLAR ---

# Aşı Takip Tablosu (hayvan_id ile buzağılara bağlıyoruz)
cursor.execute('''
CREATE TABLE IF NOT EXISTS asi_takip (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hayvan_id INTEGER,
    asi_adi TEXT NOT NULL,
    planlanan_tarih TEXT,
    durum TEXT DEFAULT 'Yapılmadı',
    FOREIGN KEY(hayvan_id) REFERENCES buzagilar(id)
)
''')

# Yem ve Gider Tablosu (Çiftliğin kasası)
cursor.execute('''
CREATE TABLE IF NOT EXISTS yem_gider (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gider_turu TEXT NOT NULL,
    miktar REAL,
    tutar REAL,
    tarih TEXT
)
''')

# Değişiklikleri kaydet
conn.commit()
print("Sistem Güncellemesi: Aşı ve Yem tabloları başarıyla eklendi!")
# -----------------------------

# 4. Buzağı Ekleme Fonksiyonu (CRUD - Create)
def buzagi_ekle(kupe, tarih, cinsiyet):
    cursor.execute("INSERT INTO buzagilar (kupe_no, dogum_tarihi, cinsiyet) VALUES (?, ?, ?)",
                   (kupe, tarih, cinsiyet))
    conn.commit()
    print(f"Başarılı: {kupe} küpeli buzağı sisteme kaydedildi!")

# 5. Sistemi Test Et: İlk buzağımızı ekleyelim
# buzagi_ekle("TR-001", "2026-06-25", "Dişi")

# 6. Buzağıları Listeleme Fonksiyonu (CRUD - Read)
def buzagilari_listele():
    # Veritabanına "Bana buzagilar tablosundaki her şeyi (*) getir" diyoruz
    cursor.execute("SELECT * FROM buzagilar")
    hayvanlar = cursor.fetchall() # Gelen tüm verileri yakala ve 'hayvanlar' listesine at
    
    print("\n--- ÇİFTLİK 360: KAYITLI BUZAĞILAR ---")
    for hayvan in hayvanlar:
        print(f"Kayıt ID: {hayvan[0]} | Küpe No: {hayvan[1]} | Doğum Tarihi: {hayvan[2]} | Cinsiyet: {hayvan[3]}")
    print("--------------------------------------\n")

# 7. Sistemi Test Et: Kayıtları listeleyelim
buzagilari_listele()

# 8. Gider Ekleme Fonksiyonu
def gider_ekle(tur, miktar, tutar, tarih):
    cursor.execute("INSERT INTO yem_gider (gider_turu, miktar, tutar, tarih) VALUES (?, ?, ?, ?)",
                   (tur, miktar, tutar, tarih))
    conn.commit()
    print(f"KASAYA İŞLENDİ: {miktar} kg {tur} için {tutar} TL harcandı. Tarih: {tarih}")

# Test edelim (Eğer kodu tekrar tekrar çalıştırırsan aynı faturayı 2 kere girer, dikkat et)
# İlk çalıştırdıktan sonra bu satırın başına # koymayı unutma.
gider_ekle("Buzağı Büyütme Yemi", 50, 750.00, "2026-06-25")