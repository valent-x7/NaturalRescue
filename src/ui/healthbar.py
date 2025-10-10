import pygame
from ui.utils import draw_text
from settings import TITLE_FONT_PATH

class HealthBar():
    def __init__(self, x, y, w, h, max_hp, player_image):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

        # ? Player Image
        self.player_image = player_image

        self.border = 2
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp

        # ? Monkey Image
        surface.blit(self.player_image, [6, self.y - 4])

        # ? HealthBar
        pygame.draw.rect(surface, "#1E1E1E", 
                         (self.x - self.border, self.y - self.border, self.w + (2 * self.border), self.h + (2 * self.border)))
        pygame.draw.rect(surface, "#8B0000", (self.x, self.y, self.w, self.h))

        if ratio <= 0.1:
            color = "#FF0000"
        elif ratio <= 0.5:
            color = "#FFFF00"
        else:
            color = "#00A82D"
        
        pygame.draw.rect(surface, color, (self.x, self.y, self.w * ratio, self.h))

        # ? Health Text
        draw_text(surface, TITLE_FONT_PATH, 16, f"{self.hp} / {self.max_hp}", "white", self.x + self.w / 2, self.y - self.h / 2)