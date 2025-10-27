import pygame
from settings import *
from sprites import Penguin, Sprite
from os import getcwd
from sprites import *
from pytmx import load_pygame

class Level_two:
    def __init__(self, game, screen):
        self.game_screen = screen
        self.game = game
        self.wd = getcwd()
        self.penguin_spritesheet = Spritesheet(join(self.wd, "img", "penguin_spritesheet.png"))
        
        self.zoom = 1  # Un poco de zoom
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.level_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Cargar fondo (más grande para permitir movimiento)
        bg_original = pygame.image.load(join(self.wd, 'img', 'bgiceberg.png'))
        self.bg_width = bg_original.get_width() * 2  # Fondo más ancho
        self.bg_height = bg_original.get_height() * 2  # Fondo más alto
        
        # Posición de la cámara
        self.camera_x = 0
        self.camera_y = 0

        self.all_sprites = pygame.sprite.LayeredUpdates()
        
        self.setup_map(["Fondo", "Capa iceberg", "FondoRoca", "Estructura", "Agua"])
        self.penguin = Penguin(256, 256, self.penguin_spritesheet)
        self.all_sprites.add(self.penguin, layer=4)
        self.setup_decor("Decoración")

    def run(self, game, events):
        self.game_screen.blit(self.bg, (0, 0))

    def setup_map(self, layersList):
        # layersList = ["Fondo", "Capa iceberg", "FondoRoca", "Estructura", "Agua", "Decoración"]
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "ice.tmx"))

        for layer_name in layersList:
            layer = map.get_layer_by_name(layer_name)
            for x, y, image in layer.tiles():
                pos = (x * TILE, y * TILE)
                if layer_name == "Estructura":
                    CollisionSprite(
                        (self.all_sprites, self.collision_sprites),
                        "Estructura",
                        pos,
                        image
                    )
                if layer_name == "Agua":
                    DamageSprite(
                        (self.all_sprites, self.damage_sprites),
                        pos,
                        image
                    )
                else:
                    Sprite(self.all_sprites, pos, image)

    def setup_decor(self, Layer):
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "ice.tmx"))

        layer = map.get_layer_by_name(Layer)
        for x, y, image in layer.tiles():
            pos = (x * TILE, y * TILE)
            decor_sprite = Sprite(self.all_sprites, pos, image)
            self.all_sprites.add(decor_sprite, layer=10)

    def update_camera(self):
        # Centrar la cámara en el pingüino
        target_x = self.penguin.rect.centerx - WINDOW_WIDTH // 2
        target_y = self.penguin.rect.centery - WINDOW_HEIGHT // 2
        
        # Suavizar el movimiento de la cámara (opcional)
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Limitar la cámara a los bordes del fondo
        self.camera_x = max(0, min(self.camera_x, self.bg_width - WINDOW_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.bg_height - WINDOW_HEIGHT))

    def draw_level2(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "MENU"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        running = False
                        return "LEVEL_SELECT"
                    elif event.key == pygame.K_ESCAPE:
                        return "SALIR"  
                     
            self.penguin.update(self.collision_sprites, self.game.dt)

            if self.penguin.alive:
                damage_collisions = pygame.sprite.spritecollide(self.penguin, self.damage_sprites, False)
            
            if damage_collisions:
                self.penguin.damage()

            self.update_camera()

            # Dibujar fondo con desplazamiento de cámara
            # self.level_surface.blit(self.bg, (-self.camera_x, -self.camera_y))
            
            # Dibujar sprites con desplazamiento de cámara
            for sprite in self.all_sprites:
                adjusted_pos = (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y)
                self.level_surface.blit(sprite.image, adjusted_pos)

            # Aplicar zoom
            zoomed_surface = pygame.transform.smoothscale(
                self.level_surface,
                (int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom))
            )

            # Centrar en pantalla (teniendo en cuenta el zoom)
            x_offset = (zoomed_surface.get_width() - WINDOW_WIDTH) // 2
            y_offset = (zoomed_surface.get_height() - WINDOW_HEIGHT) // 2
            self.game_screen.blit(zoomed_surface, (-x_offset, -y_offset))

            pygame.display.flip()
            clock.tick(60)

        return "LEVEL_2"

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(131,208,212)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))