import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="Çiftlik 360", page_icon="🌾", layout="wide")

def veritabani_baglan_ve_guncelle():
    baglanti = sqlite3.connect('ciftlik.db')
    cursor = baglanti.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hayvanlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            kupe_no TEXT,
            cins TEXT,
            kullanici_adi TEXT
        )
    """)
    
    try: cursor.execute("ALTER TABLE kullanicilar ADD COLUMN gizli_soru TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE kullanicilar ADD COLUMN gizli_cevap TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE buzagilar ADD COLUMN isim TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE buzagilar ADD COLUMN cins TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE buzagilar ADD COLUMN anne_adi TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE buzagilar ADD COLUMN anne_kupe_no TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE buzagilar ADD COLUMN kullanici_adi TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE yem_gider ADD COLUMN kullanici_adi TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE asi_takip ADD COLUMN kullanici_adi TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE asi_takip ADD COLUMN hayvan_kupe TEXT")
    except: pass
        
    baglanti.commit()
    return baglanti

conn = veritabani_baglan_ve_guncelle()

# =========================================================================
# --- OTURUMU AÇIK TUTMA SİSTEMİ (URL KANCASI) ---
# =========================================================================
if 'kullanici' not in st.session_state:
    if 'oturum' in st.query_params:
        st.session_state['kullanici'] = st.query_params['oturum']
    else:
        st.session_state['kullanici'] = None

# --- GİRİŞ, KAYIT VE ŞİFRE YENİLEME PORTALI ---
if st.session_state['kullanici'] is None:
    st.title("🌾 Çiftlik 360 - Giriş Portalı")
    tab1, tab2, tab3 = st.tabs(["Giriş Yap", "Yeni Hesap Oluştur", "Şifremi Unuttum"])
    
    with tab1:
        st.subheader("Sisteme Giriş")
        with st.form("giris_formu"):
            giris_ad = st.text_input("Kullanıcı Adı", key="g_ad", placeholder="Kullanıcı adınızı girin...")
            giris_sifre = st.text_input("Şifre", type="password", key="g_sifre", placeholder="Şifrenizi girin...")
            giris_buton = st.form_submit_button("Giriş Yap")
            
            if giris_buton:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (giris_ad, giris_sifre))
                if cursor.fetchone():
                    st.session_state['kullanici'] = giris_ad
                    st.query_params['oturum'] = giris_ad
                    st.success(f"Hoş geldin {giris_ad}! İçeri alınıyorsun...")
                    st.rerun()
                else: 
                    st.error("Kullanıcı adı veya şifre hatalı!")
                
    with tab2:
        st.subheader("Aramıza Katıl")
        with st.form("kayit_formu", clear_on_submit=True):
            kayit_ad = st.text_input("Belirlediğiniz Kullanıcı Adı", key="k_ad", placeholder="Yeni bir kullanıcı adı belirleyin...")
            kayit_sifre = st.text_input("Belirlediğiniz Şifre", type="password", key="k_sifre", placeholder="Yeni bir şifre belirleyin...")
            st.markdown("---")
            st.write("**Şifre Yenileme Güvenliği**")
            soru_secenekleri = ["İlk evcil hayvanınızın adı?", "İlkokul öğretmeninizin adı?", "En sevdiğiniz yemek?", "✍️ Kendi sorumu yazmak istiyorum..."]
            secilen_soru = st.selectbox("Bir Gizli Soru Seçin", soru_secenekleri)
            if secilen_soru == "✍️ Kendi sorumu yazmak istiyorum...":
                gizli_soru = st.text_input("Kendi Gizli Sorunuzu Yazın", key="k_ozel_soru", placeholder="Örn: En sevdiğim renk nedir?")
            else: 
                gizli_soru = secilen_soru
                
            gizli_cevap = st.text_input("Gizli Cevabınız", key="k_cevap", placeholder="Cevabınızı girin...")
            kayit_buton = st.form_submit_button("Kayıt Ol")
            
            if kayit_buton:
                if kayit_ad and kayit_sifre and gizli_soru and gizli_cevap:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, gizli_soru, gizli_cevap) VALUES (?, ?, ?, ?)", 
                                       (kayit_ad, kayit_sifre, gizli_soru, gizli_cevap))
                        conn.commit()
                        st.success("Hesabın başarıyla açıldı! Giriş yapabilirsin.")
                    except sqlite3.IntegrityError: 
                        st.error("Bu kullanıcı adı alınmış!")
                else: 
                    st.warning("Lütfen tüm alanları doldurun!")
                
    with tab3:
        st.subheader("Şifreni mi Unuttun?")
        unutulan_ad = st.text_input("Kullanıcı Adınızı Girin", key="u_ad", placeholder="Hesabınızın kullanıcı adını yazın...")
        if unutulan_ad:
            cursor = conn.cursor()
            cursor.execute("SELECT gizli_soru, gizli_cevap FROM kullanicilar WHERE kullanici_adi=?", (unutulan_ad,))
            kullanici_bilgisi = cursor.fetchone()
            if kullanici_bilgisi and kullanici_bilgisi[0]:
                st.info(f"**Güvenlik Sorunuz:** {kullanici_bilgisi[0]}")
                with st.form("sifre_yenileme_formu"):
                    girilen_cevap = st.text_input("Cevabınızı Girin", key="u_cevap", placeholder="Güvenlik cevabınız...")
                    yeni_sifre = st.text_input("Yeni Şifrenizi Belirleyin", type="password", key="u_yeni_sifre", placeholder="Yeni şifreniz...")
                    yenile_buton = st.form_submit_button("Şifremi Yenile")
                    
                    if yenile_buton:
                        if girilen_cevap.lower() == kullanici_bilgisi[1].lower():
                            cursor.execute("UPDATE kullanicilar SET sifre=? WHERE kullanici_adi=?", (yeni_sifre, unutulan_ad))
                            conn.commit()
                            st.success("Şifreniz yenilendi! Giriş yapabilirsiniz.")
                        else: 
                            st.error("Gizli cevap yanlış!")
            else: 
                st.warning("Kullanıcı bulunamadı veya gizli sorusu yok.")
    st.stop()

# --- SİSTEME GİRİŞ YAPILDIYSA BURASI ÇALIŞIR ---
aktif_kullanici = st.session_state['kullanici']

st.sidebar.title(f"👤 {aktif_kullanici}")
secili_sayfa = st.sidebar.radio("📌 Menü", ["🏠 Ana Panel", "📊 Raporlar ve Grafikler"])
st.sidebar.markdown("---")

if st.sidebar.button("Çıkış Yap"):
    st.session_state['kullanici'] = None
    if 'oturum' in st.query_params:
        del st.query_params['oturum']
    st.rerun()

st.sidebar.header("⚙️ Yeni Kayıt İşlemleri")

with st.sidebar.expander("🐄 Yeni Yetişkin Hayvan Ekle", expanded=False):
    with st.form("yetiskin_formu", clear_on_submit=True):
        h_isim = st.text_input("Hayvanın Adı / Lakabı")
        h_kupe = st.text_input("Küpe Numarası")
        h_cins = st.selectbox("Cinsi / Irkı", ["Holstein", "Simental", "Montofon", "Yerli Kara", "Diğer"])
        if st.form_submit_button("Kaydet") and h_kupe:
            conn.cursor().execute("INSERT INTO hayvanlar (isim, kupe_no, cins, kullanici_adi) VALUES (?, ?, ?, ?)", (h_isim, h_kupe, h_cins, aktif_kullanici))
            conn.commit()
            st.success("Kaydedildi!")
            st.rerun()

with st.sidebar.expander("👶 Yeni Buzağı Ekle", expanded=False):
    with st.form("buzagi_formu", clear_on_submit=True):
        b_isim = st.text_input("Buzağının Adı")
        b_kupe = st.text_input("Buzağı Küpe Numarası")
        b_dogum = st.date_input("Doğum Tarihi", value=datetime.now())
        b_cinsiyet = st.selectbox("Cinsiyet", ["Dişi", "Erkek"])
        b_cins = st.selectbox("Cinsi / Irkı", ["Holstein", "Simental", "Montofon", "Melez", "Diğer"])
        
        hayvanlar_df = pd.read_sql_query(f"SELECT isim, kupe_no FROM hayvanlar WHERE kullanici_adi='{aktif_kullanici}'", conn)
        if not hayvanlar_df.empty:
            anne_secenekleri = ["Seçiniz..."] + (hayvanlar_df['isim'] + " (" + hayvanlar_df['kupe_no'] + ")").tolist() + ["Elle Gir..."]
            secilen_anne = st.selectbox("Annesi Kim?", anne_secenekleri)
        else: secilen_anne = "Elle Gir..."
            
        if secilen_anne == "Elle Gir...":
            b_anne_adi = st.text_input("Anne Adı")
            b_anne_kupe = st.text_input("Anne Küpe No")
        elif secilen_anne != "Seçiniz...":
            b_anne_adi = secilen_anne.split(" (")[0]
            b_anne_kupe = secilen_anne.split(" (")[1].replace(")", "")
        else: b_anne_adi, b_anne_kupe = "", ""

        if st.form_submit_button("Kaydet") and b_kupe:
            conn.cursor().execute("INSERT INTO buzagilar (isim, kupe_no, dogum_tarihi, cinsiyet, cins, anne_adi, anne_kupe_no, kullanici_adi) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (b_isim, b_kupe, str(b_dogum), b_cinsiyet, b_cins, b_anne_adi, b_anne_kupe, aktif_kullanici))
            conn.commit()
            st.success("Kaydedildi!")
            st.rerun()

with st.sidebar.expander("💰 Yeni Gider Ekle", expanded=False):
    with st.form("gider_formu", clear_on_submit=True):
        gider_turu = st.text_input("Gider Türü", placeholder="Örn: Yem, İlaç, Veteriner...")
        gider_miktari = st.number_input("Miktar / Adet", min_value=0.0, value=None, step=1.0)
        birim_fiyat = st.number_input("Birim Fiyatı (TL)", min_value=0.0, value=None, step=10.0)
        
        toplam_hesaplanan = (gider_miktari * birim_fiyat) if (gider_miktari is not None and birim_fiyat is not None) else 0.0
        st.info(f"💵 Tutar: {toplam_hesaplanan:,.2f} TL")
        gider_tarihi = st.date_input("Gider Tarihi", value=datetime.now())
        
        if st.form_submit_button("Kasaya İşle") and gider_turu and toplam_hesaplanan > 0:
            conn.cursor().execute("INSERT INTO yem_gider (gider_turu, miktar, tutar, tarih, kullanici_adi) VALUES (?, ?, ?, ?, ?)", (gider_turu, gider_miktari, toplam_hesaplanan, str(gider_tarihi), aktif_kullanici))
            conn.commit()
            st.success("Kasaya işlendi!")
            st.rerun()

with st.sidebar.expander("💉 Yeni Aşı Planla", expanded=False):
    with st.form("asi_formu", clear_on_submit=True):
        yetiskin_df = pd.read_sql_query(f"SELECT isim, kupe_no FROM hayvanlar WHERE kullanici_adi='{aktif_kullanici}'", conn)
        buz_df = pd.read_sql_query(f"SELECT isim, kupe_no FROM buzagilar WHERE kullanici_adi='{aktif_kullanici}'", conn)
        tuml_liste = [f"🐄 {r['isim']} ({r['kupe_no']})" for _, r in yetiskin_df.iterrows()] + [f"👶 {r['isim']} ({r['kupe_no']})" for _, r in buz_df.iterrows()]
        
        if tuml_liste:
            secilen_asi_hayvan = st.selectbox("Hangi Hayvan?", tuml_liste)
            asi_adi = st.text_input("Aşı Adı")
            asi_tarihi = st.date_input("Planlanan Aşı Tarihi", value=datetime.now())
            if st.form_submit_button("Aşıyı Planla") and asi_adi:
                h_kupe_ayrik = secilen_asi_hayvan.split("(")[1].replace(")", "")
                conn.cursor().execute("INSERT INTO asi_takip (hayvan_kupe, asi_adi, planlanan_tarih, kullanici_adi, durum) VALUES (?, ?, ?, ?, 'Yapılmadı')", (h_kupe_ayrik, asi_adi, str(asi_tarihi), aktif_kullanici))
                conn.commit()
                st.success("Aşı eklendi!")
                st.rerun()
        else: st.warning("Hayvan bulunmuyor.")

with st.sidebar.expander("✅ Aşı / 🗑️ Kayıt Sil", expanded=False):
    with st.form("islem_formu", clear_on_submit=True):
        st.write("**Aşı Durumu Güncelle**")
        bekleyen_asilar = pd.read_sql_query(f"SELECT id, hayvan_kupe, asi_adi FROM asi_takip WHERE durum = 'Yapılmadı' AND kullanici_adi = '{aktif_kullanici}'", conn)
        if not bekleyen_asilar.empty:
            guncelleme_secenekleri = bekleyen_asilar['id'].astype(str) + " - " + bekleyen_asilar['hayvan_kupe'] + " [" + bekleyen_asilar['asi_adi'] + "]"
            secilen_guncelleme = st.selectbox("Yapılan Aşıyı Seç", guncelleme_secenekleri)
            if st.form_submit_button("Aşıyı 'Yapıldı' Yap"):
                conn.cursor().execute("UPDATE asi_takip SET durum = 'Yapıldı' WHERE id = ? AND kullanici_adi = ?", (secilen_guncelleme.split(" - ")[0], aktif_kullanici))
                conn.commit()
                st.success("Güncellendi!")
                st.rerun()
                
        st.markdown("---")
        st.write("**Hatalı Gideri Sil**")
        tum_giderler = pd.read_sql_query(f"SELECT id, gider_turu, tutar FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}'", conn)
        if not tum_giderler.empty:
            silinecek_secenekler = tum_giderler['id'].astype(str) + " - " + tum_giderler['gider_turu'] + " (" + tum_giderler['tutar'].astype(str) + " TL)"
            secilen_silinecek = st.selectbox("Harcamayı Seç", silinecek_secenekler)
            if st.form_submit_button("🚨 Kaydı Sil"):
                conn.cursor().execute("DELETE FROM yem_gider WHERE id = ? AND kullanici_adi = ?", (secilen_silinecek.split(" - ")[0], aktif_kullanici))
                conn.commit()
                st.warning("Silindi!")
                st.rerun()


# =========================================================================
# --- SAYFA 1: ANA PANEL (Sadece Bu Ayın Verileri) ---
# =========================================================================
if secili_sayfa == "🏠 Ana Panel":
    st.title("🌾 Çiftlik 360 Yönetim Paneli")
    st.write(f"Hoş geldin patron **{aktif_kullanici}**! Çiftliğini buradan uçtan uca yönetebilirsin.")
    
    st.header("📋 Hayvanlarım (Tüm Çiftlik Kontrol Paneli)")
    tab_yetiskinler, tab_buzagilar = st.tabs(["🐄 Yetişkin Hayvanlar (Anaçlar/Boğalar)", "👶 Buzağılar / Yavrular"])

    with tab_yetiskinler:
        tablo_yetiskin = pd.read_sql_query(f"SELECT isim AS 'Hayvan Adı', kupe_no AS 'Küpe Numarası', cins AS 'Cinsi / Irkı' FROM hayvanlar WHERE kullanici_adi = '{aktif_kullanici}' ORDER BY id DESC", conn)
        if not tablo_yetiskin.empty: st.dataframe(tablo_yetiskin, use_container_width=True, hide_index=True)
        else: st.info("Yetişkin hayvan kaydı yok.")

    with tab_buzagilar:
        tablo_buzagi = pd.read_sql_query(f"SELECT isim AS 'Buzağı Adı', kupe_no AS 'Küpe Numarası', dogum_tarihi AS 'Doğum Tarihi', cinsiyet AS 'Cinsiyet', cins AS 'Cinsi', anne_adi AS 'Anne Adı' FROM buzagilar WHERE kullanici_adi = '{aktif_kullanici}' ORDER BY id DESC", conn)
        if not tablo_buzagi.empty: st.dataframe(tablo_buzagi, use_container_width=True, hide_index=True)
        else: st.info("Buzağı kaydı yok.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💉 Yaklaşan / Yapılan Aşılar")
        tablo_asi = pd.read_sql_query(f"SELECT hayvan_kupe AS 'Küpe No', asi_adi AS 'Aşı Adı', planlanan_tarih AS 'Tarih', durum AS 'Durum' FROM asi_takip WHERE kullanici_adi = '{aktif_kullanici}' ORDER BY planlanan_tarih ASC", conn)
        if not tablo_asi.empty: st.dataframe(tablo_asi, use_container_width=True, hide_index=True)
        else: st.info("Planlanmış aşı yok.")

    with col2:
        bu_ay_str = datetime.now().strftime('%Y-%m') 
        st.subheader("💰 Bu Ayki Harcamalar (Aktif Ay)")
        
        tablo_gider_bu_ay = pd.read_sql_query(f"SELECT gider_turu AS 'Tür', miktar AS 'Miktar', tutar AS 'Tutar (TL)', tarih AS 'Tarih' FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}' AND tarih LIKE '{bu_ay_str}-%' ORDER BY tarih DESC", conn)
        if not tablo_gider_bu_ay.empty: 
            st.dataframe(tablo_gider_bu_ay, use_container_width=True, hide_index=True)
            bu_ay_toplam = tablo_gider_bu_ay['Tutar (TL)'].sum()
        else: 
            st.info("Bu ay henüz hiç harcama girmediniz.")
            bu_ay_toplam = 0.0
            
        st.metric(label="Bu Ayın Toplam Kasa Çıkışı", value=f"{bu_ay_toplam:,.2f} TL")


# =========================================================================
# --- SAYFA 2: RAPORLAR VE GRAFİKLER ---
# =========================================================================
elif secili_sayfa == "📊 Raporlar ve Grafikler":
    st.title("📊 Finansal Raporlar ve Arşiv")
    st.write("Geçmiş aylardaki harcama trendlerinizi ve kategorik giderlerinizi buradan analiz edebilirsiniz.")
    
    tum_giderler = pd.read_sql_query(f"SELECT gider_turu, tutar, tarih FROM yem_gider WHERE kullanici_adi = '{aktif_kullanici}'", conn)
    
    if not tum_giderler.empty:
        tum_giderler['tarih'] = pd.to_datetime(tum_giderler['tarih'])
        tum_giderler['Ay_Yil'] = tum_giderler['tarih'].dt.strftime('%Y-%m') 
        
        mevcut_aylar = sorted(tum_giderler['Ay_Yil'].unique(), reverse=True)
        
        col_secim, col_bos = st.columns([1, 2])
        with col_secim:
            secilen_donem = st.selectbox("🗓️ İncelemek İstediğiniz Dönemi Seçin", mevcut_aylar)
            
        st.markdown("---")
        
        secilen_ay_verisi = tum_giderler[tum_giderler['Ay_Yil'] == secilen_donem]
        aylik_toplam = secilen_ay_verisi['tutar'].sum()
        
        st.subheader(f"📈 {secilen_donem} Dönemi Harcama Analizi")
        st.metric(label=f"Seçilen Ayın Toplam Gideri", value=f"{aylik_toplam:,.2f} TL")
        
        grafik_verisi = secilen_ay_verisi.groupby('gider_turu')['tutar'].sum().reset_index()
        
        st.write("**Kategorilere Göre Harcama Dağılımı (Pasta Grafik)**")
        
        fig = px.pie(
            grafik_verisi, 
            values='tutar', 
            names='gider_turu', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # GÜNCELLEME: 'texttemplate' kullanarak dilimlerin içerisine isim, yüzde ve binlik ayrılmış net TL miktarını bastık
        fig.update_traces(
            textposition='inside', 
            texttemplate='<b>%{label}</b><br>%{percent}<br>%{value:,.2f} TL'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Sistemde raporlanacak hiçbir finansal geçmiş bulunmuyor.")

conn.close()