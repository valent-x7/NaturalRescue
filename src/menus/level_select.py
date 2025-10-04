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


# ? Dibujamos la pantalla de selección de niveles
def draw_level_select(screen, events, translations, current_lang):

    bg = pygame.image.load("assets/images/fondo2.png")
    bg = pygame.transform.scale(bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
    screen.blit(bg, (0,0))

    # ? Fuentes de texto estilo 8 bit
    fuente_pixel = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 40)

    # ? Título de la pantalla
    title_text = fuente_pixel.render(get_text(translations, current_lang, "level-select-title"), True, (255, 255, 255))
    text_rect = title_text.get_rect(center=(main_settings.WINDOW_WIDTH / 2, 100))
    screen.blit(title_text, text_rect)

    # ? Ancho y espacio entre los botones
    button_width = 500
    button_height = 150
    spacing = 50

    # ? Calculamos la posición inicial para centrarlos horizontalmente
    total_width = (button_width * 3) + (spacing * 2)
    start_x = (main_settings.WINDOW_WIDTH / 2) - (total_width / 2)
    center_y = 380

    # ? Botones para los niveles
    level1_btn = Button(screen, start_x, center_y, button_width, button_height, get_text(translations, current_lang, "level-select-level-1"), fuente_pixel, '#3b82f6',  '#1d4ed8')
    level2_btn = Button(screen, start_x + button_width + spacing, center_y, button_width, button_height, get_text(translations, current_lang, "level-select-level-2"), fuente_pixel, '#ef4444', '#dc2626')
    level3_btn = Button(screen, start_x + 2*(button_width + spacing), center_y, button_width, button_height, get_text(translations, current_lang, "level-select-level-3"), fuente_pixel, '#22c55e','#16a34a')

    # ? Dibujamos los botones en la pantalla
    level1_btn.draw()
    level2_btn.draw()
    level3_btn.draw()

    # ? Recorremos los eventos
    for event in events:

        # ? Devolver al menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"

        # ? Manejar niveles
        elif level1_btn.is_clicked(event):
            return "LEVEL_1"
        elif level2_btn.is_clicked(event):
            pass
            # return "LEVEL_2"
        elif level3_btn.is_clicked(event):
            pass
            # return "LEVEL_3"

    return "LEVEL_SELECT"