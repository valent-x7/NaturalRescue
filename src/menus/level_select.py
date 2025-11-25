import sys
import os
from os.path import join
from ui.button import Button as ImageButton
import pygame
from ui.utils import get_text, draw_text, set_difficulty
from math import sin
from settings import *

sys.path.append(os.path.abspath(".."))
import settings as main_settings


class LevelSelectMenu:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen
        self.translations = game.translations
        self.wd = os.getcwd()

        # Sonido de clic manual
        self.click_sound = pygame.mixer.Sound(
            join(self.wd, "assets", "button_click.mp3")
        )

        self.setup_images()
        self.setup_fonts()
        self.setup_buttons(game.current_lang)

    def setup_buttons(self, lang):
        # --- CAMBIO DE RUTA ---
        # Ahora busca en "botones_levelselect"
        path_btns = join(
            self.wd, "assets", "images", "level_select", "botones_levelselect"
        )

        # --- TAMAÑO MÁS GRANDE ---
        # Aumentamos de 450 a 550 para que se vean imponentes
        btn_w = 550
        btn_h = 180
        target_size = (btn_w, btn_h)

        # Función auxiliar para cargar y escalar
        def load_and_scale(filename):
                img = pygame.image.load(join(path_btns, filename)).convert_alpha()
                return pygame.transform.scale(img, target_size)

        if lang == "es":
            # ESPAÑOL 
            self.lvl1_unpressed = load_and_scale("btn_nivel1_unpressed.png")
            self.lvl1_pressed = load_and_scale("btn_nivel1_pressed.png")

            self.lvl2_unpressed = load_and_scale("btn_nivel2_unpressed.png")
            self.lvl2_pressed = load_and_scale("btn_nivel2_pressed.png")

            self.lvl3_unpressed = load_and_scale("btn_nivel3_unpressed.png")
            self.lvl3_pressed = load_and_scale("btn_nivel3_pressed.png")
        else:
            # INGLÉS
            self.lvl1_unpressed = load_and_scale("btn_level1_unpressed.png")
            self.lvl1_pressed = load_and_scale("btn_level1_pressed.png")

            self.lvl2_unpressed = load_and_scale("btn_level2_unpressed.png")
            self.lvl2_pressed = load_and_scale("btn_level2_pressed.png")

            self.lvl3_unpressed = load_and_scale("btn_level3_unpressed.png")
            self.lvl3_pressed = load_and_scale("btn_level3_pressed.png")

        # --- POSICIONES ---
        center_y = 380
        # Aumentamos el espacio porque los botones ahora son gigantes (550px)
        spacing = 600

        # Creamos los rectángulos centrados
        self.lvl1_rect = self.lvl1_unpressed.get_rect(
            center=(main_settings.WINDOW_WIDTH // 2 - spacing, center_y)
        )
        self.lvl2_rect = self.lvl2_unpressed.get_rect(
            center=(main_settings.WINDOW_WIDTH // 2, center_y)
        )
        self.lvl3_rect = self.lvl3_unpressed.get_rect(
            center=(main_settings.WINDOW_WIDTH // 2 + spacing, center_y)
        )

        # --- BOTONES DE DIFICULTAD (Sin cambios) ---
        self.normal_difficulty_btn = ImageButton(
            self.game_screen,
            (WINDOW_WIDTH / 2 - 250, 705),
            self.change_difficulty_font,
            340,
            90,
            get_text(self.translations, lang, "normal-difficulty"),
            4,
            join(self.wd, "assets", "images", "level_select", "normal.png"),
            15,
            "#26FF26",
            "#106122",
        )

        self.advanced_difficulty_btn = ImageButton(
            self.game_screen,
            (WINDOW_WIDTH / 2 + 250, 705),
            self.change_difficulty_font,
            340,
            90,
            get_text(self.translations, lang, "advanced-difficulty"),
            4,
            join(self.wd, "assets", "images", "level_select", "advanced.png"),
            25,
            "#EF5350",
            "#C62828",
        )

    def run(self, game, events):
        # Fondo
        self.game_screen.blit(self.background, [0, 0])

        # Títulos
        title_text = self.fuente_pixel.render(
            get_text(game.translations, game.current_lang, "level-select-title"),
            True,
            (255, 255, 255),
        )
        text_rect = title_text.get_rect(center=(main_settings.WINDOW_WIDTH / 2, 100))
        self.game_screen.blit(title_text, text_rect)

        difficulty_title = self.difficulty_title_font.render(
            get_text(game.translations, game.current_lang, "select-difficulty-title"),
            True,
            "white",
        )
        difficulty_title_rect = difficulty_title.get_frect(
            center=(WINDOW_WIDTH / 2, 615)
        )
        self.game_screen.blit(difficulty_title, difficulty_title_rect)

        # Flecha de dificultad
        if game.current_difficulty == "normal":
            self.arrow_rect.centerx = WINDOW_WIDTH / 2 - 485
        else:
            self.arrow_rect.centerx = WINDOW_WIDTH / 2
        self.game_screen.blit(self.arrow_image, self.arrow_rect)

        # Posición del mouse
        mouse_pos = pygame.mouse.get_pos()

        # --- FUNCIÓN DE ESCALADO ---
        def scale_rect_center(image, rect, scale):
            w = int(image.get_width() * scale)
            h = int(image.get_height() * scale)
            scaled = pygame.transform.scale(image, (w, h))
            new_rect = scaled.get_rect(center=rect.center)
            return scaled, new_rect

        # --- DIBUJAR BOTONES DE NIVEL (Lógica Hover + Pressed) ---

        # Nivel 1
        if self.lvl1_rect.collidepoint(mouse_pos):
            # Mouse encima: Usamos PRESSED y escalamos
            img, r = scale_rect_center(self.lvl1_pressed, self.lvl1_rect, 1.15)
        else:
            # Normal: Usamos UNPRESSED normal
            img, r = self.lvl1_unpressed, self.lvl1_rect
        self.game_screen.blit(img, r)

        # Nivel 2
        if self.lvl2_rect.collidepoint(mouse_pos):
            img, r = scale_rect_center(self.lvl2_pressed, self.lvl2_rect, 1.15)
        else:
            img, r = self.lvl2_unpressed, self.lvl2_rect
        self.game_screen.blit(img, r)

        # Nivel 3
        if self.lvl3_rect.collidepoint(mouse_pos):
            img, r = scale_rect_center(self.lvl3_pressed, self.lvl3_rect, 1.15)
        else:
            img, r = self.lvl3_unpressed, self.lvl3_rect
        self.game_screen.blit(img, r)

        # Dibujar botones de dificultad
        self.normal_difficulty_btn.draw()
        self.advanced_difficulty_btn.draw()

        # Texto de volver
        exit_hint = get_text(game.translations, game.current_lang, "press-m-to-menu")
        t = pygame.time.get_ticks() / 500
        alpha = sin(t) * 0.5 + 0.5
        color_blink = [int(100 + alpha * 155)] * 3
        draw_text(
            self.game_screen,
            TITLE_FONT_PATH,
            24,
            exit_hint,
            color_blink,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 40,
        )

        # --- EVENTOS ---
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "MENU"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clic en Nivel 1
                if self.lvl1_rect.collidepoint(event.pos):
                    if not game.muted:
                        self.click_sound.play()
                    return "START_LEVEL_1"

                # Clic en Nivel 2
                elif self.lvl2_rect.collidepoint(event.pos):
                    if not game.muted:
                        self.click_sound.play()
                    return "START_LEVEL_2"

                # Clic en Nivel 3
                elif self.lvl3_rect.collidepoint(event.pos):
                    if not game.muted:
                        self.click_sound.play()
                    return "START_LEVEL_3"

                # Clics en dificultad
                elif self.normal_difficulty_btn.is_clicked(event, game.muted):
                    set_difficulty("config.json", "normal")
                    game.current_difficulty = "normal"

                elif self.advanced_difficulty_btn.is_clicked(event, game.muted):
                    set_difficulty("config.json", "advanced")
                    game.current_difficulty = "advanced"

        return "LEVEL_SELECT"

    def setup_images(self):
        bg = pygame.image.load("assets/images/fondo2.png")
        self.background = pygame.transform.scale(
            bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert()

        arrow_img = pygame.image.load(
            join(self.wd, "assets", "images", "ajustes", "flecha.png")
        )
        self.arrow_image = pygame.transform.scale(arrow_img, (96, 96)).convert_alpha()
        self.arrow_rect = self.arrow_image.get_frect()
        self.arrow_rect.centery = 705

    def setup_fonts(self):
        self.fuente_pixel = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 40)
        self.difficulty_title_font = pygame.font.Font(
            "src/menus/fuentestexto/prstartk.ttf", 30
        )
        self.change_difficulty_font = pygame.font.Font(
            "src/menus/fuentestexto/prstartk.ttf", 24
        )
