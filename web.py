import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Çiftlik 360", page_icon="🌾", layout="wide")

def veritabani_baglan_ve_guncelle():
    baglanti = sqlite3.connect('ciftlik.db')
    cursor = baglanti.cursor()
    
    try:
        cursor.execute("ALTER TABLE kullanicilar ADD COLUMN gizli_soru TEXT")
        cursor.execute("ALTER TABLE kullanicilar ADD COLUMN gizli_cevap TEXT")
    except:
        pass 
        
    try:
        cursor.execute("ALTER TABLE buzagilar ADD COLUMN kullanici_adi TEXT")
        cursor.execute("ALTER TABLE yem_gider ADD COLUMN kullanici_adi TEXT")
        cursor.execute("ALTER TABLE asi_takip ADD COLUMN kullanici_adi TEXT")
    except:
        pass 
        
    baglanti.commit()
    return baglanti

conn = veritabani_baglan_ve_guncelle()

# --- ZİYARETÇİ KARTI (SESSION) TANIMLAMA ---
if 'kullanici' not in st.session_state:
    st.session_state['kullanici'] = None

# --- PROFESYONEL GİRİŞ, KAYIT VE ŞİFRE YENİLEME PORTALI ---
if st.session_state['kullanici'] is None:
    st.title("🌾 Çiftlik 360 - Giriş Portalı")
    
    tab1, tab2, tab3 = st.tabs(["Giriş Yap", "Yeni Hesap Oluştur", "Şifremi Unuttum"])
    
    with tab1:
        st.subheader("Sisteme Giriş")
        giris_ad = st.text_input("Kullanıcı Adı", key="g_ad")
        giris_sifre = st.text_input("Şifre", type="password", key="g_sifre")
        
        if st.button("Giriş Yap", key="giris_btn"):
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (giris_ad, giris_sifre))
            sonuc = cursor.fetchone()
            
            if sonuc:
                st.session_state['kullanici'] = giris_ad
                st.success(f"Hoş geldin {giris_ad}! İçeri alınıyorsun...")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı! Tekrar dene.")
                
    with tab2:
        st.subheader("Aramıza Katıl")
        kayit_ad = st.text_input("Belirlediğiniz Kullanıcı Adı", key="k_ad")
        kayit_sifre = st.text_input("Belirlediğiniz Şifre", type="password", key="k_sifre")
        
        st.markdown("---")
        st.write("**Şifre Yenileme Güvenliği**")
        
        # YENİ: Kullanıcının kendi sorusunu yazabilme özelliği eklendi
        soru_secenekleri = [
            "İlk evcil hayvanınızın adı?", 
            "İlkokul öğretmeninizin adı?", 
            "En sevdiğiniz yemek?", 
            "Çocukluk lakabınız nedir?",
            "✍️ Kendi sorumu yazmak istiyorum..."
        ]
        secilen_soru = st.selectbox("Bir Gizli Soru Seçin", soru_secenekleri)
        
        # Eğer "Kendi sorumu yazmak istiyorum" seçilirse altta yeni bir kutu açılır
        if secilen_soru == "✍️ Kendi sorumu yazmak istiyorum...":
            gizli_soru = st.text_input("Kendi Gizli Sorunuzu Yazın", placeholder="Örn: En sevdiğim araba modeli?", key="k_ozel_soru")
        else:
            gizli_soru = secilen_soru
            
        gizli_cevap = st.text_input("Gizli Cevabınız (Bunu asla unutmayın!)", key="k_cevap")
        
        if st.button("Kayıt Ol", key="kayit_btn"):
            if kayit_ad and kayit_sifre and gizli_soru and gizli_cevap:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, gizli_soru, gizli_cevap) VALUES (?, ?, ?, ?)", 
                                   (kayit_ad, kayit_sifre, gizli_soru, gizli_cevap))
                    conn.commit()
                    st.success("Hesabın başarıyla açıldı! 'Giriş Yap' sekmesinden girebilirsin.")
                except sqlite3.IntegrityError:
                    st.error("Bu kullanıcı adı alınmış kral, başka bir tane dene.")
            else:
                st.warning("Lütfen tüm alanları (Gizli soru ve cevap dahil) doldurun!")
                
    with tab3:
        st.subheader("Şifreni mi Unuttun?")
        unutulan_ad = st.text_input("Kullanıcı Adınızı Girin", key="u_ad")
        
        if unutulan_ad:
            cursor = conn.cursor()
            cursor.execute("SELECT gizli_soru, gizli_cevap FROM kullanicilar WHERE kullanici_adi=?", (unutulan_ad,))
            kullanici_bilgisi = cursor.fetchone()
            
            if kullanici_bilgisi:
                kayitli_soru = kullanici_bilgisi[0]
                kayitli_cevap = kullanici_bilgisi[1]
                
                if kayitli_soru is None:
                    st.error("Bu hesabın gizli sorusu ayarlanmamış. Lütfen yöneticiye başvurun.")
                else:
                    st.info(f"**Güvenlik Sorunuz:** {kayitli_soru}")
                    girilen_cevap = st.text_input("Cevabınızı Girin", key="u_cevap")
                    yeni_sifre = st.text_input("Yeni Şifrenizi Belirleyin", type="password", key="u_yeni_sifre")
                    
                    if st.button("Şifremi Yenile"):
                        if girilen_cevap.lower() == kayitli_cevap.lower(): 
                            cursor.execute("UPDATE kullanicilar SET sifre=? WHERE kullanici_adi=?", (yeni_sifre, unutulan_ad))
                            conn.commit()
                            st.success("Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz.")
                        else:
                            st.error("Gizli cevabınız yanlış! Şifre sıfırlanamadı.")
            else:
                st.warning("Böyle bir kullanıcı adı sistemde bulunamadı.")
                
    st.stop() 

