# scenes/tutorial.py
import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin


class Tutorial:
    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.finished = False
        self.start_time = pygame.time.get_ticks()

    def draw(self, screen, events, current_lang):
        # Fondo
        bg = pygame.image.load(
            "assets/images/tutorial/tutorial_background.png"
        ).convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))

        # Título
        title = get_text(self.translations, current_lang, "tutorial-title")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # Tamaño de imágenes
        IMG_SIZE = (120, 120)

        # Fila WASD
        actions = ["W", "A", "S", "D"]
        start_y = 220
        gap_x = 200
        base_x = WINDOW_WIDTH // 2 - (len(actions) - 1) * gap_x // 2

        for i, key in enumerate(actions):
            x = base_x + i * gap_x
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y)))

            monkey_img = pygame.transform.scale(
                self.tutorial_assets["monkey"][key], IMG_SIZE
            )
            screen.blit(monkey_img, monkey_img.get_rect(center=(x, start_y + 150)))

        # --- ✅ Texto: "Acciones extras" ---
        extra_title = get_text(
            self.translations, current_lang, "tutorial-extra-actions"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            extra_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            start_y + 280,  # Justo debajo de los changos
        )

        # Fila H, R, P
        extra_actions = ["H", "R", "P"]
        start_y_extras = start_y + 350
        base_x_extras = WINDOW_WIDTH // 2 - (len(extra_actions) - 1) * gap_x // 2

        for i, key in enumerate(extra_actions):
            x = base_x_extras + i * gap_x
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y_extras)))

            # Imagen extra
            if key == "H":
                extra_img = self.tutorial_assets["extras"]["H_brote"]
                extra_img = pygame.transform.scale(extra_img, (250, 120))
            elif key == "R":
                extra_img = self.tutorial_assets["extras"]["R_restart"]
                extra_img = pygame.transform.scale(extra_img, IMG_SIZE)
            elif key == "P":
                extra_img = self.tutorial_assets["extras"]["P_pause"]
                extra_img = pygame.transform.scale(extra_img, (250, 120))

            screen.blit(extra_img, extra_img.get_rect(center=(x, start_y_extras + 150)))

        # Mensaje parpadeante
        hint = get_text(self.translations, current_lang, "press-enter")
        t = pygame.time.get_ticks() / 500
        alpha = sin(t) * 0.5 + 0.5
        color_blink = [int(150 + alpha * 100)] * 3
        draw_text(
            screen,
            TITLE_FONT_PATH,
            30,
            hint,
            color_blink,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 60,
        )

        # Eventos
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    return "LEVEL"
                elif e.key == pygame.K_m:
                    return "MENU"

        return None
