import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from fpdf import FPDF
import os

# --- 1. VERİTABANI VE SİSTEM ---
def init_db():
    conn = sqlite3.connect('quantum_ultimate.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS risk_logs 
                 (id INTEGER PRIMARY KEY, title TEXT, category TEXT, 
                  value REAL, summary TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(title, category, value, summary):
    conn = sqlite3.connect('quantum_ultimate.db')
    conn.execute("INSERT INTO risk_logs (title, category, value, summary, date) VALUES (?,?,?,?,?)",
                 (title, category, value, summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- 2. MÜKEMMEL PDF MOTORU ---
class RiskReport(FPDF):
    def header(self):
        if os.path.exists('logo.png'):
            self.image('logo.png', 10, 8, 30)
        self.set_font('Arial', 'B', 16)
        self.cell(80)
        self.cell(30, 10, 'QUANTUM RISK ANALYTICS', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 10, 'Profesyonel Aktuerya ve Stratejik Risk Raporu', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()} | Gizli Belge', 0, 0, 'C')

def generate_perfect_pdf(title, category, value, summary, scenario_df=None, plot_fig=None):
    pdf = RiskReport()
    pdf.add_page()
    def clean(t): return str(t).replace('ı','i').replace('ğ','g').replace('ü','u').replace('ş','s').replace('ö','o').replace('ç','c').replace('İ','I')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"Analiz Birimi: {clean(title)}", ln=1)
    pdf.cell(0, 10, txt=f"Kategori: {clean(category)}", ln=1)
    pdf.cell(0, 10, txt=f"Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1)
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, txt=f"NET SONUC: {value:,.2f} TL", ln=1, fill=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, txt=f"Aciklama: {clean(summary)}")
    pdf.ln(10)

    if scenario_df is not None:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "STRES TESTI SENARYO VERILERI", ln=1)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(60, 10, "Senaryo", 1, 0, 'C', True)
        pdf.cell(60, 10, "Potansiyel Kayip (TL)", 1, 1, 'C', True)
        pdf.set_font("Arial", size=10)
        for _, row in scenario_df.iterrows():
            pdf.cell(60, 10, clean(row['Senaryo']), 1)
            pdf.cell(60, 10, f"{row['Kayıp']:,.2f}", 1)
            pdf.ln()

    if plot_fig is not None:
        plot_fig.savefig("temp_plot.png", bbox_inches='tight', dpi=150)
        pdf.ln(10)
        pdf.image("temp_plot.png", x=25, w=150)
        os.remove("temp_plot.png")
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI YARDIMCISI ---
def precise_input(label, min_v, max_v, default_v, step_v, key_id):
    st.write(f"**{label}**")
    c1, c2 = st.columns([3, 1])
    num = c2.number_input(f"n_{key_id}", float(min_v), float(max_v), float(default_v), float(step_v), label_visibility="collapsed")
    val = c1.slider(f"s_{key_id}", float(min_v), float(max_v), num, float(step_v), label_visibility="collapsed")
    return val

# --- 4. ANA PROGRAM ---
st.set_page_config(page_title="Quantum Ultimate v5.1 Full", layout="wide")
init_db()

st.sidebar.title("💎 Quantum Ultimate")
module = st.sidebar.selectbox("Modüller", ["🛡️ Aktüeryal Tazminat", "💰 Yatırım & NPV", "🏦 Kredi Riski (Basel III)", "📜 Arşiv"])

# --- MODÜL: AKTÜERYAL ---
if module == "🛡️ Aktüeryal Tazminat":
    st.title("🛡️ Aktüeryal Tazminat Hesabı")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Dosya No", "2026/AKT-001")
        age = st.number_input("Yaş", 0, 90, 35)
        income = st.number_input("Aylık Net Gelir (TL)", value=45000)
        rate = precise_input("Teknik Faiz (%)", 0.0, 20.0, 9.0, 0.01, "act_rate")
    with c2:
        rem = max(0, 75 - age)
        v = 1 / (1 + (rate/100))
        annuity = (1 - v**rem) / (1 - v) if rate > 0 else rem
        total = annuity * income * 12
        st.metric("Toplam Tazminat Yükümlülüğü", f"{total:,.2f} TL")
        if st.button("🚀 Kaydet ve PDF Raporla"):
            summary = f"Yas {age} ve %{rate} teknik faiz ile 75 yas hedefli tazminat hesabi."
            save_to_db(name, "Aktüeryal", total, summary)
            pdf = generate_perfect_pdf(name, "Aktüeryal", total, summary)
            st.download_button("📥 PDF İndir", data=pdf, file_name=f"{name}.pdf")

# --- MODÜL: YATIRIM & NPV ---
elif module == "💰 Yatırım & NPV":
    st.title("💰 Yatırım Analizi ve NPV")
    c1, c2 = st.columns(2)
    with c1:
        p_name = st.text_input("Yatırım Projesi", "Enerji Santrali Yatırımı")
        inv = st.number_input("Başlangıç Maliyeti (TL)", value=1000000)
        disc = precise_input("İskonto Oranı (WACC %)", 0.0, 50.0, 15.0, 0.1, "npv_rate")
        years = st.slider("Analiz Süresi (Yıl)", 1, 10, 5)
    with c2:
        cfs = []
        for i in range(years):
            cfs.append(st.number_input(f"Yıl {i+1} Nakit Akışı", value=300000, key=f"cf_{i}"))
        npv = -inv + sum([cf / (1 + (disc/100))**(t+1) for t, cf in enumerate(cfs)])
        if npv > 0: st.success(f"Karlı Proje: NPV = {npv:,.2f} TL")
        else: st.error(f"Zararlı Proje: NPV = {npv:,.2f} TL")
        if st.button("🚀 Yatırımı Kaydet ve Raporla"):
            summary = f"Maliyet: {inv} TL, Iskonto: %{disc}, Sure: {years} yil."
            save_to_db(p_name, "Yatırım-NPV", npv, summary)
            pdf = generate_perfect_pdf(p_name, "Yatırım-NPV", npv, summary)
            st.download_button("📥 Analiz Raporunu İndir", data=pdf, file_name=f"{p_name}_NPV.pdf")

# --- MODÜL: KREDİ RİSKİ ---
elif module == "🏦 Kredi Riski (Basel III)":
    st.title("🏦 Kredi Riski ve Stres Testi")
    c1, c2 = st.columns(2)
    with c1:
        client = st.text_input("Müşteri", "Kurumsal Portföy X")
        ead = st.number_input("Risk Tutarı (EAD)", value=5000000)
        pd_val = precise_input("PD (%)", 0.1, 20.0, 5.0, 0.05, "pd")
        lgd_val = precise_input("LGD (%)", 10.0, 100.0, 45.0, 0.1, "lgd")
    el = (pd_val/100) * (lgd_val/100) * ead
    c2.metric("Beklenen Kayıp (EL)", f"{el:,.2f} TL")
    
    st.divider()
    st.subheader("📉 Senaryo Bazlı Karşılaştırmalı Analiz")
    scs = {"İyimser": {"p": 0.5, "l": 0.8}, "Beklenen": {"p": 1.0, "l": 1.0}, "Kötümser": {"p": 2.5, "l": 1.5}}
    s_list = []
    for sn, m in scs.items():
        loss = (min(pd_val*m["p"],100)/100) * (min(lgd_val*m["l"],100)/100) * ead
        s_list.append({"Senaryo": sn, "Kayıp": loss})
    df_s = pd.DataFrame(s_list)

    col_t, col_g = st.columns(2)
    col_t.table(df_s)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(df_s["Senaryo"], df_s["Kayıp"], color=['#2ecc71', '#3498db', '#e74c3c'])
    col_g.pyplot(fig)

    if st.button("🚀 Kurumsal Risk Raporu Oluştur"):
        summary = f"EAD: {ead} TL icin PD: %{pd_val} ve LGD: %{lgd_val} bazli stres testi."
        save_to_db(client, "Kredi Riski", el, summary)
        pdf_bytes = generate_perfect_pdf(client, "Kredi Riski", el, summary, df_s, fig)
        st.download_button("📥 PDF Raporunu İndir", data=pdf_bytes, file_name=f"{client}_Risk_Raporu.pdf")

# --- MODÜL: ARŞİV ---
elif module == "📜 Arşiv":
    st.title("📜 Analiz Arşivi")
    conn = sqlite3.connect('quantum_ultimate.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM risk_logs ORDER BY date DESC", conn), use_container_width=True)
    conn.close()