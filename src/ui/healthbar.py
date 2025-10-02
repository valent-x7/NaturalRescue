import pygame

class HealthBar():
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

        self.border = 2
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "#1E1E1E", 
                         (self.x - self.border, self.y - self.border, self.w + (2 * self.border), self.h + (2 * self.border)))
        pygame.draw.rect(surface, "#8B0000", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "#00A82D", (self.x, self.y, self.w * ratio, self.h))