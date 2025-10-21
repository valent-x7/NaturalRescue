from settings import *
from ui.utils import draw_text
import os

class TreeSprout:
    def __init__(self, image_path):
        self.display_surface = pygame.display.get_surface()

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100)).convert_alpha()
        self.rect = self.image.get_frect()
        self.rect.topleft = (self.display_surface.width - self.rect.width - 60, 64)

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

class PlayerWaterBar:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
            
        # Directiorio de trabajo
        working_directory = os.getcwd()

        # ? Imagenes
        self.image_state = {
            "full": os.path.join(working_directory, "assets", "images", "user-i", "full_tank.png"),
            "mid": os.path.join(working_directory, "assets", "images", "user-i", "mid_tank.png"),
            "empty": os.path.join(working_directory, "assets", "images", "user-i", "empty_tank.png")
        }

        # ? Cargamos el convert alpha de las imagenes
        self.loaded_images = {}

        for key, value in self.image_state.items():
            surf = pygame.image.load(value).convert_alpha()
            surf_scaled = pygame.transform.scale(surf, (100, 100)) # Escalamos superficie
            self.loaded_images[key] = surf_scaled # Guardamos la imagen escalada

        self.image = self.loaded_images["empty"]
        self.current_status = "water-tank-empty"

        self.rect = self.image.get_frect()
        self.rect.topleft = (self.display_surface.width - self.rect.width - 262, 64)

    def get_status(self): # -> Devuelve la clave de traducción
        return self.current_status

    def update(self, water_amount):
        if water_amount > 25:
            self.image = self.loaded_images["full"]
            self.current_status = "water-tank-full"
        elif water_amount > 0:
            self.image = self.loaded_images["mid"]
            self.current_status = "water-tank-mid"
        else:
            self.image = self.loaded_images["empty"]
            self.current_status = "water-tank-empty"

    def draw(self, screen, name_item, amount_item):
        # ? Borde del circulo
        pygame.draw.circle(screen, "#000000", (self.rect.centerx, self.rect.centery), 42)

        # ? Fondo del item
        pygame.draw.circle(screen, "#FDE68A", (self.rect.centerx, self.rect.centery), 40)

        # ? Texto del item
        draw_text(screen, TITLE_FONT_PATH, 12, name_item, "#FFFFFF", self.rect.centerx, self.rect.top - 5)

        # ? Cantidad del item
        draw_text(screen, TITLE_FONT_PATH, 12, f"{amount_item}", "#FFFFFF", self.rect.centerx + (self.rect.width / 2) + 20, self.rect.bottom - 20)

        # Imagen del item
        screen.blit(self.image, self.rect)

class AcornItem:
    def __init__(self, image_path):
        self.display_surface = pygame.display.get_surface()

        image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(image, (100, 100)).convert_alpha()

        self.rect = self.image.get_frect()
        self.rect.topleft = (self.display_surface.width - self.rect.width - 464, 64)

    def draw(self, screen, name_item, amount_item):
        # ? Borde del circulo
        pygame.draw.circle(screen, "#000000", (self.rect.centerx, self.rect.centery), 42)

        # ? Fondo del item
        pygame.draw.circle(screen, "#FDE68A", (self.rect.centerx, self.rect.centery), 40)

        # ? Texto del item
        draw_text(screen, TITLE_FONT_PATH, 12, name_item, "#FFFFFF", self.rect.centerx, self.rect.top - 10)

        # ? Cantidad del item
        draw_text(screen, TITLE_FONT_PATH, 12, f"{amount_item}", "#FFFFFF", self.rect.centerx + (self.rect.width / 2) + 20, self.rect.bottom - 20)

        screen.blit(self.image, self.rect)