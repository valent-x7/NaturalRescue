import pygame
import cv2
import numpy as np

def reproducir_intro(video_path, audio_path, screen):    
    # ? --- Cargar el Video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"No se pudo abrir el video: {video_path}")
        return # --> Regresamos a menu 

    # --> Datos del Video
    fps = cap.get(cv2.CAP_PROP_FPS) # FPS del video
    clock = pygame.time.Clock()
    
    # --> Cargar y reproducir audio
    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        print("Reproduciendo intro...")
    except Exception as e:
        print(f"Audio de intro no encontrado o error: {e}")

    screen_width, screen_height = screen.get_size()
    running_intro = True

    while running_intro and cap.isOpened():
        clock.tick(fps) # -> Controlar FPS
        
        ret, frame = cap.read() # -> Leer siguiente Frame
        
        if not ret:
            break # -> Si no hay ret se terminó el video
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit() # Cerrar todo el programa
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    running_intro = False # Saltar intro

        # --- Procesar la Imagen ---
        
        # Paso A: Convertir de BGR (OpenCV) a RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Paso B: Transponer ejes. 
        # OpenCV usa (Alto, Ancho, Color), Pygame surface usa (Ancho, Alto, Color)
        frame = np.transpose(frame, (1, 0, 2))
        
        # Paso C: Crear la superficie
        frame_surface = pygame.surfarray.make_surface(frame)
        
        # Paso D: Escalar al tamaño de la pantalla
        frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))

        # 7. Dibujar
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()

    # --- Limpieza de recursos ---
    cap.release()             # -> Liberar el archivo de video
    pygame.mixer.music.stop() # -> Detener la música de la intro
    pygame.event.clear()      # -> Limpiar clicks residuales para no seleccionar nada en el menú por error

    # ? Transición para el juego principal.
    screen.fill((0, 0, 0))
    pygame.display.flip()