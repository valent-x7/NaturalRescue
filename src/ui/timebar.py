import pygame

class TimeBar():
    def __init__(self, x, y, w, h, maxt):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.t = maxt
        self.maxt = maxt

        self.border = 2
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 500:
            self.t -= 0.5
            self.last_update = now

            if self.t < 0:
                self.t = 0

    def draw(self, surface):
        ratio = self.t / self.maxt

        if ratio <= 0.1:
            color = "#FF0000"
        elif ratio <= 0.5:
            color = "#FFFF00"
        else: 
            color = "#00FF00"

        pygame.draw.rect(surface, "#1E1E1E", (self.x - self.border, self.y - self.border, self.w + (2 * self.border), self.h + (2 * self.border)))
        pygame.draw.rect(surface, "#000000FF", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, color, (self.x, self.y, self.w * ratio, self.h))

    
    def isEnd(self):
        if self.t <= 0:  
            # Aquí irá el gameover
            pass
      