# KULLANICI GİRİŞ YAPTIYSA GÖRECEĞİ YAN MENÜ (ÇIKIŞ BUTONU)
st.sidebar.title(f"👤 {st.session_state['kullanici']}")
if st.sidebar.button("Çıkış Yap"):
    st.session_state['kullanici'] = None
    st.rerun()

aktif_kullanici = st.session_state['kullanici']

# =========================================================================
# BURADAN AŞAĞISI SENİN MEVCUT ÇİFTLİK KODLARIN (DOKUNMA)
# =========================================================================

# BURADAN AŞAĞISI SENİN MEVCUT ÇİFTLİK KODLARIN...

# =========================================================================
# BURADAN AŞAĞISI ASIL ÇİFTLİK KODLARIN (KİŞİYE ÖZEL HALE GETİRİLDİ)
# =========================================================================

# Sayfa Yapılandırması
st.set_page_config(page_title="Çiftlik 360", page_icon="🌾", layout="wide")
st.title("🌾 Çiftlik 360 Yönetim Paneli")
st.write("Sisteme hoş geldin patron! Çiftliğini buradan uçtan uca yönetebilirsin.")

# Giriş yapan kişinin adını bir değişkene sabitliyoruz
aktif_kullanici = st.session_state['kullanici']

def veritabani_baglan_ve_guncelle():
    baglanti = sqlite3.connect('ciftlik.db')
    cursor = baglanti.cursor()
    # Eski tablolara otomatik olarak 'kullanici_adi' sütunu ekleyen kilit mekanizma
    try:
        cursor.execute("ALTER TABLE buzagilar ADD COLUMN kullanici_adi TEXT")
        cursor.execute("ALTER TABLE yem_gider ADD COLUMN kullanici_adi TEXT")
        cursor.execute("ALTER TABLE asi_takip ADD COLUMN kullanici_adi TEXT")
        baglanti.commit()
    except:
        pass # Sütunlar zaten varsa sessizce devam eder
    return baglanti

conn = veritabani_baglan_ve_guncelle()

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
            # Ekleme yaparken aktif kullanıcının adını da (sahibini) kaydediyoruz
            cursor.execute("INSERT INTO buzagilar (kupe_no, dogum_tarihi, cinsiyet, kullanici_adi) VALUES (?, ?, ?, ?)",
                           (kupe_no, str(dogum_tarihi), cinsiyet, aktif_kullanici))
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
            cursor.execute("INSERT INTO yem_gider (gider_turu, miktar, tutar, tarih, kullanici_adi) VALUES (?, ?, ?, ?, ?)",
                           (gider_turu, miktar, tutar, str(gider_tarihi), aktif_kullanici))
            conn.commit()
            st.success("Masraf kasaya işlendi!")
            st.rerun()

# 3. Yeni Aşı Planlama
with st.sidebar.expander("💉 Yeni Aşı Planla", expanded=False):
    with st.form("asi_formu", clear_on_submit=True):
        # Sadece bu kişinin buzağılarını getir
        buzagilar_df = pd.read_sql_query(f"SELECT id, kupe_no FROM buzagilar WHERE kullanici_adi='{aktif_kullanici}'", conn)
        
        if not buzagilar_df.empty:
            hayvan_secenekleri = buzagilar_df['id'].astype(str) + " - " + buzagilar_df['kupe_no']
            secilen_hayvan = st.selectbox("Hangi Buzağı?", hayvan_secenekleri)
            asi_adi = st.text_input("Aşı Adı (Örn: Şap, Karma)")
            asi_tarihi = st.date_input("Planlanan Aşı Tarihi", value=datetime.now())
            asi_kaydet = st.form_submit_button("Aşıyı Planla")
            
            if asi_kaydet and asi_adi:
                secilen_id = secilen_hayvan.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("INSERT INTO asi_takip (hayvan_id, asi_adi, planlanan_tarih, kullanici_adi) VALUES (?, ?, ?, ?)",
                               (secilen_id, asi_adi, str(asi_tarihi), aktif_kullanici))
                conn.commit()
                st.success("Aşı başarıyla planlandı!")
                st.rerun()
        else:
            st.warning("Sistemde sana ait buzağı yok. Önce buzağı ekle.")
            st.form_submit_button("Aşıyı Planla", disabled=True)

