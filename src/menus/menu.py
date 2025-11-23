import sys
import os
from os.path import join
from ui.button import Button
from ui.utils import get_text
import pygame
import math

sys.path.append(os.path.abspath(".."))
import settings as main_settings

sys.path.append(os.path.abspath("."))
import settings as menu_settings


class MainMenu:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen
        self.wd = os.getcwd()

        self.traslations = game.translations

        self.setup_fonts()
        self.setup_images()

        # Scroll de cada capa (parallax)
        self.scroll_layer_2 = 0
        self.scroll_layer_3 = 0
        self.scroll_layer_4 = 0
        self.scroll_layer_5 = 0

        self.tiles = math.ceil(main_settings.WINDOW_WIDTH / self.background_width) + 1

        self.setup_positions()
        self.setup_buttons(game.current_lang)

    def run(self, game, events):

        # ---------- PARALLAX ORIGINAL ----------
        self.game_screen.blit(self.layer1, [0, 0])

        for i in range(self.tiles + 1):
            self.game_screen.blit(self.layer2, (i * self.background_width + self.scroll_layer_2, 0))
        for i in range(self.tiles + 1):
            self.game_screen.blit(self.layer3, (i * self.background_width + self.scroll_layer_3, 0))
        for i in range(self.tiles + 1):
            self.game_screen.blit(self.layer4, (i * self.background_width + self.scroll_layer_4, 0))
        for i in range(self.tiles + 1):
            self.game_screen.blit(self.layer5, (i * self.background_width + self.scroll_layer_5, 0))

        # Velocidades originales
        self.scroll_layer_2 -= 0.2
        self.scroll_layer_3 -= 0.5
        self.scroll_layer_4 -= 1.5
        self.scroll_layer_5 -= 2.5
        # --------------------------------------

        # Título
        title_rect = self.title_image.get_frect(
            center=(main_settings.WINDOW_WIDTH // 2,
                    main_settings.WINDOW_HEIGHT // 4 + 128)
        )
        self.game_screen.blit(self.title_image, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        # ---------- BOTONES CON HOVER (120%) ----------
        def scale_rect_center(image, rect, scale):
            w = int(image.get_width() * scale)
            h = int(image.get_height() * scale)
            scaled = pygame.transform.scale(image, (w, h))
            new_rect = scaled.get_rect(center=rect.center)
            return scaled, new_rect

        # PLAY
        if self.play_btn_rect.collidepoint(mouse_pos):
            img, r = scale_rect_center(self.play_btn_unpressed, self.play_btn_rect, 1.20)
        else:
            img, r = self.play_btn_unpressed, self.play_btn_rect
        self.game_screen.blit(img, r)

        # SETTINGS
        if self.settings_btn_rect.collidepoint(mouse_pos):
            img, r = scale_rect_center(self.settings_btn_unpressed, self.settings_btn_rect, 1.20)
        else:
            img, r = self.settings_btn_unpressed, self.settings_btn_rect
        self.game_screen.blit(img, r)

        # EXIT
        if self.exit_btn_rect.collidepoint(mouse_pos):
            img, r = scale_rect_center(self.exit_btn_unpressed, self.exit_btn_rect, 1.20)
        else:
            img, r = self.exit_btn_unpressed, self.exit_btn_rect
        self.game_screen.blit(img, r)
        # ------------------------------------------------

        # Animales decorativos
        self.game_screen.blit(self.pinguino_image, (self.pinguino_x, self.position_y))
        self.game_screen.blit(self.mono_image, (self.chango_x, self.position_y))
        self.game_screen.blit(self.bushes, (0, 0))

        # Reset del scroll (sin tocar nada)
        if abs(self.scroll_layer_2) > self.background_width: self.scroll_layer_2 = 0
        if abs(self.scroll_layer_3) > self.background_width: self.scroll_layer_3 = 0
        if abs(self.scroll_layer_4) > self.background_width: self.scroll_layer_4 = 0
        if abs(self.scroll_layer_5) > self.background_width: self.scroll_layer_5 = 0

        # Eventos de clic
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_btn_rect.collidepoint(mouse_pos):
                    return "LEVEL_SELECT"
                if self.settings_btn_rect.collidepoint(mouse_pos):
                    return "SETTINGS"
                if self.exit_btn_rect.collidepoint(mouse_pos):
                    return "SALIR"

        return "MENU"

    # ----------------------------------------------------------
    # IMÁGENES ORIGINAL + OPTIMIZADO (sin tocar orden)
    # ----------------------------------------------------------
    def setup_images(self):

        # Arbustos (frente)
        self.bushes = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "bushes.png")
        ).convert_alpha()
        self.bushes = pygame.transform.scale(
            self.bushes,
            (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        )

        # Capa 1 (fondo)
        layer1 = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "background_menu1.png")
        )
        self.layer1 = pygame.transform.scale(
            layer1, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert()
        self.background_width = self.layer1.get_width()

        # Capa 2
        layer2 = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "background_menu2.png")
        )
        self.layer2 = pygame.transform.scale(
            layer2, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert_alpha()

        # Capa 3
        layer3 = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "background_menu3.png")
        )
        self.layer3 = pygame.transform.scale(
            layer3, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert_alpha()

        # Capa 4
        layer4 = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "background_menu4.png")
        )
        self.layer4 = pygame.transform.scale(
            layer4, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert_alpha()

        # Capa 5
        layer5 = pygame.image.load(
            join(self.wd, "assets", "images", "menu", "background_menu5.png")
        )
        self.layer5 = pygame.transform.scale(
            layer5, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)
        ).convert_alpha()

        # Animales
        self.mono_image = pygame.image.load(join(self.wd, "img", "chango.png")).convert_alpha()
        self.pinguino_image = pygame.image.load(join(self.wd, "img", "pinguino.png")).convert_alpha()

        # Título
        self.title_img = pygame.image.load(join(self.wd, "img", "AnimalRescue.png")).convert_alpha()
        self.title_image = pygame.transform.scale(
            self.title_img,
            (int(self.title_img.get_width() * 0.8),
             int(self.title_img.get_height() * 0.8))
        )

    # ----------------------------------------------------------
    def setup_fonts(self):
        self.fuente_titulo = pygame.font.Font(
            join(self.wd, "src", "menus", "fuentestexto", "prstartk.ttf"), 64)
        self.fuente_botones = pygame.font.Font(
            join(self.wd, "src", "menus", "fuentestexto", "prstartk.ttf"), 24)

    # ----------------------------------------------------------
    def setup_positions(self):
        self.pinguino_rect = self.pinguino_image.get_frect()

        self.position_y = main_settings.WINDOW_HEIGHT // 2 + 96
        self.pinguino_x = main_settings.WINDOW_WIDTH + 256 - 2.08 * (main_settings.WINDOW_WIDTH // 2)
        self.chango_x = main_settings.WINDOW_WIDTH + 256 - (main_settings.WINDOW_WIDTH // 2)

    # ----------------------------------------------------------
    # BOTONES BASE (sin tocar)
    # ----------------------------------------------------------
    def setup_buttons(self, lang):

        if lang == "es":
            self.play_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_jugar_unpressed.png"))
            self.play_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_jugar_pressed.png"))

            self.settings_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_configuracion_unpressed.png"))
            self.settings_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_configuracion_pressed.png"))

            self.exit_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_salir_unpressed.png"))
            self.exit_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_salir_pressed.png"))

        else:
            self.play_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_play_unpressed.png"))
            self.play_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_play_pressed.png"))

            self.settings_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_settings_unpressed.png"))
            self.settings_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_settings_pressed.png"))

            self.exit_btn_unpressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_exit_unpressed.png"))
            self.exit_btn_pressed = pygame.image.load(join(self.wd, "assets", "images", "menu", "botones_menu", "btn_exit_pressed.png"))

        # Rects centrados
        self.play_btn_rect = self.play_btn_unpressed.get_rect(center=(main_settings.WINDOW_WIDTH // 2, main_settings.WINDOW_HEIGHT // 2 + 100))
        self.settings_btn_rect = self.settings_btn_unpressed.get_rect(center=(main_settings.WINDOW_WIDTH // 2, main_settings.WINDOW_HEIGHT // 2 + 220))
        self.exit_btn_rect = self.exit_btn_unpressed.get_rect(center=(main_settings.WINDOW_WIDTH // 2, main_settings.WINDOW_HEIGHT // 2 + 340))
