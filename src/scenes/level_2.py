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
        self.water_sprite = pygame.image.load(join(self.wd, "img", "watersrote.png"))
        
        self.zoom = 1
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        
        # Cargar el mapa y sprites PRIMERO
        self.setup_map(["Fondo", "Capa iceberg", "FondoRoca", "Estructura", "Agua"])
        self.penguin = Penguin(8*TILE, 28*TILE, self.penguin_spritesheet)
        self.all_sprites.add(self.penguin, layer=6)
        self.setup_decor("Decoración")
        
        # Obtener tamaño del mapa desde el archivo TMX
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        self.level_width = map.width * TILE
        self.level_height = map.height * TILE
        
        # print(f"Tamaño del nivel: {self.level_width}x{self.level_height}")
        # print(f"Posición inicial del pingüino: ({8*TILE}, {28*TILE})")
        
        # Precalcular superficies - IMPORTANTE: usar nivel completo para el cache
        self.level_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.zoomed_surface = pygame.Surface((int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom)))
        
        # Cargar fondo
        bg_original = pygame.image.load(join(self.wd, 'img', 'bgiceberg.png')).convert_alpha()
        self.bg_width = bg_original.get_width() * 2
        self.bg_height = bg_original.get_height() * 2
        self.bg = pygame.transform.scale(bg_original, (self.bg_width, self.bg_height))
        
        # POSICIÓN INICIAL DE LA CÁMARA - MOSTRAR ESQUINA INFERIOR IZQUIERDA
        self.camera_x = 0
        self.camera_y = self.level_height - WINDOW_HEIGHT  # Comenzar desde abajo
        
        print(f"Cámara inicial: ({self.camera_x}, {self.camera_y})")
        print(f"Pingüino en pantalla inicial: ({8*TILE - self.camera_x}, {28*TILE - self.camera_y})")
        
        # Cache para sprites estáticos
        self.static_sprites_cache = pygame.Surface((self.level_width, self.level_height), pygame.SRCALPHA)
        self.create_static_cache()
        
        # Precalcular offsets para el zoom
        self.x_offset = (self.zoomed_surface.get_width() - WINDOW_WIDTH) // 2 
        self.y_offset = (self.zoomed_surface.get_height() - WINDOW_HEIGHT) // 2 
        
        # Precalcular máscaras
        self.precalculate_masks()

    def setup_map(self, layersList):
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
                elif layer_name == "Agua":
                    DamageSprite_2(
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
            self.all_sprites.add(decor_sprite, layer=12)

    def create_static_cache(self):
        print("Creando cache estática...")
        # Dibujar TODOS los sprites estáticos en la cache
        for sprite in self.all_sprites:
            if sprite != self.penguin:  # Excluir al jugador
                self.static_sprites_cache.blit(sprite.image, sprite.rect.topleft)
        print("Cache estática creada correctamente")

    def precalculate_masks(self):
        if hasattr(self.penguin, 'image'):
            self.penguin.mask = pygame.mask.from_surface(self.penguin.image)
        
        for sprite in self.damage_sprites:
            if hasattr(sprite, 'image'):
                sprite.mask = pygame.mask.from_surface(sprite.image)

    def update_camera(self):
        # Calcular posición objetivo para centrar al pingüino
        target_x = self.penguin.rect.centerx - WINDOW_WIDTH // 2
        target_y = self.penguin.rect.centery - WINDOW_HEIGHT // 2
        
        # MOVIMIENTO INSTANTÁNEO (sin suavizado para debugging)
        self.camera_x = target_x
        self.camera_y = target_y
        
        # Limitar la cámara para que no se salga del mapa
        self.camera_x = max(0, min(self.camera_x, self.level_width - WINDOW_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.level_height - WINDOW_HEIGHT))
        
        # Debug info
        penguin_screen_x = self.penguin.rect.x - self.camera_x
        penguin_screen_y = self.penguin.rect.y - self.camera_y
        print(f"Cámara: ({self.camera_x:.1f}, {self.camera_y:.1f}) | Pingüino en pantalla: ({penguin_screen_x:.1f}, {penguin_screen_y:.1f})")

    def collide_with_mask(self, sprite1, sprite2):
        if not sprite1.rect.colliderect(sprite2.rect):
            return False
        
        offset_x = sprite2.rect.x - sprite1.rect.x
        offset_y = sprite2.rect.y - sprite1.rect.y
        
        return sprite2.mask.overlap(sprite1.mask, (offset_x, offset_y)) is not None

    def handle_water_collision(self):
        water_collisions = pygame.sprite.spritecollide(
            self.penguin, 
            self.damage_sprites, 
            False,
            collided=self.collide_with_mask
        )
        
        if water_collisions:
            self.penguin.damage()

    def draw_level2(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60) / 1000.0
            
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
                    elif event.key == pygame.K_r:
                        return "RESTART"
                     
            # Actualizar jugador si está vivo
            if self.penguin.alive:
                self.penguin.update(self.collision_sprites, dt)
                self.handle_water_collision()
            else:
                return "RESTART"

            self.update_camera()

            # Limpiar superficie de nivel
            self.level_surface.fill((0, 0, 0, 0))
            
            # Dibujar el mapa visible desde el cache
            if self.static_sprites_cache:
                src_rect = pygame.Rect(
                    self.camera_x, 
                    self.camera_y, 
                    WINDOW_WIDTH, 
                    WINDOW_HEIGHT
                )
                
                # Asegurar que no nos salimos de los límites
                if src_rect.right > self.level_width:
                    src_rect.width = self.level_width - src_rect.left
                if src_rect.bottom > self.level_height:
                    src_rect.height = self.level_height - src_rect.top
                
                self.level_surface.blit(
                    self.static_sprites_cache,
                    (0, 0),
                    src_rect
                )
            
            # Dibujar jugador en posición relativa a la cámara
            if self.penguin.alive:
                adjusted_pos = (
                    self.penguin.rect.x - self.camera_x,
                    self.penguin.rect.y - self.camera_y
                )
                self.level_surface.blit(self.penguin.image, adjusted_pos)

            # Aplicar zoom a la superficie del nivel
            pygame.transform.scale(
                self.level_surface,
                (int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom)),
                self.zoomed_surface
            )

            # Dibujar la superficie con zoom centrada en la pantalla
            self.game_screen.fill((0, 0, 0))  # Fondo negro para bordes
            self.game_screen.blit(self.zoomed_surface, (-self.x_offset, -self.y_offset))
            self.game_screen.blit(self.water_sprite, (WINDOW_WIDTH-1920, WINDOW_HEIGHT-512))

            pygame.display.flip()

        return "LEVEL_2"

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(131,208,212)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))