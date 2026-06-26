import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Çiftlik 360", page_icon="🌾", layout="wide")
st.title("🌾 Çiftlik 360 Yönetim Paneli")
st.write("Sisteme hoş geldin patron! Çiftliğini buradan uçtan uca yönetebilirsin.")

def veritabani_baglan():
    return sqlite3.connect('ciftlik.db')

conn = veritabani_baglan()

# --- YAN MENÜ (SIDEBAR) / YENİ KAYIT FORMLARI ---
st.sidebar.header("⚙️ Yeni Kayıt İşlemleri")

# 1. Yeni Buzağı Ekleme
with st.sidebar.expander("🐄 Yeni Buzağı Ekle", expanded=False):
    with st.form("buzagi_formu", clear_on_submit=True):
        kupe_no = st.text_input("Küpe Numarası", placeholder="Örn: TR-002")
        dogum_tarihi = st.date_input("Doğum Tarihi", value=datetime.now())
        cinsiyet = st.selectbox("Cinsiyet", ["Dişi", "Erkek"])
        buzagi_kaydet = st.form_submit_button("Buzağıyı Sisteme Kaydet")
        
        if buzagi_kaydet and kupe_no:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO buzagilar (kupe_no, dogum_tarihi, cinsiyet) VALUES (?, ?, ?)",
                           (kupe_no, str(dogum_tarihi), cinsiyet))
            conn.commit()
            st.success(f"{kupe_no} başarıyla eklendi!")
            st.rerun()

# 2. Yeni Gider Ekleme
with st.sidebar.expander("💰 Yeni Gider Ekle", expanded=False):
    with st.form("gider_formu", clear_on_submit=True):
        gider_turu = st.text_input("Gider Türü", placeholder="Örn: Yem, İlaç")
        miktar = st.number_input("Miktar (KG / Adet)", min_value=0.0, step=1.0)
        tutar = st.number_input("Toplam Tutar (TL)", min_value=0.0, step=10.0)
        gider_tarihi = st.date_input("Gider Tarihi", value=datetime.now())
        gider_kaydet = st.form_submit_button("Gideri Kasaya İşle")
        
        if gider_kaydet and gider_turu and tutar > 0:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO yem_gider (gider_turu, miktar, tutar, tarih) VALUES (?, ?, ?, ?)",
                           (gider_turu, miktar, tutar, str(gider_tarihi)))
            conn.commit()
            st.success("Masraf kasaya işlendi!")
            st.rerun()

# 3. Yeni Aşı Planlama
with st.sidebar.expander("💉 Yeni Aşı Planla", expanded=False):
    with st.form("asi_formu", clear_on_submit=True):
        buzagilar_df = pd.read_sql_query("SELECT id, kupe_no FROM buzagilar", conn)
        
        if not buzagilar_df.empty:
            hayvan_secenekleri = buzagilar_df['id'].astype(str) + " - " + buzagilar_df['kupe_no']
            secilen_hayvan = st.selectbox("Hangi Buzağı?", hayvan_secenekleri)
            asi_adi = st.text_input("Aşı Adı (Örn: Şap, Karma)")
            asi_tarihi = st.date_input("Planlanan Aşı Tarihi", value=datetime.now())
            asi_kaydet = st.form_submit_button("Aşıyı Planla")
            
            if asi_kaydet and asi_adi:
                secilen_id = secilen_hayvan.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("INSERT INTO asi_takip (hayvan_id, asi_adi, planlanan_tarih) VALUES (?, ?, ?)",
                               (secilen_id, asi_adi, str(asi_tarihi)))
                conn.commit()
                st.success("Aşı başarıyla planlandı!")
                st.rerun()
        else:
            st.warning("Sistemde buzağı yok. Önce buzağı ekleyin.")
            st.form_submit_button("Aşıyı Planla", disabled=True)

