import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import yfinance as yf
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime
import io
import os

# --- 1. VERİTABANI VE SİSTEM AYARLARI ---
def init_db():
    conn = sqlite3.connect('quantum_master.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS risk_archive 
                 (id INTEGER PRIMARY KEY, title TEXT, category TEXT, 
                  value REAL, summary TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def notify(title, msg):
    try: subprocess.run(["notify-send", title, msg])
    except: pass
# --- HASSAS GİRDİ YARDIMCISI (Sync Mechanism) ---
def precise_slider(label, min_val, max_val, default_val, step, key):
    """Hem slider hem de manuel giriş alanı oluşturur."""
    st.write(f"**{label}**")
    # Sayı girişi ve slider aynı key üzerinden senkronize çalışır
    val = st.number_input(f"{label} (Manuel)", min_value=min_val, max_value=max_val, 
                          value=default_val, step=step, key=f"num_{key}", label_visibility="collapsed")
    slide_val = st.slider(label, min_val, max_val, val, step=step, key=f"slide_{key}", label_visibility="collapsed")
    return val
# --- 2. HESAPLAMA MOTORLARI ---
class QuantumEngine:
    @staticmethod
    def get_annuity(age, rate=0.09):
        
        # Basitleştirilmiş TRH-2010 yaklaşımı
        # Gerçek uygulamada Nx/Dx tabloları kullanılır
        remaining_years = max(0, 75 - age)
        v = 1 / (1 + rate)
        if rate == 0: return remaining_years
        return (1 - v**remaining_years) / (1 - v)

    @staticmethod
    def calculate_npv(cfs, rate):
        return sum(cf / (1 + rate)**t for t, cf in enumerate(cfs))

    @staticmethod
    def basel_iii_el(pd, lgd, ead):
        return pd * lgd * ead

# --- 3. UI BAŞLANGIÇ ---
st.set_page_config(page_title="Quantum Risk Master Suite", layout="wide")
init_db()

# Sidebar: Global Ayarlar ve Canlı Veri
st.sidebar.title("💎 Quantum Master v1.0")
if st.sidebar.button("🌍 Canlı Piyasa Verisi Çek"):
    try:
        tnx = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1] / 100
        st.session_state['live_rate'] = tnx
        notify("Piyasa Güncellendi", f"ABD 10Y Tahvil: %{tnx*100:.2f}")
    except:
        st.session_state['live_rate'] = 0.09

module = st.sidebar.selectbox("Modül Seçin", 
    ["🛡️ Aktüeryal Tazminat", "💰 Yatırım & NPV", "🏦 Kredi Riski (Basel III)", "📜 Arşiv"])

# --- 4. MODÜLLER ---

if module == "🛡️ Aktüeryal Tazminat":
    st.title("🛡️ Aktüeryal Tazminat Hesaplama")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Maktul Adı", "Ahmet Yılmaz")
        age = st.number_input("Vefat Yaşı", 0, 90, 35)
        income = st.number_input("Aylık Net Gelir (TL)", value=45000)
        rate = st.session_state.get('live_rate', 0.09)
    
    with col2:
        annuity = QuantumEngine.get_annuity(age, rate)
        total_comp = annuity * income * 12
        st.metric("Hesaplanan Tazminat", f"{total_comp:,.2f} TL")
        st.caption(f"Kullanılan İskonto Oranı: %{rate*100:.2f}")
        
    if st.button("Tazminatı Arşive Kaydet"):
        summary = f"{name} için {age} yaşında, %{rate*100:.2f} faizle hesaplanan tazminat."
        conn = sqlite3.connect('quantum_master.db')
        conn.execute("INSERT INTO risk_archive (title, category, value, summary, date) VALUES (?,?,?,?,?)",
                     (name, "Aktüeryal", total_comp, summary, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        st.success("Kaydedildi!")

elif module == "💰 Yatırım & NPV":
    st.title("💰 Yatırım ve Nakit Akış Analizi")
    st.info("Gelecekteki nakit akışlarının bugünkü değerini (NPV) hesaplayın.")
    
    col1, col2 = st.columns(2)
    with col1:
        proj_name = st.text_input("Proje Adı", "Gayrimenkul Yatırımı")
        years = st.slider("Vade (Yıl)", 1, 30, 10)
        base_cf = st.number_input("Yıllık Başlangıç Geliri", value=100000)
        discount = st.slider("İskonto Oranı (%)", 0.0, 50.0, 15.0) / 100
        
        cfs = [base_cf * (1.1)**t for t in range(years)] # %10 büyüme sabitlendi
        
    with col2:
        npv = QuantumEngine.calculate_npv(cfs, discount)
        st.metric("Net Bugünkü Değer (NPV)", f"{npv:,.2f} TL")
        st.area_chart(cfs)

elif module == "🏦 Kredi Riski (Basel III)":
    st.title("🏦 Gelişmiş Kredi Riski ve Yönetici Özeti")
    ead = st.number_input("Risk Tutarı (EAD)", value=1000000)
    pd = st.slider("Temerrüt Olasılığı (PD %)", 0.1, 20.0, 5.0) / 100
    lgd = st.slider("Kayıp Oranı (LGD %)", 10, 90, 45) / 100
    
    el = QuantumEngine.basel_iii_el(pd, lgd, ead)
    rwa = el * 12.5
    
    st.divider()
    st.subheader("📝 Yönetici Özeti")
    summary = f"Risk Tutarı: {ead:,.2f} TL. Beklenen Kayıp: {el:,.2f} TL. Sermaye Yükü (RWA): {rwa:,.2f} TL. "
    st.info(summary)
    
    # Isı Haritası (Stress Test)
    if st.checkbox("Stres Testi Matrisini Göster"):
        pd_range = np.linspace(0.01, 0.20, 10)
        lgd_range = np.linspace(0.1, 0.9, 10)
        matrix = np.array([[QuantumEngine.basel_iii_el(p, l, ead) for p in pd_range] for l in lgd_range])
        fig, ax = plt.subplots()
        sns.heatmap(matrix, cmap="RdYlGn_r", ax=ax)
        st.pyplot(fig)

elif module == "📜 Arşiv":
    st.title("📜 Kurumsal Risk Arşivi")
    conn = sqlite3.connect('quantum_master.db')
    df = pd.read_sql_query("SELECT * FROM risk_archive ORDER BY date DESC", conn)
    st.dataframe(df, use_container_width=True)
    if st.button("Arşivi Temizle"):
        conn.execute("DELETE FROM risk_archive")
        conn.commit()
        st.rerun()
    conn.close()

st.sidebar.markdown("---")
st.sidebar.caption(f"Son Güncelleme: {datetime.now().strftime('%d-%m-%Y')}")
st.sidebar.caption("Arch Linux Quantum Master Suite")