import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson

# 1. PARAMETRELER VE VERİ SETİ
# lambda (ortalama hasar sıklığı), mesleki risk ve toplumsal fayda
meslekler = ['Maden İşçisi', 'İtfaiyeci', 'Yazılım Geliştirici', 'Ofis Çalışanı']
geleneksel_risk_katsayisi = [0.9, 0.7, 0.2, 0.1] # Meslekten kaynaklı ek risk (0-1 arası)
toplumsal_fayda_puani = [100, 90, 40, 30] # Senin vizyonun: Topluma sağlanan fayda (0-100)

# 2. HESAPLAMA FONKSİYONU
def prim_hesapla():
    sonuclar = []
    baz_prim = 5000  # Standart yıllık prim bazı
    
    for i in range(len(meslekler)):
        # Geleneksel Yöntem: Sadece riske odaklanır
        geleneksel_prim = baz_prim * (1 + geleneksel_risk_katsayisi[i])
        
        # Senin Modelin: Riskten toplumsal fayda kredisini düşer
        # Fayda katsayısı primi %50'ye kadar indirebilir
        fayda_indirimi = (toplumsal_fayda_puani[i] / 100) * 0.5
        senin_modelin_primi = geleneksel_prim * (1 - fayda_indirimi)
        
        sonuclar.append({
            'Meslek': meslekler[i],
            'Geleneksel_Prim': geleneksel_prim,
            'Senin_Modelin': senin_modelin_primi,
            'Adalet_Farki': geleneksel_prim - senin_modelin_primi
        })
    
    return pd.DataFrame(sonuclar)

df = prim_hesapla()

# 3. GÖRSELLEŞTİRME (Wayland uyumlu)
plt.figure(figsize=(10, 6))
x = np.arange(len(meslekler))
width = 0.35

plt.bar(x - width/2, df['Geleneksel_Prim'], width, label='Geleneksel (Cezalandıran)', color='#e74c3c')
plt.bar(x + width/2, df['Senin_Modelin'], width, label='Senin Modelin (Adil)', color='#2ecc71')

plt.ylabel('Yıllık Sigorta Primi (TL)')
plt.title('Aktüeryal Adalet Analizi: Maden İşçisi Örneği')
plt.xticks(x, meslekler)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Konsol çıktısı ile detaylı analiz
print("\n--- AKTÜERYAL ADALET RAPORU ---")
print(df.to_string(index=False))
print("\nAnaliz: Maden işçisi toplum için en çok fiziksel riski üstlendiği için,")
print("senin modelinde 'Sosyal Hak Ediş' sayesinde en yüksek indirimi alıyor.")

plt.show()
# PROJE: Maden İşçisi Sosyal Hak Ediş Modeli
# Bu kod, fiziksel risk ile toplumsal fayda arasındaki dengeyi hesaplar.

import numpy as np
import pandas as pd
from scipy.stats import poisson

def calculate_ethical_premium(base_premium, risk_coeff, social_benefit_score):
    """
    Hesaplama mantığı: 
    Geleneksel Prim = Baz * (1 + Risk)
    Etik Prim = Geleneksel Prim * (1 - Sosyal İndirim)
    """
    trad_premium = base_premium * (1 + risk_coeff)
    social_discount = (social_benefit_score / 100) * 0.5
    ethical_premium = trad_premium * (1 - social_discount)
    return trad_premium, ethical_premium

# Örnek Uygulama
data = {
    'Occupation': 'Coal Miner',
    'Base': 5000,
    'Risk': 0.9,
    'SocialBenefit': 100
}

trad, ethical = calculate_ethical_premium(data['Base'], data['Risk'], data['SocialBenefit'])

print(f"Geleneksel Prim: {trad} TL")
print(f"Sosyal Adalet Odaklı Prim: {ethical} TL")