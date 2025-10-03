from settings import *
from ui.utils import draw_text

class TreeSprout:
    def __init__(self, image_path):

        self.display_surface = pygame.display.get_surface()

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100)).convert_alpha()
        self.rect = self.image.get_frect()
        self.rect.topleft = (self.display_surface.width / 2, self.display_surface.height - self.rect.height - 20)

    def draw(self, screen, name_item, amount_item):
        # ? Borde del circulo
        pygame.draw.circle(screen, "#000000", (self.rect.centerx, self.rect.centery), 42)

        # ? Fondo del item
        pygame.draw.circle(screen, "#FDE68A", (self.rect.centerx, self.rect.centery), 40)

        # ? Texto del item
        draw_text(screen, TITLE_FONT_PATH, 12, name_item, "#FFFFFF", self.rect.centerx, self.rect.top - 5)

        # ? Cantidad del item
        draw_text(screen, TITLE_FONT_PATH, 12, f"{amount_item}", "#FFFFFF", self.rect.centerx + (self.rect.width / 2) + 5, self.rect.bottom - 20)

        screen.blit(self.image, self.rect)