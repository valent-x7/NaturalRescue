import sys 
import os 
from ui.button import Button as ImageButton
import pygame 
from ui.utils import get_text, draw_text, set_difficulty
from math import sin
from settings import *

sys.path.append(os.path.abspath(".."))
import settings as main_settings

class Button:
    def __init__(self, screen, x, y, width, height, text, font, color, hover_color):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = pygame.Color(color)
        self.hover_color = pygame.Color(hover_color)
        self.current_color = self.color

        # ? Musica
        working_directory = os.getcwd()
        self.sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "button_click.mp3"))

    def draw(self):
        # ? Cambiamos el color al pasar el mouse
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

        # ? Dibujamos el fondo del botón
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=12)

        # ? Renderizamos texto centrado
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.sound.play()
                return True
        return False

class LevelSelectMenu:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen # -> Definir pantalla del juego
        self.translations = game.translations # -> Cargar traducciones

        self.wd = os.getcwd() # -> Working Directory

        self.setup_images() # -> Imagenes
        self.setup_fonts() # -> Fuentes
        self.setup_buttons(game.current_lang) # -> Configurar botones en base al idioma

    def run(self, game, events):
        # ? Background
        self.game_screen.blit(self.background, [0, 0])
        
        # ? Título de la pantalla
        title_text = self.fuente_pixel.render(get_text(game.translations, game.current_lang, "level-select-title"), True, (255, 255, 255))
        text_rect = title_text.get_rect(center=(main_settings.WINDOW_WIDTH / 2, 100))
        self.game_screen.blit(title_text, text_rect)

        # ? Titulo de dificultad
        difficulty_title = self.difficulty_title_font.render(get_text(game.translations, game.current_lang, "select-difficulty-title"), True, "white")
        difficulty_title_rect = difficulty_title.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 420))
        self.game_screen.blit(difficulty_title, difficulty_title_rect)

        # ? Definir la posición de la flechita de dificultad
        if game.current_difficulty == "normal":
            self.arrow_rect.centery = WINDOW_HEIGHT - 300
        else:
            self.arrow_rect.centery = WINDOW_HEIGHT - 180

        # ? Dibujar flechita
        self.game_screen.blit(self.arrow_image, self.arrow_rect)

        # ? Dibujar botones
        self.level1_btn.draw()
        self.level2_btn.draw()
        self.level3_btn.draw()
        self.normal_difficulty_btn.draw()
        self.advanced_difficulty_btn.draw()

        # Mensaje para regresar al menú
        exit_hint = get_text(game.translations, game.current_lang, "press-m-to-menu")
        t = pygame.time.get_ticks() / 500
        alpha = sin(t) * 0.5 + 0.5
        color_blink = [int(100 + alpha * 155)] * 3  

        draw_text(self.game_screen, TITLE_FONT_PATH, 24, exit_hint,
                color_blink, WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "MENU"
                
            # ? Manejar niveles
            elif self.level1_btn.is_clicked(event):
                return "START_LEVEL_1" # -> Nivel 1
            
            elif self.level2_btn.is_clicked(event):
                return "LEVEL_2" # -> Nivel 2
            
            elif self.level3_btn.is_clicked(event):
                return "LEVEL_3" # -> Nivel 3
            
            elif self.normal_difficulty_btn.is_clicked(event):
                set_difficulty("config.json", "normal")
                game.current_difficulty = "normal"

            elif self.advanced_difficulty_btn.is_clicked(event):
                set_difficulty("config.json", "advanced")
                game.current_difficulty = "advanced"
                
        return "LEVEL_SELECT"

    def setup_images(self):
        bg = pygame.image.load("assets/images/fondo2.png")
        self.background = pygame.transform.scale(bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert()

        # Arrow Image
        arrow_img = pygame.image.load(join(self.wd, "assets", "images", "ajustes", "flecha.png"))
        self.arrow_image = pygame.transform.scale(arrow_img, (96, 96)).convert_alpha()
        self.arrow_rect = self.arrow_image.get_frect() # -> Get Rect from image
        self.arrow_rect.centerx = WINDOW_WIDTH / 2 - self.arrow_rect.width - 140 # -> Define x position

    def setup_fonts(self):
        self.fuente_pixel = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 40)
        self.difficulty_title_font = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 30)
        self.change_difficulty_font = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 24)

    def setup_buttons(self, lang):
        # ? Ancho y espacio entre los botones
        button_width = 500
        button_height = 150
        spacing = 50

        # ? Calculamos la posición inicial para centrarlos horizontalmente
        total_width = (button_width * 3) + (spacing * 2)
        start_x = (main_settings.WINDOW_WIDTH / 2) - (total_width / 2)
        center_y = 380

        self.level1_btn = Button(self.game_screen, start_x, center_y, button_width, button_height,
                                 get_text(self.translations, lang, "level-select-level-1"),
                                 self.fuente_pixel, '#3b82f6',  '#1d4ed8')
        
        self.level2_btn = Button(self.game_screen, start_x + button_width + spacing, center_y, button_width, button_height,
                                 get_text(self.translations, lang, "level-select-level-2"),
                                 self.fuente_pixel, '#ef4444', '#dc2626')
        
        self.level3_btn = Button(self.game_screen, start_x + 2 * (button_width + spacing), center_y, button_width, button_height,
                                 get_text(self.translations, lang, "level-select-level-3"),
                                 self.fuente_pixel, '#22c55e','#16a34a')
        
        self.normal_difficulty_btn = ImageButton(self.game_screen, (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 300), self.change_difficulty_font, 340, 90,
                                                 get_text(self.translations, lang, "normal-difficulty"), 4, join(self.wd, "assets", 'images', "level_select", "normal.png"),
                                                 15, "#FFA726", "#EF6C00")
        
        self.advanced_difficulty_btn = ImageButton(self.game_screen, (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 180), self.change_difficulty_font, 340, 90,
                                                 get_text(self.translations, lang, "advanced-difficulty"), 4, join(self.wd, "assets", 'images', "level_select", "advanced.png"),
                                                 5, "#EF5350", "#C62828")