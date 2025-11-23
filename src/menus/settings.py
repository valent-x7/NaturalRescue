from settings import *
from ui.utils import draw_text, set_language, get_text
from ui.button import Button
from math import ceil
from math import sin
from os import getcwd
from os.path import join
from ui.button import ImageButtonUI
import pygame
import os


class SettingsMenu:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen  # -> Main Screen
        self.wd = getcwd()  # -> Get Working Directory

        self.translations = game.translations

        self.setup_images()  # -> Images

        # ? Scroll
        self.scroll = 0
        self.tiles = ceil(WINDOW_WIDTH / self.layer_width) + 1

        self.setup_fonts()  # -> Fonts
        self.setup_buttons(game.current_lang)  # -> Buttons

        button_pos = (WINDOW_WIDTH - 150, 50)
        button_scale = (96, 96)  # Tamaño del icono
        path_on = "assets/images/ajustes/sound_on.png"
        path_off = "assets/images/ajustes/sound_off.png"

        self.btn_sound_on = ImageButtonUI(
            self.game_screen, path_on, button_pos, button_scale
        )

        self.btn_sound_off = ImageButtonUI(
            self.game_screen, path_off, button_pos, button_scale
        )

    def run(self, game, events):
        # Draw layer 1
        self.game_screen.blit(self.layer1, [0, 0])

        # -> Draw layer 2 with parallax efect
        for i in range(0, self.tiles + 1):
            self.game_screen.blit(self.layer2, [i * self.layer_width + self.scroll, 0])

        # -> Change scroll
        self.scroll -= 2.5

        # -> Reset scroll
        if abs(self.scroll) > self.layer_width:
            self.scroll = 0

        vol_text = get_text(game.translations, game.current_lang, "settings-volume")

        # Titulo de settings
        draw_text(
            self.game_screen,
            TITLE_FONT_PATH,
            52,
            get_text(game.translations, game.current_lang, "settings-title"),
            "#FFFFFF",
            WINDOW_WIDTH / 2,
            150,
        )

        # Subtitulo de idioma
        draw_text(
            self.game_screen,
            TITLE_FONT_PATH,
            42,
            get_text(game.translations, game.current_lang, "settings-language"),
            "#FFFFFF",
            WINDOW_WIDTH / 2,
            300,
        )
        # Texto de Volumen
        draw_text(
            self.game_screen,
            TITLE_FONT_PATH,
            30,
            vol_text,
            "#FFFFFF",
            WINDOW_WIDTH - 280,
            100,
        )

        # Defimos y en base al lenguaje
        if game.current_lang == "en":
            self.arrow_rect.centery = 400
        else:
            self.arrow_rect.centery = 520

        # ? Draw arrow image
        self.game_screen.blit(self.arrow_image, self.arrow_rect)

        # ? Draw buttons
        self.english_button.draw()
        self.spanish_button.draw()

        # Mensaje para regresar al menú
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

        # Variable para guardar cuál botón está activo en este momento
        active_button = None

        if game.muted:
            self.btn_sound_off.draw()
            active_button = self.btn_sound_off
        else:
            self.btn_sound_on.draw()
            active_button = self.btn_sound_on

        # ? Events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "MENU"  # -> Change state to MENU

            elif self.english_button.is_clicked(event, game.muted):
                set_language("config.json", "en")
                game.current_lang = "en"
                game.reload_language(game.current_lang)

            elif self.spanish_button.is_clicked(event, game.muted):
                set_language("config.json", "es")
                game.current_lang = "es"
                game.reload_language(game.current_lang)

            # Checar clic en el botón de mute activo
            if active_button and active_button.is_clicked(event, game.muted):
                game.toggle_mute()

        return "SETTINGS"  # -> Leave the current state

    # ? This method will load the images
    def setup_images(self):
        # Layer 1
        layer1 = pygame.image.load(
            join(self.wd, "assets", "images", "ajustes", "background_settings1.png")
        )
        self.layer1 = pygame.transform.scale(
            layer1, (WINDOW_WIDTH, WINDOW_HEIGHT)
        ).convert()
        # -> Layer 1 width
        self.layer_width = self.layer1.get_width()

        # Layer 2
        layer2 = pygame.image.load(
            join(self.wd, "assets", "images", "ajustes", "background_settings2.png")
        )
        self.layer2 = pygame.transform.scale(
            layer2, (WINDOW_WIDTH, WINDOW_HEIGHT)
        ).convert_alpha()

        # Arrow Image
        arrow_img = pygame.image.load(
            join(self.wd, "assets", "images", "ajustes", "flecha.png")
        )
        self.arrow_image = pygame.transform.scale(arrow_img, (96, 96)).convert_alpha()
        self.arrow_rect = self.arrow_image.get_frect()  # -> Get Rect from image
        self.arrow_rect.centerx = (
            WINDOW_WIDTH / 2 - self.arrow_rect.width - 140
        )  # -> Define x position

    # ? Cargar fuentes
    def setup_fonts(self):
        # Letra de los botones
        self.fuente_botones = pygame.font.Font(
            "src/menus/fuentestexto/prstartk.ttf", 24
        )

    # ? Cargar botones con el lenguaje del juego
    def setup_buttons(self, lang):
        # English Button
        self.english_button = Button(
            self.game_screen,
            (WINDOW_WIDTH / 2, 400),
            self.fuente_botones,
            320,
            90,
            get_text(self.translations, lang, "settings-to-english"),
            4,
            join(self.wd, "assets", "images", "ajustes", "ukFlag.png"),
            10,
            "#4D96FF",
            "#6DAFFF",
        )

        # Spanish Button
        self.spanish_button = Button(
            self.game_screen,
            (WINDOW_WIDTH / 2, 520),
            self.fuente_botones,
            320,
            90,
            get_text(self.translations, lang, "settings-to-spanish"),
            4,
            join(self.wd, "assets", "images", "ajustes", "spainFlag.png"),
            10,
            "#38B000",
            "#70E000",
        )
