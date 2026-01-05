from fpdf import FPDF

# Türkçe karakterleri latin-1 uyumlu hale getiren yardımcı fonksiyon
def tr_fix(text):
    search = "İıŞşĞğÜüÖöÇç"
    replace = "IiSsGgUuOoCc"
    res = text
    for i in range(len(search)):
        res = res.replace(search[i], replace[i])
    return res

class CV(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, tr_fix('EMRE ORMAN'), 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, tr_fix('Matematikci & Yazilim Uzmani (Aktueryal Risk Analizi)'), 0, 1, 'C')
        self.cell(0, 5, tr_fix('emreorman29@gmail.com | LinkedIn: /in/emreeorman | GitHub: /emreorm29'), 0, 1, 'C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, tr_fix(title), 0, 1, 'L', True)
        self.ln(2)

    def content_body(self, text):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, tr_fix(text))
        self.ln(4)

# CV Nesnesini Oluştur
pdf = CV()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Kariyer Özeti
pdf.section_title('KARIYER OZETI')
summary = ("Dokuz Eylul Universitesi Ingilizce Matematik bolumunden aldigim analitik altyapiyi, "
           "Neos Yazilim bunyesinde tamamladigim Yazilim Uzmanligi egitimleriyle birlestiren bir profesyonelim. "
           "Aktueryal matematik prensiplerini Python ve SQL kullanarak dijital cozumlere donusturme, "
           "stokastik surecler ve finansal risk modelleme uzerine odaklanmaktayim.")
pdf.content_body(summary)

# Teknik Yetkinlikler
pdf.section_title('TEKNIK YETKINLIKLER')
skills = ("* Matematiksel Modelleme: Olasilik Teorisi, Istatistiksel Analiz, Finansal Matematik.\n"
          "* Yazilim Gelistirme: Python (Ileri Seviye), SQL, R (Temel).\n"
          "* Veri Analizi: Pandas, NumPy, Matplotlib, Seaborn.\n"
          "* Aktueryal Teknikler: Monte Carlo Simulasyonu, Tazminat Modelleme, Basel III Stres Testleri.\n"
          "* Araclar: Streamlit, FPDF, Git/GitHub, Arch Linux.")
pdf.content_body(skills)

# Öne Çıkan Projeler
pdf.section_title('ONE CIKAN PROJELER')
project = ("Quantum Risk Master: Black Edition (End-to-End Risk Terminal)\n"
           "- Yatirim projeksiyonlari icin 1.000+ senaryolu Monte Carlo simulasyon motoru gelistirildi.\n"
           "- Teknik faiz ve enflasyon degiskenli aktueryal tazminat modelleri kuruldu.\n"
           "- yfinance API ile canli piyasa verisi entegrasyonu ve otomatik PDF raporlama saglandi.")
pdf.content_body(project)

# Eğitim ve Sertifikalar
pdf.section_title('EGITIM & SERTIFIKALAR')
edu = ("* Dokuz Eylul Universitesi - Matematik (Ingilizce) / Lisans Mezunu\n"
       "* Neos Yazilim Akademisi - Yazilim Uzmanligi Egitimi\n"
       "* ICWW Yazilim Uzmanligi Sertifikasi - 1 & 2 (Neos Yazilim)")
pdf.content_body(edu)

# Diller
pdf.section_title('DILLER')
langs = ("* Ingilizce: Ileri Seviye (Akademik ve Teknik Literatur Hakimiyeti)\n"
         "* Turkce: Anadil")
pdf.content_body(langs)

# Kaydet
pdf.output('Emre_Orman_CV.pdf')
print("Hata giderildi! Emre_Orman_CV.pdf basariyla olusturuldu.")