from settings import *
import os

class Button:
    def __init__(self, screen, pos, font, width, height, text, thickness, image_path, image_text_spacing, base_color, hover_color=None):
        self.screen = screen
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color

        # ? Sonido de click
        working_directory = os.getcwd() 
        self.sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "button_click.mp3"))

        # Rectángulo principal del botón
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_rect.centerx = pos[0]
        self.top_rect.centery = pos[1]

        # ? Rectangulo del borde
        # Creamos el thickness rect
        self.thickness_rect = pygame.Rect(pos, (width + (2 * thickness), height + (2 * thickness)))
        # Le asignamos la posición del botón principal
        self.thickness_rect.centerx = self.top_rect.centerx
        self.thickness_rect.centery = self.top_rect.centery

        # Texto
        self.text_surface = font.render(text, True, '#fafaf9')
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.top_rect.center  # centra el texto en el botón

        # ? Imagen del botón
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.image_rect = self.image.get_frect()
        # Le asignamos posición (x, y)
        self.image_rect.x = self.top_rect.left + image_text_spacing # Espacio de la imagen y rectangulo principal
        self.image_rect.centery = self.text_rect.centery

    # Dibujar
    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        # ? Dibujamos el botón
        # Boton del borde
        pygame.draw.rect(self.screen, "black", self.thickness_rect, 0, 12)
        # Siempre dibuja el botón
        pygame.draw.rect(self.screen, self.base_color, self.top_rect, 0, 12)

        # Si hay hover, dibuja el botón con el color del hover
        if self.top_rect.collidepoint(mouse_pos) and self.hover_color:
            # Botón hover encima
            pygame.draw.rect(self.screen, self.hover_color, self.top_rect, 0, 12)

        # Dibujar texto
        self.screen.blit(self.text_surface, self.text_rect)
        # Dibujar imagen del botón
        self.screen.blit(self.image, self.image_rect)

    # Detectar clic
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.top_rect.collidepoint(event.pos):
                self.sound.play()
                return True
        return False

class ImageButtonUI:
    def __init__(self, screen: pygame.Surface, image_path, position, image_scale = None):
        self.screen = screen

        if not image_scale:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(image, image_scale).convert_alpha()

        self.rect = self.image.get_frect(topleft = position)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    # Detectar clic
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
    
class ButtonUI:
    def __init__(self, screen, position, color, hover_color, text, width, height, thickness = 2):
        self.screen = screen
        self.color = color
        self.hover_color = hover_color
        self.text = text

        self.rect = pygame.FRect(0, 0, width, height)
        self.rect.center = position

        # Creamos el thickness rect
        self.thickness_rect = pygame.FRect((0, 0), (width + (2 * thickness), height + (2 * thickness)))
        self.thickness_rect.center = position

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        # ? Dibujar borde
        pygame.draw.rect(self.screen, "black", self.thickness_rect, 0, 12)
        # ? Dibujar rect
        pygame.draw.rect(self.screen, self.color, self.rect, 0, 12)

        # Si hay hover, dibuja el botón con el color del hover
        if self.rect.collidepoint(mouse_pos):
            # Botón hover encima
            pygame.draw.rect(self.screen, self.hover_color, self.rect, 0, 12)

    # Detectar clic
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False