import pygame
from settings import *
from sprites import Penguin
from os import getcwd
from sprites import *

class Level_two:
    def __init__(self, game, screen):
        self.game_screen = screen
        self.game = game
        
        self.wd = getcwd() # -> Working Directory

        # ? Penguin Sprites
        self.penguin_spritesheet = Spritesheet(join(self.wd, "img", "penguin_spritesheet.png"))
        self.bg = pygame.image.load(join(self.wd, 'img', 'bg-ice.png'))
        self.translations = game.translations

    def run(self, game, events):
        self.game_screen.blit(self.bg, (0,0))

        if game:
            pass

    def draw_level2(self):
        clock = pygame.time.Clock()
        penguin = Penguin(256, 256, self.penguin_spritesheet)
        all_sprites = pygame.sprite.Group(penguin)
        platforms = [
           Platform(100, 400, 200, 20),
           Platform(300, 500, 200 , 20),
           Platform(340, 600, 200 , 20),
           Platform(340, 700, 200 , 20),
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

                   if event.key == pygame.K_ESCAPE:
                       return "SALIR"  
                     
            penguin.update(platforms, self.game.dt)

            self.game_screen.blit(self.bg, (0,0))
            all_sprites.draw(self.game_screen)

            pygame.display.flip()
            clock.tick(60)
        return "LEVEL_2"

    

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(131,208,212)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

