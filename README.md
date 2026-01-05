# 🛡️ Quantum Risk Master Suite - IFRS 17 Actuarial Terminal

Bu proje, bir sigorta şirketinin hasar karşılıklarını (Reserving) ve sermaye yeterliliğini analiz etmek için geliştirilmiş uçtan uca bir **Aktüeryal Karar Destek Sistemi**'dir.

## 🚀 Öne Çıkan Özellikler
- **Stokastik Modelleme:** Monte Carlo simülasyonu ile 10.000+ senaryo üzerinden hasar frekansı ve şiddeti tahmini. [cite: 2026-01-04]
- **IFRS 17 Uyumluluğu:** İskontolu nakit akışları (PV) ve %95 - %99 güven aralıklarında Risk Adjustment (RA) hesaplamaları.
- **Reasürans Modülü:** Excess of Loss (XoL) yapısı ile risk transfer optimizasyonu ve şirket retansiyon limit analizi.
- **Mortalite Analizi:** Gompertz-Makeham yasası kullanılarak yaşam tablosu ve ölüm hızı projeksiyonları. [cite: 2026-01-04]

## 🛠️ Teknik Altyapı
- **Backend:** FastAPI (Python) ile yüksek performanslı mikroservis mimarisi.
- **Frontend:** Streamlit ile interaktif aktüeryal dashboard.
- **Veri:** SQLite üzerinde kalıcı raporlama ve trend analizi.
- **Dağıtım:** Docker ve Docker Compose ile her ortamda (Cloud/Local) tek komutla kurulum. [cite: 2026-01-04]

## 📦 Kurulum
Proje klasöründe terminali açın ve çalıştırın:
```bash
docker-compose up --build
