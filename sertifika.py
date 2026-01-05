from fpdf import FPDF
import os

def images_to_pdf(image_list, output_pdf):
    pdf = FPDF()
    
    for img_path in image_list:
        if os.path.exists(img_path):
            pdf.add_page()
            # Resmi sayfaya sığacak şekilde ortalayarak ekler (A4 boyutu: 210x297mm)
            # Genişliği 190mm yaparak kenarlardan pay bırakıyoruz
            pdf.image(img_path, x=10, y=10, w=190) 
        else:
            print(f"Uyarı: {img_path} bulunamadı!")

    pdf.output(output_pdf)
    print(f"Başarılı: {output_pdf} oluşturuldu.")

# Sertifika dosyalarının isimlerini buraya yaz (Aynı klasörde olduklarından emin ol)
sertifikalar = ["sertifika1.png", "sertifika2.png"] 
output_name = "Emre_Orman_Sertifikalar.pdf"

images_to_pdf(sertifikalar, output_name)