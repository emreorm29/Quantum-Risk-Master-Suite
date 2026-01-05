import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import yfinance as yf
import subprocess
from datetime import datetime

# --- DATABASE & NOTIFICATION ---
def init_db():
    conn = sqlite3.connect('quantum_full.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS risk_logs 
                 (id INTEGER PRIMARY KEY, client TEXT, type TEXT, el REAL, rwa REAL, summary TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def notify(title, msg):
    try: subprocess.run(["notify-send", title, msg])
    except: pass

# --- CORE CALCULATORS ---
class FinanceEngine:
    @staticmethod
    def basel_iii_el(pd, lgd, ead): return pd * lgd * ead
    
    @staticmethod
    def generate_summary(name, el, rwa, pd):
        risk_level = "YÜKSEK" if pd > 0.1 else "MAKUL"
        return f"Sayın Yönetici, {name} isimli portföy için Beklenen Kayıp (EL) {el:,.2f} TL olarak hesaplanmıştır. " \
               f"Sermaye yükümlülüğü (RWA) ise {rwa:,.2f} TL'dir. Risk seviyesi {risk_level} olarak değerlendirilmektedir."

# --- UI MAIN ---
st.set_page_config(page_title="Quantum Enterprise Risk", layout="wide")
init_db()

st.sidebar.title("💎 Quantum Full Suite")
app_mode = st.sidebar.selectbox("Modül Seçin", ["Banka/Kredi Riski", "Yatırım/NPV", "Arşiv"])

if app_mode == "Banka/Kredi Riski":
    st.title("🏦 Basel III Kredi Risk Yönetimi")
    client = st.text_input("Müşteri/Portföy Adı", "Global Corp A.Ş.")
    
    c1, c2 = st.columns(2)
    with c1:
        ead = st.number_input("Risk Tutarı (EAD)", value=5000000)
        pd = st.slider("Temerrüt Olasılığı (PD %)", 0.5, 20.0, 5.0) / 100
        lgd = st.slider("Kayıp Oranı (LGD %)", 10, 90, 45) / 100
        
    with c2:
        el = FinanceEngine.basel_iii_el(pd, lgd, ead)
        rwa = el * 12.5 # Basitleştirilmiş RWA
        st.metric("Beklenen Kayıp (EL)", f"{el:,.2f} TL")
        st.metric("Sermaye Yükü (RWA)", f"{rwa:,.2f} TL")

    # --- YÖNETİCİ ÖZETİ ---
    st.divider()
    st.subheader("📝 Yönetici Özeti (Executive Summary)")
    summary_text = FinanceEngine.generate_summary(client, el, rwa, pd)
    st.info(summary_text)

    if st.button("Analizi Onayla ve Kaydet"):
        conn = sqlite3.connect('quantum_full.db')
        c = conn.cursor()
        c.execute("INSERT INTO risk_logs (client, type, el, rwa, summary, date) VALUES (?,?,?,?,?,?)",
                  (client, "Kredi", el, rwa, summary_text, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        notify("Analiz Kaydedildi", f"{client} portföyü arşive eklendi.")
        st.success("Veritabanı güncellendi.")

elif app_mode == "Arşiv":
    st.title("📜 Kurumsal Risk Arşivi")
    conn = sqlite3.connect('quantum_full.db')
    df = pd.read_sql_query("SELECT * FROM risk_logs", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()