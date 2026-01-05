import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt

# Ortalama hasar sayısı (Lambda)
lambda_hasar = 2 

# Hasar sayıları (0'dan 10'a kadar olasılıkları görelim)
k_degerleri = np.arange(0, 11)

# Olasılık kütle fonksiyonu (PMF) hesaplama
olasiliklar = poisson.pmf(k_degerleri, lambda_hasar)

# Görselleştirme
plt.figure(figsize=(10, 6))
plt.bar(k_degerleri, olasiliklar, color='skyblue', edgecolor='black')
plt.title(f'Hasar Olasılığı Dağılımı ($\lambda$={lambda_hasar})')
plt.xlabel('Gerçekleşen Hasar Sayısı (k)')
plt.ylabel('Olasılık')
plt.xticks(k_degerleri)
plt.grid(axis='y', alpha=0.3)
plt.show()

print(f"Hiç hasar olmama olasılığı: %{olasiliklar[0]*100:.2f}")
print(f"Tam 2 hasar olma olasılığı (Beklenen): %{olasiliklar[2]*100:.2f}")