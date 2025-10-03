import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin

def draw_tutorial(screen, events, translations, lang, tutorial_assets):
    screen.fill("#1e1e1e")

    # Título traducido
    title = get_text(translations, lang, "tutorial-title")
    draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 100)

    # Acciones con chango (W, A, S, D)
    actions = ["W", "A", "S", "D"]
    start_y = 200
    gap_y = 150

    for i, key in enumerate(actions):
        y = start_y + i * gap_y

        # Imagen de la tecla
        key_img = tutorial_assets["keys"][key]
        key_img = pygame.transform.scale(key_img, (100, 100))
        key_rect = key_img.get_rect()
        key_rect.center = (WINDOW_WIDTH // 2 - 150, y)
        screen.blit(key_img, key_rect)

        # Imagen del chango
        monkey_img = tutorial_assets["monkey"][key]
        monkey_img = pygame.transform.scale(monkey_img, (150, 150))
        monkey_rect = monkey_img.get_rect()
        monkey_rect.center = (WINDOW_WIDTH // 2 + 100, y)
        screen.blit(monkey_img, monkey_rect)

        # Acciones extras (H, R, P)
        extra_actions = ["H", "R", "P"]
        start_y_extras = start_y + (len(actions) * gap_y) - 50  # más arriba
        gap_y_extras = 100  # menos espacio entre extras

        for i, key in enumerate(extra_actions):
            y = start_y_extras + i * gap_y_extras

            # Imagen de la tecla
            key_img = tutorial_assets["keys"].get(key)
            if key_img:
             key_img = pygame.transform.scale(key_img, (80, 80))  # un poco más pequeño
             key_rect = key_img.get_rect()
             key_rect.center = (WINDOW_WIDTH // 2 - 150, y)
             screen.blit(key_img, key_rect)

    # Imagen extra al lado
    if key == "H":
        extra_img = tutorial_assets["extras"]["H_brote"]
    elif key == "R":
        extra_img = tutorial_assets["extras"]["R_restart"]
    elif key == "P":
        extra_img = tutorial_assets["extras"]["P_pause"]

    extra_img = pygame.transform.scale(extra_img, (80, 80))
    extra_rect = extra_img.get_rect()
    extra_rect.center = (WINDOW_WIDTH // 2 + 100, y)
    screen.blit(extra_img, extra_rect)


    # Mensaje traducido para regresar al menú (parpadea)
    exit_hint = get_text(translations, lang, "tutorial-control-menu")
    t = pygame.time.get_ticks() / 500
    alpha = sin(t) * 0.5 + 0.5
    color_blink = [int(100 + alpha * 155)] * 3  

    draw_text(screen, TITLE_FONT_PATH, 24, exit_hint,
              color_blink, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60)

    # Eventos
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            return "MENU"

    return "TUTORIAL"
