import numpy as np
import matplotlib.pyplot as plt

# 1. Senaryo Parametreleri
sim_count = 10000 # Daha hassas sonuç için 10.000 senaryo
lambda_val = 3    # Beklenen yıllık hasar sayısı
avg_cost = 50000  # Hasar başına ortalama maliyet

# 2. Monte Carlo Simülasyonu
# Poisson dağılımı ile hasar sayılarını, Üstel dağılım ile hasar şiddetini modelliyoruz
np.random.seed(42)
damage_counts = np.random.poisson(lambda_val, sim_count)
total_costs = []

for count in damage_counts:
    # Her kaza için maliyet simülasyonu (lognormal dağılım gerçekçidir)
    costs = np.random.lognormal(mean=np.log(avg_cost), sigma=0.4, size=count)
    total_costs.append(np.sum(costs))

# 3. IFRS 17 - Risk Adjustment (RA) Hesaplaması
bel = np.mean(total_costs) # En İyi Tahmin Yükümlülüğü
confidence_level = 75
target_percentile = np.percentile(total_costs, confidence_level)
risk_adjustment = target_percentile - bel

# 4. Görselleştirme
plt.figure(figsize=(12, 7))
plt.hist(total_costs, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
plt.axvline(bel, color='green', linestyle='--', label=f'Best Estimate (BEL): {bel:,.0f} TL')
plt.axvline(target_percentile, color='red', linestyle='-', label=f'%75 Güven Sınırı: {target_percentile:,.0f} TL')

plt.title("IFRS 17 Risk Adjustment Analizi (Monte Carlo)")
plt.xlabel("Yıllık Toplam Hasar Maliyeti")
plt.ylabel("Frekans")
plt.legend()
plt.show()

print(f"Risk Adjustment Payı: {risk_adjustment:,.0f} TL")