# 4. Aşı Durumu Güncelleme
with st.sidebar.expander("✅ Aşı Durumu Güncelle", expanded=False):
    with st.form("asi_guncelle_formu", clear_on_submit=True):
        # Sadece bu kişiye ait bekleyen aşıları getir
        bekleyen_asilar = pd.read_sql_query(f"""
            SELECT asi_takip.id, buzagilar.kupe_no, asi_takip.asi_adi 
            FROM asi_takip 
            JOIN buzagilar ON asi_takip.hayvan_id = buzagilar.id
            WHERE asi_takip.durum = 'Yapılmadı' AND asi_takip.kullanici_adi = '{aktif_kullanici}'
        """, conn)
        
        if not bekleyen_asilar.empty:
            guncelleme_secenekleri = bekleyen_asilar['id'].astype(str) + " - " + bekleyen_asilar['kupe_no'] + " : " + bekleyen_asilar['asi_adi']
            secilen_guncelleme = st.selectbox("Yapılan Aşıyı Seç", guncelleme_secenekleri)
            guncelle_buton = st.form_submit_button("Aşıyı 'Yapıldı' Olarak İşaretle")
            
            if guncelle_buton and secilen_guncelleme:
                guncelle_id = secilen_guncelleme.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("UPDATE asi_takip SET durum = 'Yapıldı' WHERE id = ? AND kullanici_adi = ?", (guncelle_id, aktif_kullanici))
                conn.commit()
                st.success("Aşı durumu başarıyla güncellendi!")
                st.rerun()
        else:
            st.info("Şu an bekleyen aşınız bulunmuyor.")
            st.form_submit_button("Aşıyı 'Yapıldı' Olarak İşaretle", disabled=True)

# 5. YENİ: Hatalı Kayıt Silme (DELETE İşlemi)
with st.sidebar.expander("🗑️ Hatalı Gider Kaydını Sil", expanded=False):
    with st.form("silme_formu", clear_on_submit=True):
        # Sadece bu kişiye ait giderleri getir
        tum_giderler = pd.read_sql_query(f"SELECT id, gider_turu, tutar FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}'", conn)
        
        if not tum_giderler.empty:
            silinecek_secenekler = tum_giderler['id'].astype(str) + " - " + tum_giderler['gider_turu'] + " (" + tum_giderler['tutar'].astype(str) + " TL)"
            secilen_silinecek = st.selectbox("Silinecek Harcamayı Seç", silinecek_secenekler)
            sil_buton = st.form_submit_button("🚨 Kaydı Kalıcı Olarak Sil")
            
            if sil_buton and secilen_silinecek:
                sil_id = secilen_silinecek.split(" - ")[0]
                cursor = conn.cursor()
                cursor.execute("DELETE FROM yem_gider WHERE id = ? AND kullanici_adi = ?", (sil_id, aktif_kullanici))
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
    # Sadece giriş yapan kullanıcının buzağıları listelenir
    tablo_buzagi = pd.read_sql_query(f"SELECT id, kupe_no, dogum_tarihi, cinsiyet FROM buzagilar WHERE kullanici_adi = '{aktif_kullanici}' ORDER BY id DESC", conn)
    st.dataframe(tablo_buzagi, width='stretch')

with col2:
    st.subheader("💉 Aşı Takvimi")
    sorgu = f"""
    SELECT asi_takip.id, buzagilar.kupe_no, asi_takip.asi_adi, asi_takip.planlanan_tarih, asi_takip.durum 
    FROM asi_takip 
    JOIN buzagilar ON asi_takip.hayvan_id = buzagilar.id
    WHERE asi_takip.kullanici_adi = '{aktif_kullanici}'
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
    tablo_gider = pd.read_sql_query(f"SELECT id, gider_turu, miktar, tutar, tarih FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}' ORDER BY id DESC", conn)
    st.dataframe(tablo_gider, width='stretch')

with col4:
    st.subheader("📊 Finansal Özet")
    toplam_harcama = pd.read_sql_query(f"SELECT SUM(tutar) FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}'", conn).iloc[0, 0]
    if pd.isna(toplam_harcama) or toplam_harcama is None: 
        toplam_harcama = 0
    st.metric(label="Toplam Kasa Çıkışı", value=f"{toplam_harcama:,.2f} TL")

conn.close()