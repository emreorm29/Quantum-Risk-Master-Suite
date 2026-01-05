import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
from fpdf import FPDF
import io
import os
import subprocess

# --- CORE ENGINE GÜNCELLEMESİ ---
class RiskEngine:
    def __init__(self, rate):
        self.i = rate
        self.v = 1 / (1 + self.i)

    def calculate_npv(self, cash_flows, rate_override=None):
        r = rate_override if rate_override is not None else self.i
        return sum(cf / (1 + r)**t for t, cf in enumerate(cash_flows))

# --- WEB ARAYÜZÜNE EKLEME ---
st.set_page_config(page_title="Quantum Enterprise Risk", layout="wide")

# Modüllere "Stres Testi" ekleyelim
module = st.sidebar.selectbox("Çalışma Alanı", 
    ["Aktüeryal Tazminat", "Yatırım Analizi", "Stres Testi (Isı Haritası)"])

if module == "Stres Testi (Isı Haritası)":
    st.title("🔥 Kurumsal Stres Testi ve Isı Haritası")
    st.markdown("Farklı faiz ve büyüme oranlarının projenin/tazminatın bugünkü değerine etkisini analiz edin.")

    # Parametreler
    base_cf = st.number_input("Baz Nakit Akışı / Yıllık Gelir", value=100000)
    years = st.slider("Vade (Yıl)", 5, 30, 10)
    
    # Senaryo Aralıkları
    rates = np.linspace(0.05, 0.25, 10) # %5 ile %25 arası faiz
    growths = np.linspace(0.0, 0.20, 10) # %0 ile %20 arası büyüme
    
    # Isı Haritası Matrisi Oluşturma
    matrix = np.zeros((len(rates), len(growths)))
    
    for i, r in enumerate(rates):
        for j, g in enumerate(growths):
            cfs = [base_cf * (1 + g)**t for t in range(years)]
            matrix[i, j] = sum(cf / (1 + r)**t for t, cf in enumerate(cfs))
            
    # Görselleştirme
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matrix, annot=False, fmt=".0f", 
                xticklabels=[f"%{x*100:.1f}" for x in growths],
                yticklabels=[f"%{y*100:.1f}" for y in rates],
                cmap="RdYlGn", ax=ax)
    plt.xlabel("Büyüme Oranı")
    plt.ylabel("İskonto (Faiz) Oranı")
    plt.title("Net Bugünkü Değer (NPV) Hassasiyet Matrisi")
    st.pyplot(fig)
    
    st.success("Yeşil alanlar yatırımın en kârlı/güvenli olduğu, kırmızı alanlar ise riskli olduğu bölgelerdir.")

# ... (Diğer modül kodları aynı kalacak)