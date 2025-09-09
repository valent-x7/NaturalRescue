# -> Aquí se haran las configuraciones del juego
from settings import *
from ui.utils import draw_text

def draw_settings(screen, events):
    screen.fill("#6ee7b7")

    draw_text(screen, "Settings", "#FFFFFF", 250)

    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            
    return "SETTINGS"