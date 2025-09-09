# -> Aquí se dibujará el juego
from settings import *

def draw_game(screen, events):
    
    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            
    screen.fill('#38bdf8')
            
    return "PLAYING"