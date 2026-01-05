import subprocess

def send_wayland_notification(title, message):
    """
    Wayland üzerinde çalışan Arch Linux sistemine masaüstü bildirimi gönderir.
    """
    try:
        # notify-send (libnotify paketinden gelir) Arch'ta standarttır.
        subprocess.run(["notify-send", "-u", "critical", title, message])
    except Exception as e:
        print(f"Bildirim gönderilemedi: {e}")

# Kullanım Örneği:
if st.sidebar.button("Test Bildirimi Gönder"):
    send_wayland_notification("Quantum Risk Motoru", "Yarınki rapor teslimi için veriler hazırlandı!")