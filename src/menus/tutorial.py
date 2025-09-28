# -> Aquí haremos la pantalla del tutorial
from settings import *
from ui.utils import draw_text

def draw_tutorial(screen, events):
    screen.fill("#e7e5e4")
    
    draw_text(screen, TITLE_FONT_PATH, 42, 'Use the Keys To Move', "#FFFFFF", WINDOW_WIDTH / 2, 100)

    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"

    return "TUTORIAL"