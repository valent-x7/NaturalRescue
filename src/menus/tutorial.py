import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin


# --- Funciones de Utilidad Comunes ---


def _draw_blinking_hint(screen, translations, current_lang):
    """Dibuja el mensaje parpadeante de 'Presiona Enter'."""
    hint = get_text(translations, current_lang, "press-enter")
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


def _handle_tutorial_events(game, events, next_scene_on_enter, scene_on_m):
    """Maneja los eventos de teclado para continuar o salir."""
    for e in events:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                # Marcar el tutorial específico como completado
                if next_scene_on_enter == "LEVEL_1":
                    game.tutorial_1_done = True
                elif next_scene_on_enter == "LEVEL_2":
                    game.tutorial_2_done = True
                elif next_scene_on_enter == "LEVEL_3":
                    game.tutorial_3_done = True

                return next_scene_on_enter
            elif e.key == pygame.K_m:
                return scene_on_m
    return None



class Tutorial_levelone:
    """Tutorial Nivel 1: Movimiento y Acciones Básicas."""

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.finished = False
        self.start_time = pygame.time.get_ticks()
        self.scene_name = "TUTORIAL_1"
        self.next_scene_on_enter = "LEVEL_1"  # Escena a cargar al terminar
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):
        # Fondo
        bg = pygame.image.load("assets/images/tutorial/background_forest.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))

        # Título
        title = get_text(self.translations, current_lang, "tutorial-title")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # Tamaño de imágenes
        IMG_SIZE = (120, 120)
        ARROW_SIZE = (120, 120)  # Mismo tamaño que WASD

        # Fila WASD
        actions = ["W", "A", "S", "D"]
        start_y = 220
        gap_x = 200
        base_x = WINDOW_WIDTH // 2 - (len(actions) - 1) * gap_x // 2

        for i, key in enumerate(actions):
            x = base_x + i * gap_x

            # Dibujar la tecla (WASD)
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y)))

            # Dibujar el mono
            monkey_img = pygame.transform.scale(
                self.tutorial_assets["monkey"][key], IMG_SIZE
            )
            screen.blit(monkey_img, monkey_img.get_rect(center=(x, start_y + 150)))

            # <--- AQUÍ SE DIBUJA LA FLECHA
            arrow_img = pygame.transform.scale(
                self.tutorial_assets["arrows"][key], ARROW_SIZE
            )
            screen.blit(arrow_img, arrow_img.get_rect(center=(x, start_y + 280)))

        # --- Texto: "Acciones extras" (Ajustado Y) ---
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
            start_y + 380,  # Ajustado para dar espacio a la flecha
        )

        # Fila H
        extra_actions = ["H"]
        start_y_extras = start_y + 450  # Ajustado para dar espacio
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


            screen.blit(extra_img, extra_img.get_rect(center=(x, start_y_extras + 150)))

        # Mensaje parpadeante
        _draw_blinking_hint(screen, self.translations, current_lang)

        # Eventos
        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )

        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass




class Tutorial_leveltwo:
    """Tutorial Nivel 2: Muestra el mismo contenido que el Nivel 1."""

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.finished = False
        self.start_time = pygame.time.get_ticks()
        self.scene_name = "TUTORIAL_2"
        self.next_scene_on_enter = "LEVEL_2"
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):
        # Fondo
        bg = pygame.image.load("assets/images/tutorial/background_ice.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))

        # Título
        title = get_text(self.translations, current_lang, "tutorial-title")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # Tamaño de imágenes
        IMG_SIZE = (120, 120)
        ARROW_SIZE = (120, 120)

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

            # <--- AQUÍ SE DIBUJA LA FLECHA
            arrow_img = pygame.transform.scale(
                self.tutorial_assets["arrows"][key], ARROW_SIZE
            )
            screen.blit(arrow_img, arrow_img.get_rect(center=(x, start_y + 280)))

        # --- Texto: "Acciones extras" ---
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
            start_y + 380,
        )

        # Fila H
        extra_actions = ["H"]
        start_y_extras = start_y + 450
        base_x_extras = WINDOW_WIDTH // 2 - (len(extra_actions) - 1) * gap_x // 2

        for i, key in enumerate(extra_actions):
            x = base_x_extras + i * gap_x
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y_extras)))

            if key == "H":
                extra_img = self.tutorial_assets["extras"]["H_brote"]
                extra_img = pygame.transform.scale(extra_img, (250, 120))
            screen.blit(extra_img, extra_img.get_rect(center=(x, start_y_extras + 150)))

        # Mensaje parpadeante
        _draw_blinking_hint(screen, self.translations, current_lang)

        # Eventos
        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )

        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass



class Tutorial_levelthree:
    """Tutorial Nivel 3: Muestra el mismo contenido que el Nivel 1."""

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.finished = False
        self.start_time = pygame.time.get_ticks()
        self.scene_name = "TUTORIAL_3"
        self.next_scene_on_enter = "LEVEL_3"  # <--- DIFERENCIA
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):
        # Fondo
        bg = pygame.image.load("assets/images/tutorial/background_lab.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))

        # Título
        title = get_text(self.translations, current_lang, "tutorial-title")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # Tamaño de imágenes
        IMG_SIZE = (120, 120)
        ARROW_SIZE = (120, 120)

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

            # <--- AQUÍ SE DIBUJA LA FLECHA
            arrow_img = pygame.transform.scale(
                self.tutorial_assets["arrows"][key], ARROW_SIZE
            )
            screen.blit(arrow_img, arrow_img.get_rect(center=(x, start_y + 280)))

        # --- Texto: "Acciones extras" ---
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
            start_y + 380,
        )

        # Fila H
        extra_actions = ["H"]
        start_y_extras = start_y + 450
        base_x_extras = WINDOW_WIDTH // 2 - (len(extra_actions) - 1) * gap_x // 2

        for i, key in enumerate(extra_actions):
            x = base_x_extras + i * gap_x
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y_extras)))

            if key == "H":
                extra_img = self.tutorial_assets["extras"]["H_brote"]
                extra_img = pygame.transform.scale(extra_img, (250, 120))
            screen.blit(extra_img, extra_img.get_rect(center=(x, start_y_extras + 150)))

        # Mensaje parpadeante
        _draw_blinking_hint(screen, self.translations, current_lang)

        # Eventos
        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )

        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass
