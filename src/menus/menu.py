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
        self.game_screen = screen # -> Pantalla del juego
        self.wd = os.getcwd() # -> Working Directory

        self.traslations = game.translations # -> Traducciones

        self.setup_fonts() # -> Metodo que carga las fuentes de texto
        self.setup_images() # -> Carga y optimiza las imagenes

        # ? Define Scroll
        self.scroll_layer_2 = 0
        self.scroll_layer_3 = 0
        self.scroll_layer_4 = 0
        self.scroll_layer_5 = 0

        self.tiles = math.ceil(main_settings.WINDOW_WIDTH / self.background_width) + 1

        self.setup_positions() # -> Define las posiciones de las imagenes
        self.setup_buttons(game.current_lang) # -> Crea botones en base al lenguaje de game

    def run(self, game, events):
        # ? Draw Parallax Efect
        self.game_screen.blit(self.layer1, [0, 0])

        # Dibujamos capa 2
        for i in range(0, self.tiles + 1):
            self.game_screen.blit(self.layer2, (i * self.background_width + self.scroll_layer_2, 0))

        # Dibujamos capa 3
        for i in range(0, self.tiles + 1):
            self.game_screen.blit(self.layer3, (i * self.background_width + self.scroll_layer_3, 0))

        # Dibujamos capa 4
        for i in range(0, self.tiles + 1):
            self.game_screen.blit(self.layer4, (i * self.background_width + self.scroll_layer_4, 0))

        # Dibujamos capa 5
        for i in range(0, self.tiles + 1):
            self.game_screen.blit(self.layer5, (i * self.background_width + self.scroll_layer_5, 0))

        # Modificamos scroll
        self.scroll_layer_2 -= 0.2
        self.scroll_layer_3 -= 0.5
        self.scroll_layer_4 -= 1.5
        self.scroll_layer_5 -= 2.5

        
        # ? Título del videojuego
        title_rect = self.title_image.get_frect(center=(main_settings.WINDOW_WIDTH / 2, 400))
        # Dibujamos la imagen del título en pantalla
        self.game_screen.blit(self.title_image, title_rect)

        # ? Dibujamos botones del menu
        self.play_btn.draw()
        self.settings_btn.draw()
        self.exit_btn.draw()

        # ? Dibujamos el pingüino y el chango en las posiciones calculadas y asignadas previamente.
        self.game_screen.blit(self.pinguino_image, (self.pinguino_x, self.position_y))
        self.game_screen.blit(self.mono_image, (self.chango_x, self.position_y))

        # Reseteamos el scroll
        if abs(self.scroll_layer_2) > self.background_width:
            self.scroll_layer_2 = 0

        elif abs(self.scroll_layer_3) > self.background_width:
            self.scroll_layer_3 = 0

        elif abs(self.scroll_layer_4) > self.background_width:
            self.scroll_layer_4 = 0

        elif abs(self.scroll_layer_5) > self.background_width:
            self.scroll_layer_5 = 0

        # ? Recorremos eventos
        for event in events:
            if self.play_btn.is_clicked(event):
                return "LEVEL_SELECT"

            elif self.settings_btn.is_clicked(event):
                return "SETTINGS"
            elif self.exit_btn.is_clicked(event):
                return "SALIR"

        return "MENU"

    # ? Cargar imagenes
    def setup_images(self):
        # -> Layer 1
        layer1 = pygame.image.load(join(self.wd, "assets", "images", "menu", "background_menu1.png"))
        self.layer1 = pygame.transform.scale(layer1, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert()
        self.background_width = self.layer1.get_width() # -> Get background width for scroll

        # -> Layer 2
        layer2 = pygame.image.load(join(self.wd, "assets", "images", "menu", "background_menu2.png"))
        self.layer2 = pygame.transform.scale(layer2, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert_alpha()

        # -> Layer 3
        layer3 = pygame.image.load(join(self.wd, "assets", "images", "menu", "background_menu3.png"))
        self.layer3 = pygame.transform.scale(layer3, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert_alpha()       

        # -> Layer 4
        layer4 = pygame.image.load(join(self.wd, "assets", "images", "menu", "background_menu4.png"))
        self.layer4 = pygame.transform.scale(layer4, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert_alpha()

        # -> Layer 5
        layer5 = pygame.image.load(join(self.wd, "assets", "images", "menu", "background_menu5.png"))
        self.layer5 = pygame.transform.scale(layer5, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert_alpha()

        # ? Imagenes del mono y pinguino
        self.mono_image = pygame.image.load(os.path.join(self.wd, "img", "chango.png")).convert_alpha()
        self.pinguino_image = pygame.image.load(os.path.join(self.wd, "img", "pinguino.png")).convert_alpha()

        self.title_image = pygame.image.load(os.path.join(self.wd, "img", "AnimalRescue.png")).convert_alpha()

    # ? Fuentes de texto
    def setup_fonts(self):
        # Letra del titulo
        self.fuente_titulo = pygame.font.Font(join(self.wd, "src", "menus", "fuentestexto", "prstartk.ttf"), 64)
        # Letra de los botones
        self.fuente_botones = pygame.font.Font(join(self.wd, "src", "menus", "fuentestexto", "prstartk.ttf"), 24)

    # ? Posiciones de imagenes
    def setup_positions(self):
        self.pinguino_rect = self.pinguino_image.get_frect() # -> Rect de la imagen del pinguino

        # Calculamos una posición para el pingüino y asignamos una posición fija para el chango.
        self.position_y = 400
        self.pinguino_x = main_settings.WINDOW_WIDTH - self.pinguino_rect.width - 80
        self.chango_x = 900

    # ? Cargamos botones
    def setup_buttons(self, lang):
        # -> Play Button
        self.play_btn = Button(self.game_screen, (main_settings.WINDOW_WIDTH // 4, 400), self.fuente_botones, 300, 90, 
                                get_text(self.traslations, lang, "play"), 4, join(self.wd, "assets", "images", "play_icon.png"),
                                20, '#34D399', '#10B981')
      
        # -> Settings Button
        self.settings_btn = Button(self.game_screen, (main_settings.WINDOW_WIDTH // 4, 520), self.fuente_botones, 300, 90, 
                                get_text(self.traslations, lang, "settings"), 4, join(self.wd, "assets", "images", "settings_icon.png"),
                                0, '#38BDF8', '#0EA5E9')
        
        # -> Exit Button
        self.exit_btn = Button(self.game_screen, (main_settings.WINDOW_WIDTH // 4, 640), self.fuente_botones, 300, 90, 
                                get_text(self.traslations, lang, "exit"), 4, join(self.wd, "assets", "images", "salir_icon.png"),
                                20, '#FB923C', '#F97316')