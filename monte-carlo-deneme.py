from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import uvicorn
import sqlite3
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from sklearn.linear_model import LinearRegression
import pandas as pd

def init_db():
    conn = sqlite3.connect("aktuer_veritabani.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raporlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            police_sayisi INTEGER,
            kaza_sayisi INTEGER,
            nominal_maliyet REAL,
            iskontolu_karsilik REAL,
            faiz_orani REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
app = FastAPI(
    title="Emre Orman - Aktüeryal Hesaplama Motoru",
    description="IFRS 17 ve Monte Carlo Simülasyonları için API",
    version="1.0.0"
)

# --- Veri Modelleri ---
class KarlilikGirdisi(BaseModel):
    toplam_prim: float  # Sigortalılardan toplanan para
    yillik_faiz: float = 0.45
    vade_ay: int = 12
@app.get("/analiz/ml-tahmin")
def hasar_tahmin_modeli(yeni_police_sayisi: int):
    # 1. Veritabanından geçmiş verileri çek
    conn = sqlite3.connect("aktuer_veritabani.db")
    df = pd.read_sql_query("SELECT police_sayisi, nominal_maliyet FROM raporlar", conn)
    conn.close()
    
    if len(df) < 5:
        return {"hata": "Model eğitmek için en az 5 geçmiş veri lazım. Biraz daha simülasyon yapın."}
    
    # 2. Modeli eğit (Poliçe sayısı -> Hasar maliyeti)
    X = df[['police_sayisi']]
    y = df['nominal_maliyet']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 3. Tahmin yap
    tahmin = model.predict([[yeni_police_sayisi]])
    
    return {
        "egitilen_veri_sayisi": len(df),
        "yeni_police_sayisi": yeni_police_sayisi,
        "yapay_zeka_tahmini_hasar": round(float(tahmin[0]), 2),
        "mesaj": "Bu tahmin, geçmişteki 6+ simülasyonunuzun trendine dayanmaktadır."
    }
class RiskGirdisi(BaseModel):
    police_sayisi: int = 5000
    kaza_olasiligi: float = 0.05
    ortalama_hasar: float = 50000.0
    guven_duzeyi: float = 0.95 # %95 güven aralığı
class ReasuransGirdisi(BaseModel):
    limit_tutar: float = 10000000.0 # Şirketin kendi üstünde tutacağı max hasar (Retansiyon)
    toplam_hasar: float

@app.post("/reasurans/paylasim-hesapla")
def reasurans_hesapla(data: ReasuransGirdisi):
    # Eğer toplam hasar limitimizi aşarsa, üzerini reasürör öder
    sirket_payi = min(data.toplam_hasar, data.limit_tutar)
    reasuror_payi = max(0, data.toplam_hasar - data.limit_tutar)
    
    return {
        "toplam_hasar": data.toplam_hasar,
        "sigorta_sirketi_odeyecek": round(sirket_payi, 2),
        "reasuror_odeyecek": round(reasuror_payi, 2),
        "korunma_orani": f"%{round((reasuror_payi / data.toplam_hasar) * 100, 2) if data.toplam_hasar > 0 else 0}"
    }
@app.post("/ifrs17/sermaye-yeterliligi")
def sermaye_yeterliligi(data: RiskGirdisi):
    # 10.000 farklı gelecek senaryosu yaratıyoruz
    sim_sayisi = 10000
    
    # Frekans: Kaç kaza olacak? (Poisson)
    kaza_sayilari = np.random.poisson(data.police_sayisi * data.kaza_olasiligi, sim_sayisi)
    
    # Şiddet: Her senaryo için toplam maliyet
    senaryo_maliyetleri = []
    for k in kaza_sayilari:
        if k > 0:
            maliyet = np.sum(np.random.gamma(shape=2.0, scale=data.ortalama_hasar/2.0, size=k))
            senaryo_maliyetleri.append(maliyet)
        else:
            senaryo_maliyetleri.append(0.0)
    
    # Verileri sırala ve %95'lik dilimi (Percentile) bul
    senaryo_maliyetleri = np.array(senaryo_maliyetleri)
    var_95 = np.percentile(senaryo_maliyetleri, data.guven_duzeyi * 100)
    beklenen_hasar = np.mean(senaryo_maliyetleri)
    
    # Risk Adjustment = %95'lik senaryo - Beklenen hasar
    ra = var_95 - beklenen_hasar
    
    return {
        "ortalama_beklenen_hasar": round(float(beklenen_hasar), 2),
        "yuzde_95_guvenli_tutar": round(float(var_95), 2),
        "risk_adjustment_payi": round(float(ra), 2),
        "aciklama": f"Şirket %{data.guven_duzeyi*100} ihtimalle bu hasarı ödeyebilmek için {round(float(ra), 2)} TL ek risk payı ayırmalıdır."
    }
@app.post("/ifrs17/karlilik-analizi")
def karlilik_analizi(data: KarlilikGirdisi):
    # Veritabanındaki son simülasyonu çekelim
    conn = sqlite3.connect("aktuer_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT iskontolu_karsilik FROM raporlar ORDER BY id DESC LIMIT 1")
    son_karsilik = cursor.fetchone()[0]
    conn.close()
    
    net_durum = data.toplam_prim - son_karsilik
    durum_mesaji = "KÂRLI (Profitable)" if net_durum > 0 else "ZARARDA (Onerous)"
    
    return {
        "toplam_prim": data.toplam_prim,
        "iskontolu_yukumluluk": son_karsilik,
        "net_kar_zarar": round(net_durum, 2),
        "ifrs17_siniflandirma": durum_mesaji
    }

@app.get("/analiz/grafik")
def analiz_grafigi():
    # Veritabanından son 10 raporun iskontolu karşılıklarını çek
    conn = sqlite3.connect("aktuer_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, iskontolu_karsilik FROM raporlar ORDER BY id DESC LIMIT 10")
    data = cursor.fetchall()
    conn.close()
    
    ids = [str(r[0]) for r in reversed(data)]
    degerler = [r[1] for r in reversed(data)]
    
    # Grafik oluşturma
    plt.figure(figsize=(10, 5))
    plt.plot(ids, degerler, marker='o', linestyle='-', color='b')
    plt.title("Son 10 Simülasyon: İskontolu Karşılık Trendi")
    plt.xlabel("Simülasyon ID")
    plt.ylabel("TL (Milyon)")
    plt.grid(True)
    
    # Grafiği bir stream olarak döndür
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
class FaizGirdisi(BaseModel):
    mevcut_faiz: float = 0.45
    oynaklik: float = 0.05
    vade_ay: int = 12
    simulasyon_sayisi: int = 1000

class HasarGirdisi(BaseModel):
    police_sayisi: int = 1000
    kaza_olasiligi: float = 0.05
    ortalama_hasar: float = 50000.0

# --- Endpointler ---

@app.get("/")
def ana_sayfa():
    return {
        "mesaj": "Aktüeryal API çalışıyor!",
        "dokumantasyon": "Endpointleri görmek için tarayıcıya http://127.0.0.1:8000/docs yazın."
    }

@app.post("/simule-et/faiz")
def faiz_simulasyonu(data: FaizGirdisi):
    # Monte Carlo ile Faiz Yolu
    soklar = np.random.normal(0, data.oynaklik, (data.simulasyon_sayisi, data.vade_ay))
    yollar = np.zeros((data.simulasyon_sayisi, data.vade_ay))
    yollar[:, 0] = data.mevcut_faiz
    
    for t in range(1, data.vade_ay):
        yollar[:, t] = yollar[:, t-1] + soklar[:, t]
    
    return {
        "beklenen_final_faiz": float(np.mean(yollar[:, -1])),
        "max_risk": float(np.max(yollar[:, -1])),
        "min_risk": float(np.min(yollar[:, -1]))
    }

@app.post("/hesapla/hasar-tahmini")
def hasar_tahmini(data: HasarGirdisi):
    # Kolektif Risk Modeli (Poisson + Gamma)
    # Kaç kaza olacak?
    kaza_sayisi = np.random.poisson(data.police_sayisi * data.kaza_olasiligi)
    
    # Bu kazaların toplam maliyeti ne olacak?
    if kaza_sayisi > 0:
        hasarlar = np.random.gamma(shape=2.0, scale=data.ortalama_hasar/2.0, size=kaza_sayisi)
        toplam_maliyet = np.sum(hasarlar)
    else:
        toplam_maliyet = 0.0
        
    return {
        "simule_edilen_kaza_sayisi": int(kaza_sayisi),
        "toplam_hasar_maliyeti": round(float(toplam_maliyet), 2),
        "police_basi_maliyet": round(float(toplam_maliyet / data.police_sayisi), 2)
    }
class IFRS17Girdisi(BaseModel):
    gelecek_hasar: float
    yillik_faiz: float
    vade_ay: int

@app.post("/ifrs17/bugunku-deger")
def bugunku_deger_hesapla(data: IFRS17Girdisi):
    # Klasik İskonto Formülü: PV = FV / (1 + r)^n
    aylik_oran = data.yillik_faiz / 12
    bugunku_deger = data.gelecek_hasar / ((1 + aylik_oran) ** data.vade_ay)
    
    return {
        "nominal_deger": data.gelecek_hasar,
        "bugunku_deger_PV": round(bugunku_deger, 2),
        "fark_iskonto_kazanci": round(data.gelecek_hasar - bugunku_deger, 2)
    }
class TopluRaporGirdisi(BaseModel):
    police_sayisi: int = 5000
    kaza_olasiligi: float = 0.08
    ortalama_hasar: float = 65000.0
    yillik_faiz: float = 0.45
    vade_ay: int = 12
@app.get("/raporlar/gecmis")
def gecmis_raporlar():
    conn = sqlite3.connect("aktuer_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raporlar ORDER BY tarih DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    return [{"id": r[0], "tarih": r[1], "iskontolu_karsilik": r[5]} for r in rows]
@app.post("/ifrs17/tam-rapor")
def tam_rapor_hesapla(data: TopluRaporGirdisi):
    # 1. Adım: Hasar Simülasyonu (Frekans x Şiddet)
    kaza_sayisi = np.random.poisson(data.police_sayisi * data.kaza_olasiligi)
    
    if kaza_sayisi > 0:
        hasarlar = np.random.gamma(shape=2.0, scale=data.ortalama_hasar/2.0, size=kaza_sayisi)
        toplam_nominal_hasar = np.sum(hasarlar)
    else:
        toplam_nominal_hasar = 0.0
        
    # 2. Adım: Risk Adjustment (RA) - IFRS 17 gereği belirsizlik payı ekleyelim (%10)
    # Gerçek hayatta bu da simülasyonla hesaplanır ama şimdilik sabit ekleyelim
    risk_adjustment = toplam_nominal_hasar * 0.10
    toplam_yukumluluk = toplam_nominal_hasar + risk_adjustment
    
    # 3. Adım: İskonto (PV)
    aylik_oran = data.yillik_faiz / 12
    bugunku_deger = toplam_yukumluluk / ((1 + aylik_oran) ** data.vade_ay)
    # Veritabanına kaydet
    conn = sqlite3.connect("aktuer_veritabani.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO raporlar (police_sayisi, kaza_sayisi, nominal_maliyet, iskontolu_karsilik, faiz_orani)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.police_sayisi, int(kaza_sayisi), float(toplam_nominal_hasar), round(float(bugunku_deger), 2), data.yillik_faiz))
    conn.commit()
    conn.close()
    return {
        "analiz_ozeti": {
            "toplam_kaza_sayisi": int(kaza_sayisi),
            "nominal_hasar_maliyeti": round(float(toplam_nominal_hasar), 2),
            "risk_adjustment_payi": round(float(risk_adjustment), 2),
            "toplam_brut_yukumluluk": round(float(toplam_yukumluluk), 2)
        },
        "finansal_sonuc": {
            "ayrilmasi_gereken_karsilik_PV": round(float(bugunku_deger), 2),
            "iskonto_tasarrufu": round(float(toplam_yukumluluk - bugunku_deger), 2)
        },
        "mesaj": "Bu değer, IFRS 17 bilançonuzda 'Yükümlülük' olarak görünecek rakamdır."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)