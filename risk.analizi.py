import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

# --- 1. AYARLAR VE VERİ YÜKLEME ---
def setup_page():
    st.set_page_config(page_title="Aktüer Dashboard V2", layout="wide")
    st.title("🛡️ Stratejik Risk Yönetim Paneli")

def load_data():
    file_path = 'risk_verisi.csv'
    try:
        df = pd.read_csv(file_path)
        
        # 1. Adım: Beklenen tüm sayısal sütunların varlığından emin ol
        cols_to_fix = ['Yas', 'Gelir', 'Risk_Skoru']
        
        for col in cols_to_fix:
            # Sütun yoksa hata vermek yerine varsayılan değerlerle oluştur
            if col not in df.columns:
                df[col] = 0.0 
            
            # Sayıya çevir, metinleri NaN yap
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 2. Adım: NaN (Boş) değerleri temizle (En kritik kısım burası)
            # Sayısal sütunlardaki boşlukları o sütunun ortalamasıyla doldur
            if df[col].isnull().any():
                mean_value = df[col].mean()
                # Eğer tüm sütun boşsa mean_value NaN çıkar, o zaman 0 bas
                df[col] = df[col].fillna(mean_value if pd.notnull(mean_value) else 0)
        
        # 3. Adım: Hedef değişken (Churn) kontrolü
        if 'Churn' not in df.columns or df['Churn'].isnull().any():
            # Churn yoksa veya boşsa basit bir kurala göre doldur (Eğitim için şart)
            df['Churn'] = (df['Risk_Skoru'] > 0.6).astype(int)
            
        return df
    
    except Exception as e:
        st.error(f"⚠️ Veri yüklenirken hata oluştu: {e}")
        st.stop()
# --- 2. MODEL EĞİTİMİ (GÜNCEL SÜTUNLARLA) ---
def train_model(df):
    # CSV'deki yeni sütun isimlerine göre eğitim yapalım
    # Özellikler: Yaş, Gelir, Risk_Skoru
    X = df[['Yas', 'Gelir', 'Risk_Skoru']]
    y = df['Churn']
    model = LogisticRegression().fit(X, y)
    return model

# --- 3. ANA UYGULAMA DÖNGÜSÜ (GÜNCEL) ---
def main():
    setup_page()
    df = load_data()
    model = train_model(df)

    # Üst Kısım: Genel Şirket Özeti (Yöneticiler bunu sever)
    total_customers = len(df)
    avg_risk = df['Risk_Skoru'].mean()
    
    st.columns(3)[0].metric("Toplam Müşteri", total_customers)
    st.columns(3)[1].metric("Ortalama Risk Skoru", f"{round(avg_risk*100, 1)}%")
    st.columns(3)[2].metric("Veri Kalitesi", "Yüksek" if not df.isnull().values.any() else "Düşük")
    
    st.divider()

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.header("🔍 Risk & Kayıp Tahmini")
        yas = st.slider("Müşteri Yaşı", 18, 90, 35)
        gelir = st.number_input("Yıllık Gelir (TL)", 20000, 2000000, 100000)
        risk_skoru = st.slider("Mevcut Risk Skoru (0-1)", 0.0, 1.0, 0.3)
        
        # ML Tahmini (PD - Probability of Default/Churn)
        input_data = pd.DataFrame([[yas, gelir, risk_skoru]], 
                                  columns=['Yas', 'Gelir', 'Risk_Skoru'])
        prob = model.predict_proba(input_data)[0][1]
        
        # Aktüeryal Hesaplama (Expected Loss)
        # Gelirin %10'unun risk altında olduğunu varsayalım (Exposure)
        exposure = gelir * 0.1 
        expected_loss = prob * exposure
        
        st.subheader("Tahmin Sonuçları")
        st.write(f"**Ayrılma Olasılığı (PD):** %{round(prob*100, 2)}")
        st.write(f"**Risk Altındaki Tutar (EAD):** {round(exposure, 2)} TL")
        
        # Büyük bir sonuç kartı
        st.error(f"### Beklenen Kayıp: {round(expected_loss, 2)} TL")
        
        if expected_loss > (gelir * 0.05):
            st.button("🔴 Acil Aksiyon Planı Oluştur")

    with col2:
        st.header("📊 Finansal Dağılım")
        # Gelir gruplarına göre risk analizi
        df['Gelir_Grubu'] = pd.cut(df['Gelir'], bins=[0, 50000, 150000, 10000000], labels=['Düşük', 'Orta', 'Yüksek'])
        risk_dist = df.groupby('Gelir_Grubu', observed=True)['Risk_Skoru'].mean()
        
        fig, ax = plt.subplots()
        risk_dist.plot(kind='bar', color='salmon', ax=ax)
        ax.set_title("Gelir Grubuna Göre Ortalama Risk")
        st.pyplot(fig)