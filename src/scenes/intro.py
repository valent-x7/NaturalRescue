import tkinter as tk
from pathlib import Path
import threading
import time

def playIntro():
    BASE_DIR = Path(__file__).resolve().parent.parent
    VIDEO_PATH = BASE_DIR.parent / "assets" / "vod" / "intro.mp4"
    
    if not VIDEO_PATH.exists():
        print(f"Advertencia: Intro no encontrada en: {VIDEO_PATH}")
        return False
    
    try:
        # Intentar con VLC primero (más fácil de instalar)
        try:
            import vlc
            return playIntro_vlc(VIDEO_PATH)
        except ImportError:
            pass
        
        # Si VLC falla, usar tkinter con video (más básico)
        return playIntro_tkinter(VIDEO_PATH)
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def playIntro_vlc(video_path):
    """Usando python-vlc que es más fácil de instalar"""
    import vlc
    
    # Crear instancia de VLC
    instance = vlc.Instance('--no-xlib --quiet')
    player = instance.media_player_new()
    
    # Configurar media
    media = instance.media_new(str(video_path))
    player.set_media(media)
    
    # Reproducir
    player.play()
    
    # Esperar a que termine o el usuario interrumpa
    time.sleep(0.5)  # Dar tiempo para que empiece
    
    print("Reproduciendo intro... (Presiona cualquier tecla para saltar)")
    
    # Esperar a que termine
    while player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
        time.sleep(0.1)
    
    player.stop()
    return True

def playIntro_tkinter(video_path):
    """Solución de emergencia con tkinter"""
    root = tk.Tk()
    root.title("Intro")
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    
    # Mensaje simple
    label = tk.Label(
        root, 
        text="Intro Video\n\n" + str(video_path.name),
        font=("Arial", 24),
        fg="white",
        bg="black"
    )
    label.pack(expand=True)
    
    # Timer para cerrar automáticamente
    def close_after_delay():
        time.sleep(5)  # 5 segundos
        root.quit()
    
    # Cerrar con cualquier tecla o click
    def on_key(event):
        root.quit()
    
    root.bind('<Key>', on_key)
    root.bind('<Button-1>', on_key)
    
    # Iniciar timer en hilo separado
    timer_thread = threading.Thread(target=close_after_delay, daemon=True)
    timer_thread.start()
    
    print("Mostrando pantalla de intro... (Presiona cualquier tecla para saltar)")
    
    root.mainloop()
    root.destroy()
    return True

# VERSIÓN DE EMERGENCIA MÁS SIMPLE
def playIntro_simple():
    """La solución más simple posible"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    VIDEO_PATH = BASE_DIR.parent / "assets" / "vod" / "intro.mp4"
    
    if not VIDEO_PATH.exists():
        print(f"Advertencia: Intro no encontrada en: {VIDEO_PATH}")
        return False
    
    print("=" * 50)
    print("INTRO DEL JUEGO")
    print(f"Video: {VIDEO_PATH.name}")
    print("Presiona Enter para continuar...")
    print("=" * 50)
    
    input()  # Esperar a que el usuario presione Enter
    return True

# VERSIÓN CON PYTHON VLC (RECOMENDADA)
def playIntro_vlc_simple():
    """Instala: pip install python-vlc"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    VIDEO_PATH = BASE_DIR.parent / "assets" / "vod" / "intro.mp4"
    
    if not VIDEO_PATH.exists():
        print(f"Advertencia: Intro no encontrada en: {VIDEO_PATH}")
        return False
    
    try:
        import vlc
        import time
        
        # Configurar VLC sin interfaz gráfica
        instance = vlc.Instance('--no-video-title-show --quiet')
        player = instance.media_player_new()
        media = instance.media_new(str(VIDEO_PATH))
        player.set_media(media)
        
        print("Reproduciendo intro... (Presiona Ctrl+C para saltar)")
        player.play()
        
        # Esperar a que termine
        while True:
            state = player.get_state()
            if state in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                break
            time.sleep(0.1)
                
        player.stop()
        return True
        
    except ImportError:
        print("python-vlc no instalado. Usando método simple...")
        return playIntro_simple()
    except KeyboardInterrupt:
        print("\nIntro interrumpida por el usuario")
        return True
    except Exception as e:
        print(f"Error con VLC: {e}")
        return playIntro_simple()

# EJECUCIÓN PRINCIPAL - USA ESTA
def show_intro():
    """FUNCIÓN QUE DEBES USAR EN TU JUEGO"""
    print("Iniciando intro...")
    
    # Probamos en este orden:
    # 1. VLC (mejor calidad)
    # 2. Método simple (fallback)
    
    success = playIntro_vlc_simple()
    
    if success:
        print("Intro completada")
    else:
        print("Intro falló, continuando...")
    
    return success

# Para probar
if __name__ == "__main__":
    show_intro()