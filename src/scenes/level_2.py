import pygame
from settings import *
from sprites import Penguin
from os import getcwd
from os.path import join
from sprites import *

class Level_two:
    def __init__(self, game, screen):
        self.game_screen = screen
        self.game = game
        self.wd = getcwd()
        
        self.penguin_spritesheet = Spritesheet(join(self.wd, "img", "penguin_spritesheet.png"))
        
        bg_original = pygame.image.load(join(self.wd, 'img', 'bgiceberg.png')).convert()
        self.bg = pygame.transform.scale(bg_original, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.translations = game.translations
        
        self.setup_level()

    def setup_level(self):
        self.penguin = Penguin(256, 256, self.penguin_spritesheet)
        
        self.platforms = [
            Platform(100, 400, 200, 20),
            Platform(300, 500, 200, 20),
            Platform(340, 600, 200, 20),
            Platform(340, 700, 200, 20),
        ]
        
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.penguin)
        self.all_sprites.add(self.platforms)
        
        self.platform_group = pygame.sprite.Group(self.platforms)
        
        self.running = False

    def run(self, game, events):
        """✅ OPTIMIZADO: Método unificado que funciona con el bucle principal del juego"""
        self.game_screen.blit(self.bg, (0, 0))
        
        if game:
            self.penguin.update(self.platforms, game.dt)
            
            self.all_sprites.draw(self.game_screen)
            
        return self.handle_events(events)

    def handle_events(self, events):
        """✅ OPTIMIZADO: Manejar eventos de forma más organizada"""
        for event in events:
            if event.type == pygame.QUIT:
                return "SALIR"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "LEVEL_SELECT"
                    
                if event.key == pygame.K_ESCAPE:
                    return "SALIR"
        
        return "LEVEL_2"
    
    def draw_level2(self):
        """✅ MEJORADO: Versión mejorada del bucle original (si lo necesitas)"""
        clock = pygame.time.Clock()
        
        if not hasattr(self, 'penguin'):
            self.setup_level()
        
        self.running = True
        
        while self.running:
            dt = clock.tick(60) / 1000.0
            
            events = pygame.event.get()
            new_state = self.process_events(events)
            if new_state:
                return new_state
            
            self.penguin.update(self.platforms, dt)
            
            self.game_screen.blit(self.bg, (0, 0))
            self.all_sprites.draw(self.game_screen)
            
            pygame.display.flip()
            
        return "LEVEL_2"

    def process_events(self, events):
        """✅ EXTRACTO: Procesamiento de eventos para draw_level2"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "MENU"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.running = False
                    return "LEVEL_SELECT"

                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "SALIR"
        return None

    def cleanup(self):
        """Limpiar recursos cuando se cambia de nivel"""
        if hasattr(self, 'all_sprites'):
            self.all_sprites.empty()
        self.running = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(131, 208, 212)):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill(color)
        
        self.rect = self.image.get_frect(topleft=(x, y))
        
        pygame.draw.rect(self.image, (100, 180, 200), self.image.get_rect(), 2)