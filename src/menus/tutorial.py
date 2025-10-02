from settings import *
from ui.utils import draw_text, get_text
import pygame
from math import sin


def draw_tutorial(screen, events, translations, lang, tutorial_assets):
    screen.fill("#1e1e1e")

    # Título traducido
    title = get_text(translations, lang, "tutorial-title")
    draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 100)

    # Acciones visuales (tecla + chango)
    actions = ["W", "S", "A", "D"]
    start_y = 200
    gap_y = 150

    for i, key in enumerate(actions):
        y = start_y + i * gap_y

        # Imagen de la tecla
        key_img = tutorial_assets["keys"][key]
        key_img = pygame.transform.scale(key_img, (100, 100))
        key_rect = key_img.get_frect()
        key_rect.center = (WINDOW_WIDTH // 2 - 150, y)
        screen.blit(key_img, key_rect)

        # Imagen del chango
        monkey_img = tutorial_assets["monkey"][key]
        monkey_img = pygame.transform.scale(monkey_img, (150, 150))
        monkey_rect = monkey_img.get_frect()
        monkey_rect.center = (WINDOW_WIDTH // 2 + 100, y)
        screen.blit(monkey_img, monkey_rect)

    # Mensaje traducido para regresar al menú
    exit_hint = get_text(translations, lang, "tutorial-control-menu")
    time = pygame.time.get_ticks() / 500
    alpha = sin(time) * 0.5 + 0.5
    color_blink = [int(100 + alpha * 155)] * 3  # RGB: gris brillante

    draw_text(screen, TITLE_FONT_PATH, 24, exit_hint,
              color_blink, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60)

    # Eventos
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            return "MENU"

    return "TUTORIAL"
