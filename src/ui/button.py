from settings import *

class Button:
    def __init__(self, screen, pos, font, width, height, text, base_color, hover_color=None):
        self.screen = screen
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color

        # Rectángulo del botón
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_rect.centerx = WINDOW_WIDTH // 4

        # Rectángulo de la sombra (solo se mostrará al hacer hover)
        self.bottom_rect = pygame.Rect(pos, (width, height + 2))
        self.bottom_rect.centerx = self.top_rect.centerx
        self.bottom_rect.centery = self.top_rect.centery + 2  # offset hacia abajo

        # Texto
        self.text_surface = font.render(text, True, '#fafaf9')
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.top_rect.center  # centra el texto en el botón

    # Dibujar
    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        # Siempre dibuja el botón
        pygame.draw.rect(self.screen, self.base_color, self.top_rect, 0, 12)

        # Si hay hover, dibuja sombra negra detrás y color hover
        if self.top_rect.collidepoint(mouse_pos) and self.hover_color:
            # Sombra
            pygame.draw.rect(self.screen, 'black', self.bottom_rect, 0, 12)
            # Botón hover encima
            pygame.draw.rect(self.screen, self.hover_color, self.top_rect, 0, 12)

        # Dibujar texto
        self.screen.blit(self.text_surface, self.text_rect)

    # Detectar clic
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.top_rect.collidepoint(event.pos):
                return True
        return False
