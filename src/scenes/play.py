# -> Aquí se dibujará el juego
from settings import *

def draw_game(screen, events, game_instance=None, delta_time = 0):
    
    screen.fill("black")

    if game_instance:
        # ? Jugador
        player = game_instance.player

        # ? Actualizamos los sprites
        player.input(events)
        game_instance.all_sprites.update(delta_time, events)

        # ? Centramos en el jugador
        game_instance.all_sprites.center_on_target(player, game_instance.map_width, game_instance.map_height)

        # ? Dibujamos los sprites
        game_instance.all_sprites.draw_sprites()
    
    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "LEVEL_SELECT"   
            
    return "PLAYING"