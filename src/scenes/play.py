from settings import *
from ui.utils import draw_text, get_text
import pygame
import textwrap

def draw_game(screen, events, translations, TimeBar, healthbar, game_instance=None, delta_time=0):
    screen.fill("black")

    if game_instance:
        player = game_instance.player
        healthbar = game_instance.player_healthbar
        healthbar.hp = player.health
        TimeBar.maxt = 150

        if not game_instance.paused:
            player.input(events)
            game_instance.all_sprites.update(delta_time, events, player)
            TimeBar.update()
            game_instance.water_item.update(player.water_amount)

        game_instance.all_sprites.center_on_target(player, game_instance.map_width, game_instance.map_height)
        game_instance.all_sprites.draw_sprites()

        # ? Dibujamos elementos de UI
        # Definir clave de water item
        water_item_key = game_instance.water_item.get_status()

        healthbar.draw(screen) # -> Barra de vida
        TimeBar.draw(screen) # -> Tiempo
        game_instance.item.draw(screen, get_text(translations, game_instance.current_lang, "tree-sprout"), player.seeds) # -> Item de brotes
        game_instance.water_item.draw(screen, get_text(translations, game_instance.current_lang, "water-tank"), get_text(translations, game_instance.current_lang, water_item_key))

        if healthbar.hp <= 0 or TimeBar.t <= 0:
            return "GAMEOVER"

        #  Mostrar texto en rectángulo por 5 segundos
        if not hasattr(game_instance, "tutorial_start_time"):
            game_instance.tutorial_start_time = pygame.time.get_ticks()

        elapsed = (pygame.time.get_ticks() - game_instance.tutorial_start_time) / 1000
        if elapsed < 5:
            message = get_text(
                translations,
                game_instance.current_lang,
                "mission-text"
            )

            # Dividir el texto en líneas cortas
            wrapped_text = textwrap.wrap(message, width=50)
            font = pygame.font.Font(TITLE_FONT_PATH, 22)
            line_height = font.size("Tg")[1]
            text_height = line_height * len(wrapped_text) + 20
            text_width = max(font.size(line)[0] for line in wrapped_text) + 40

            # Crear rectángulo semitransparente
            rect_x = (WINDOW_WIDTH - text_width) // 2
            rect_y = 30
            rect_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            rect_surface.fill((0, 0, 0, 160))  # Negro con transparencia

            # Dibujar rectángulo
            screen.blit(rect_surface, (rect_x, rect_y))

            # Dibujar texto dentro del rectángulo
            y_offset = rect_y + 10
            for line in wrapped_text:
                text_surface = font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=y_offset)
                screen.blit(text_surface, text_rect)
                y_offset += line_height

        # Texto de pausa
        if game_instance.paused:
            draw_text(screen, TITLE_FONT_PATH, 64,
                      get_text(translations, game_instance.current_lang, "paused-title"),
                      "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
            draw_text(screen, TITLE_FONT_PATH, 36,
                      get_text(translations, game_instance.current_lang, "paused-description"),
                      "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

    # 🔘 Controles de pausa y nivel select
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                game_instance.paused = False
                return "LEVEL_SELECT"
            if event.key == pygame.K_p:
                game_instance.paused = not game_instance.paused
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_instance.paused:
            player.shoot((game_instance.all_sprites), player, event.pos,
                         game_instance.all_sprites.camera_offset, game_instance.all_sprites.zoom)

    return "PLAYING"
