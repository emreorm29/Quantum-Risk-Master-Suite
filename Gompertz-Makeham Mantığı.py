import pandas as pd

df = pd.read_csv('risk_verisi.csv')

def prim_hesapla(row):
    yas = row['Yas']
    cinsiyet = row['Cinsiyet']
    teminat = row['Teminat_Tutari']
    
    # Basit bir Mortalite Modeli (Yaşlandıkça risk logaritmik artar)
    # qx = Bir yıl içinde ölme olasılığı
    base_risk = 0.0001  # Temel risk
    qx = base_risk * (1.1 ** (yas - 20)) 
    
    # Cinsiyet Farkı (İstatistiksel olarak kadınlar daha uzun yaşar)
    if cinsiyet == 'K':
        qx = qx * 0.8  # Kadın primi %20 indirimli
    
    # Net Prim = Teminat * Ölme Olasılığı
    net_prim = teminat * qx
    
    # Şirket Karı ve Operasyonel Giderler (%30 ekleyelim)
    brut_prim = net_prim * 1.3
    
    return round(brut_prim, 2)

df['Yillik_Sigorta_Primi'] = df.apply(prim_hesapla, axis=1)

print("\n--- AKTÜERYAL POLİÇE FİYATLANDIRMA ---")
print(df[['Musteri_ID', 'Yas', 'Cinsiyet', 'Yillik_Sigorta_Primi']])
def urun_oneri(row):
    # Eğer yıllık prim, teminatın %5'inden fazlaysa ürün değiştir
    if row['Yillik_Sigorta_Primi'] > (row['Teminat_Tutari'] * 0.05):
        return "Kaza Sigortası (Alternatif)"
    else:
        return "Tam Hayat Sigortası (Standart)"

df['Onerilen_Urun'] = df.apply(urun_oneri, axis=1)

print("\n--- STRATEJİK ÜRÜN YÖNLENDİRME ---")
print(df[['Musteri_ID', 'Yas', 'Yillik_Sigorta_Primi', 'Onerilen_Urun']])