# -> Aquí se dibujará el juego
from settings import *

def draw_game(screen, events, game_instance=None, delta_time = 0):
    keys = pygame.key.get_pressed()
    screen.fill('#38bdf8')

    if game_instance:
        game_instance.all_sprites.update(keys, delta_time)
        game_instance.all_sprites.draw(screen)
    
    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "LEVEL_SELECT"   
            
    return "PLAYING"