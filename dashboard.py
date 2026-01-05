import streamlit as st
import httpx
import pandas as pd

st.set_page_config(page_title="Aktüeryal Karar Destek Sistemi", layout="wide")

st.title("🛡️ Emre Orman - IFRS 17 Aktüeryal Dashboard")
st.sidebar.header("Parametreler")

# Kullanıcı Girişleri
police = st.sidebar.number_input("Poliçe Sayısı", value=5000)
olasilik = st.sidebar.slider("Kaza Olasılığı", 0.0, 1.0, 0.08)
ortalama_h = st.sidebar.number_input("Ortalama Hasar (TL)", value=65000)
faiz = st.sidebar.slider("Yıllık Faiz", 0.0, 1.0, 0.45)

if st.sidebar.button("Hesapla ve Kaydet"):
    # Backend API'ye istek at (FastAPI'nin çalıştığından emin ol)
    with httpx.Client() as client:
        response = client.post("http://127.0.0.1:8000/ifrs17/tam-rapor", json={
            "police_sayisi": police,
            "kaza_olasiligi": olasilik,
            "ortalama_hasar": ortalama_h,
            "yillik_faiz": faiz,
            "vade_ay": 12
        })
        
        if response.status_code == 200:
            res = response.json()
            
            # Kartlarla özet gösterimi
            col1, col2, col3 = st.columns(3)
            col1.metric("Beklenen Kaza", res['analiz_ozeti']['toplam_kaza_sayisi'])
            col2.metric("İskontolu Karşılık (PV)", f"{res['finansal_sonuc']['ayrilmasi_gereken_karsilik_PV']:,} TL")
            col3.metric("İskonto Tasarrufu", f"{res['finansal_sonuc']['iskonto_tasarrufu']:,} TL")
            
            st.success(res['mesaj'])
        else:
            st.error("Backend API'ye bağlanılamadı. Lütfen uvicorn'un çalıştığından emin olun.")

st.divider()
st.subheader("📊 Geçmiş Analizler")

# Geçmiş verileri API'den çekip tablo olarak göster
if st.button("Verileri Yenile"):
    with httpx.Client() as client:
        history = client.get("http://127.0.0.1:8000/raporlar/gecmis")
        if history.status_code == 200:
            df = pd.DataFrame(history.json())
            st.table(df)

st.divider()
st.subheader("📉 Karşılık Trend Grafiği")
st.image("http://127.0.0.1:8000/analiz/grafik") # Daha önce yazdığın grafik endpoint'ini çağırır