# 4. Aşı Durumu Güncelleme
with st.sidebar.expander("✅ Aşı Durumu Güncelle", expanded=False):
    with st.form("asi_guncelle_formu", clear_on_submit=True):
        bekleyen_asilar = pd.read_sql_query("""
            SELECT asi_takip.id, buzagilar.kupe_no, asi_takip.asi_adi 
            FROM asi_takip 
            JOIN buzagilar ON asi_takip.hayvan_id = buzagilar.id
            WHERE asi_takip.durum = 'Yapılmadı'
        """, conn)
        
        if not bekleyen_asilar.empty:
            guncelleme_secenekleri = bekleyen_asilar['id'].astype(str) + " - " + bekleyen_asilar['kupe_no'] + " : " + bekleyen_asilar['asi_adi']
            secilen_guncelleme = st.selectbox("Yapılan Aşıyı Seç", guncelleme_secenekleri)
            guncelle_buton = st.form_submit_button("Aşıyı 'Yapıldı' Olarak İşaretle")
            
            if guncelle_buton and secilen_guncelleme:
                guncelle_id = secilen_guncelleme.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("UPDATE asi_takip SET durum = 'Yapıldı' WHERE id = ?", (guncelle_id,))
                conn.commit()
                st.success("Aşı durumu başarıyla güncellendi!")
                st.rerun()
        else:
            st.info("Şu an bekleyen aşınız bulunmuyor.")
            st.form_submit_button("Aşıyı 'Yapıldı' Olarak İşaretle", disabled=True)

# 5. YENİ: Hatalı Kayıt Silme (DELETE İşlemi)
with st.sidebar.expander("🗑️ Hatalı Gider Kaydını Sil", expanded=False):
    with st.form("silme_formu", clear_on_submit=True):
        # Tüm giderleri veritabanından çek
        tum_giderler = pd.read_sql_query("SELECT id, gider_turu, tutar FROM yem_gider", conn)
        
        if not tum_giderler.empty:
            # Kullanıcıya "1 - Buzağı Yemi (750 TL)" formatında gösteriyoruz
            silinecek_secenekler = tum_giderler['id'].astype(str) + " - " + tum_giderler['gider_turu'] + " (" + tum_giderler['tutar'].astype(str) + " TL)"
            secilen_silinecek = st.selectbox("Silinecek Harcamayı Seç", silinecek_secenekler)
            sil_buton = st.form_submit_button("🚨 Kaydı Kalıcı Olarak Sil")
            
            if sil_buton and secilen_silinecek:
                sil_id = secilen_silinecek.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("DELETE FROM yem_gider WHERE id = ?", (sil_id,))
                conn.commit()
                st.warning("Kayıt sistemden tamamen silindi!")
                st.rerun()
        else:
            st.info("Sistemde silinecek harcama kaydı yok.")
            st.form_submit_button("🚨 Kaydı Kalıcı Olarak Sil", disabled=True)

# --- ANA SAYFA / VERİ GÖSTERİMİ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🐄 Çiftlikteki Buzağılar")
    tablo_buzagi = pd.read_sql_query("SELECT * FROM buzagilar ORDER BY id DESC", conn)
    st.dataframe(tablo_buzagi, width='stretch')

with col2:
    st.subheader("💉 Aşı Takvimi")
    sorgu = """
    SELECT asi_takip.id, buzagilar.kupe_no, asi_takip.asi_adi, asi_takip.planlanan_tarih, asi_takip.durum 
    FROM asi_takip 
    JOIN buzagilar ON asi_takip.hayvan_id = buzagilar.id
    ORDER BY asi_takip.planlanan_tarih ASC
    """
    try:
        tablo_asi = pd.read_sql_query(sorgu, conn)
        st.dataframe(tablo_asi, width='stretch')
    except:
        st.info("Henüz planlanmış aşı yok.")

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("💰 Son Harcamalar")
    tablo_gider = pd.read_sql_query("SELECT * FROM yem_gider ORDER BY id DESC", conn)
    st.dataframe(tablo_gider, width='stretch')

with col4:
    st.subheader("📊 Finansal Özet")
    toplam_harcama = pd.read_sql_query("SELECT SUM(tutar) FROM yem_gider", conn).iloc[0, 0]
    if toplam_harcama is None: toplam_harcama = 0
    st.metric(label="Toplam Kasa Çıkışı", value=f"{toplam_harcama:,.2f} TL")

conn.close()