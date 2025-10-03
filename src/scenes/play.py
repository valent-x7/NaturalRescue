# -> Aquí se dibujará el juego
from settings import *
from ui.healthbar import HealthBar
from ui.utils import draw_text, get_text
from sprites import Monkey

def draw_game(screen, events, translations, game_instance=None, delta_time = 0):
    
    screen.fill("black")

    if game_instance:
        # ? Jugador
        player = game_instance.player
        # ? Barra de vida
        healthbar = game_instance.player_healthbar
        healthbar.hp = player.health # Definimos vida en base a la del jugador

        if not game_instance.paused:
            # ? Actualizamos los sprites si no esta en pausa
            player.input(events)
            game_instance.all_sprites.update(delta_time, events, player)

        # Dibujamos juego
        # ? Centramos en el jugador
        game_instance.all_sprites.center_on_target(player, game_instance.map_width, game_instance.map_height)

        # ? Dibujamos los sprites
        game_instance.all_sprites.draw_sprites()

        # ? Dibujamos barra de vida
        healthbar.draw(screen)

        # ? Dibujamos item
        game_instance.item.draw(screen, get_text(translations, game_instance.current_lang, "tree-sprout"), player.seeds)

        # Texto de pausa
        if game_instance.paused:
            draw_text(screen, TITLE_FONT_PATH, 64, get_text(translations, game_instance.current_lang, "paused-title"), "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
            draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, game_instance.current_lang, "paused-description"), "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                game_instance.paused = False
                return "LEVEL_SELECT" 
            if event.key == pygame.K_p:
                game_instance.paused = not game_instance.paused
            
    return "PLAYING"