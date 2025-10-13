import pygame
from settings import *
from sprites import Penguin

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(100,255,100)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

def draw_level2(screen):
    clock = pygame.time.Clock()
    penguin = Penguin(256, 256)
    all_sprites = pygame.sprite.Group(penguin)
    platforms = [
        Platform(100, 500, 200, 20),
        Platform(300, 400, 200 , 20),
        Platform(150, 300, 200 , 20),
        Platform(250, 200, 200 , 20),
        Platform(100, 100, 200 , 20)
    ]
    platform_group = pygame.sprite.Group(platforms)
    all_sprites.add(platforms)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "MENU"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    running = False
                    return "LEVEL_SELECT"
                    
        penguin.update(platforms)
        screen.fill((30,30,60))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    return "LEVEL_2"