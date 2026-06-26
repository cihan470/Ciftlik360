import sqlite3

# Mevcut veritabanımıza bağlanıyoruz (Yoksa oluşturur, varsa içine girer)
conn = sqlite3.connect('ciftlik.db')
c = conn.cursor()

# Sadece üyelerin bilgilerini tutacak yeni tabloyu kuruyoruz
c.execute('''
    CREATE TABLE IF NOT EXISTS kullanicilar (
        kullanici_adi TEXT PRIMARY KEY,
        sifre TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Kral, Kullanıcılar tablosu başarıyla eklendi!")