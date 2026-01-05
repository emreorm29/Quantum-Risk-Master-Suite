import numpy as np

def analyze_interest_sensitivity(self, age, rate_range):
        """
        Farklı faiz oranlarının peşin değer üzerindeki etkisini analiz eder.
        rate_range: [0.02, 0.03, 0.04, 0.05, 0.06] gibi faiz listesi
        """
        sensitivity_results = []
        original_rate = self.i  # Mevcut faizi yedekle

        for rate in rate_range:
            self.i = rate
            self.v = 1 / (1 + self.i)
            self._build_table() # Tabloyu anlık yeniden hesapla
            annuity = self.get_annuity(age)
            sensitivity_results.append({'Faiz Oranı': f"%{rate*100}", 'Peşin Değer (ax)': round(annuity, 4)})

        # Sistemi eski haline getir
        self.i = original_rate
        self.v = 1 / (1 + self.i)
        self._build_table()
        
        return pd.DataFrame(sensitivity_results)

# Kullanım:
rates = [0.02, 0.04, 0.06, 0.08, 0.10]
analysis = engine.analyze_interest_sensitivity(30, rates)
print("\n--- Faiz Duyarlılık Analizi (30 Yaş İçin) ---")