from settings import *

class Button:
    def __init__(self, screen, pos, font, width, height, text, base_color, hover_color = None):
        self.screen = screen
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color

        # ? Rectangulo superior del Texto
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_rect.centerx = WINDOW_WIDTH // 2

        # ? Rectangulo inferior
        self.bottom_rect = pygame.Rect(pos, (width, height + 2))
        self.bottom_rect.centerx = WINDOW_WIDTH // 2

        # ? Texto
        self.text_surface = font.render(text, True, '#fafaf9')
        self.text_rect = self.text_surface.get_frect()

        # ? Centramos el texto en el centro del rectangulo inicial
        self.text_rect.centerx = self.top_rect.centerx
        self.text_rect.centery = self.top_rect.centery

    # Dibujar
    def draw(self):

        # ? Checar hover
        if self.top_rect.collidepoint(pygame.mouse.get_pos()):
            if self.hover_color is not None:
                # ? Rectangulo (Pantalla, Color, Forma, Fill, Borde)
                pygame.draw.rect(self.screen, 'black', self.bottom_rect, 0, 12)
                pygame.draw.rect(self.screen, self.hover_color, self.top_rect, 0, 12)
            else:
                pygame.draw.rect(self.screen, self.base_color, self.top_rect, 0, 12)
        else:
            pygame.draw.rect(self.screen, self.base_color, self.top_rect, 0, 12)

        # ? Dibujar texto
        self.screen.blit(self.text_surface, self.text_rect)

    # Click
    def is_clicked(self, event):
        # ? Tecla izquierda del mouse presionada
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.top_rect.collidepoint(event.pos):
                return True
        return False