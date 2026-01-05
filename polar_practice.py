import polars as pl
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt

# 1. ELİMİZDEKİ MODELİ VE VERİYİ KULLANALIM (Hızlıca tekrar oluşturuyoruz)
n_rows = 100_000 # Hız için bu sefer 100k yapalım
data = pl.DataFrame({
    "surucu_yasi": np.random.randint(18, 70, n_rows),
    "arac_yasi": np.random.randint(0, 15, n_rows),
    "yillik_km": np.random.normal(15000, 5000, n_rows)
})

# Basit bir risk puanı oluşturalım
risk_skoru = (70 - data["surucu_yasi"]) * 0.5 + (data["yillik_km"] / 1000) * 2
kaza_olasiligi = 1 / (1 + np.exp(-(risk_skoru / 10 - 5)))
data = data.with_columns(kaza_yapti_mi = (np.random.rand(n_rows) < kaza_olasiligi).cast(pl.Int8))

# 2. MODELİ EĞİTELİM
X = data.drop("kaza_yapti_mi").to_numpy()
y = data["kaza_yapti_mi"].to_numpy()
model = xgb.XGBClassifier().fit(X, y)

# 3. SOMUT ADIM: FİYATLANDIRMA (PRICING)
# Modelden her müşteri için kaza yapma ihtimalini alıyoruz
tahminler = model.predict_proba(X)[:, 1]

# Aktüeryal Formül: Saf Prim = Beklenen Hasar (Hasar başı 50.000 TL varsayalım)
hasar_maliyeti = 50_000
data = data.with_columns(
    tahmin_edilen_risk = pl.Series(tahminler),
    onerilen_prim = pl.Series(tahminler * hasar_maliyeti * 1.2) # %20 kar payı ekledik
)

# 4. SOMUT SONUÇ: RİSK GRUPLARINA GÖRE TABLO
# Yaş gruplarına göre ortalama primleri görelim
yas_gruplari = data.with_columns(
    yas_grubu = (pl.col("surucu_yasi") // 10) * 10
).group_by("yas_grubu").agg(
    pl.col("onerilen_prim").mean().alias("Ortalama_Prim"),
    pl.col("kaza_yapti_mi").mean().alias("Gercek_Kaza_Orani")
).sort("yas_grubu")

print("\n--- SOMUT SİGORTA TARİFESİ ---")
print(yas_gruplari)

# 5. GÖRSELLEŞTİRME: KAR/ZARAR ANALİZİ
plt.figure(figsize=(10,5))
plt.bar(yas_gruplari["yas_grubu"].to_numpy().astype(str), yas_gruplari["Ortalama_Prim"].to_numpy(), color='gold')
plt.title("Yaş Gruplarına Göre Belirlediğin Poliçe Fiyatları")
plt.ylabel("TL")
plt.xlabel("Yaş Grubu")
plt.show()