from settings import *
from ui.utils import draw_text, get_text
import pygame
from math import sin

def draw_tutorial(screen, events, translations, current_lang):
    screen.fill("#e7e5e4")

    # Título principal
    title = get_text(translations, current_lang, "tutorial-title")
    draw_text(screen, TITLE_FONT_PATH, 42, title, "#000000", WINDOW_WIDTH / 2, 80)

    # Controles (ya con su traducción)
    controls = [
        get_text(translations, current_lang, "tutorial-control-up"),
        get_text(translations, current_lang, "tutorial-control-down"),
        get_text(translations, current_lang, "tutorial-control-left"),
        get_text(translations, current_lang, "tutorial-control-right"),
        get_text(translations, current_lang, "tutorial-control-menu")
    ]

    # Dibujar controles
    for i, text in enumerate(controls):
        draw_text(screen, TITLE_FONT_PATH, 28, text, "#000000", WINDOW_WIDTH / 2, 150 + i * 50)

    # ? Mensaje parpadeante: de cómo salir
    exit_hint = get_text(translations, current_lang, "tutorial-control-menu")
    time = pygame.time.get_ticks() / 500
    alpha = sin(time) * 0.5 + 0.5
    color_blink = [int(100 + alpha * 155)] * 3  # RGB: gris brillante

    draw_text(screen, TITLE_FONT_PATH, 24, exit_hint,
              color_blink, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60)

    # ? Manejo de eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"

    return "TUTORIAL"