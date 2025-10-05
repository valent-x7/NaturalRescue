import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin

def draw_tutorial(screen, events, translations, lang, tutorial_assets):
    # Fondo con imagen
    bg = pygame.image.load("assets/images/tutorial/tutorial_background.png").convert()
    bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(bg, (0, 0))

    # Título
    title = get_text(translations, lang, "tutorial-title")
    draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

    # Tamaño uniforme para todas las imágenes
    IMG_SIZE = (120, 120)

    # -----------------------------
    # Fila 1 (WASD + chango)
    # -----------------------------
    actions = ["W", "A", "S", "D"]
    start_y = 220
    gap_x = 200
    base_x = WINDOW_WIDTH // 2 - (len(actions) - 1) * gap_x // 2

    for i, key in enumerate(actions):
        x = base_x + i * gap_x

        # Tecla
        key_img = pygame.transform.scale(tutorial_assets["keys"][key], IMG_SIZE)
        key_rect = key_img.get_rect(center=(x, start_y))
        screen.blit(key_img, key_rect)

        # Acción del chango
        monkey_img = pygame.transform.scale(tutorial_assets["monkey"][key], IMG_SIZE)
        monkey_rect = monkey_img.get_rect(center=(x, start_y + 150))
        screen.blit(monkey_img, monkey_rect)


    # Título
    extra_title = get_text(translations, lang, "tutorial-extra-actions")
    draw_text(screen, TITLE_FONT_PATH, 36, extra_title, "#FFFFFF", WINDOW_WIDTH // 2, start_y + 280)

    # -----------------------------
    # Fila 2 (H, R, P + extras)
    # -----------------------------
    extra_actions = ["H", "R", "P"]
    start_y_extras = start_y + 350  # debajo de WASD
    base_x_extras = WINDOW_WIDTH // 2 - (len(extra_actions) - 1) * gap_x // 2

    for i, key in enumerate(extra_actions):
        x = base_x_extras + i * gap_x

        # Tecla
        key_img = pygame.transform.scale(tutorial_assets["keys"][key], IMG_SIZE)
        key_rect = key_img.get_rect(center=(x, start_y_extras))
        screen.blit(key_img, key_rect)

        # Imagen extra al lado
        if key == "H":
            extra_img = tutorial_assets["extras"]["H_brote"]
        elif key == "R":
            extra_img = tutorial_assets["extras"]["R_restart"]
        elif key == "P":
            extra_img = tutorial_assets["extras"]["P_pause"]

        # Si es H o P, más anchas
        if key in ["H", "P"]:
            extra_img = pygame.transform.scale(extra_img, (250, 120))
        else:
            extra_img = pygame.transform.scale(extra_img, IMG_SIZE)

        extra_rect = extra_img.get_rect(center=(x, start_y_extras + 150))
        screen.blit(extra_img, extra_rect)

    # Mensaje para regresar al menú
    exit_hint = get_text(translations, lang, "tutorial-control-menu")
    t = pygame.time.get_ticks() / 500
    alpha = sin(t) * 0.5 + 0.5
    color_blink = [int(100 + alpha * 155)] * 3  

    draw_text(screen, TITLE_FONT_PATH, 24, exit_hint,
              color_blink, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40)

    # Eventos
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            return "MENU"

    return "TUTORIAL"
