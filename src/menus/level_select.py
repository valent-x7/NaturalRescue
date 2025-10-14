import sys 
import os 
from ui.button import Button
import pygame 
from ui.utils import get_text

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

        # ? Dibujar botones
        self.level1_btn.draw()
        self.level2_btn.draw()
        self.level3_btn.draw()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "MENU"
                
            # ? Manejar niveles
            elif self.level1_btn.is_clicked(event):
                return "LEVEL_1" # -> Nivel 1
            
            elif self.level2_btn.is_clicked(event):
                return "LEVEL_2"
                
        return "LEVEL_SELECT"

    def setup_images(self):
        bg = pygame.image.load("assets/images/fondo2.png")
        self.background = pygame.transform.scale(bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert()

    def setup_fonts(self):
        self.fuente_pixel = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 40)

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