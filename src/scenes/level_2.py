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
        
        # Obtener tamaño del mapa desde el archivo TMX
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        self.level_width = map.width * TILE
        self.level_height = map.height * TILE
        
        self.zoom = 1.0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        
        # Cargar el mapa y sprites PRIMERO
        self.setup_map(["Fondo", "Capa iceberg", "FondoRoca", "Estructura", "Agua"])
        self.penguin = Penguin(8*TILE, 28*TILE, self.penguin_spritesheet)
        
        # POSICIÓN DEL AGUA - Comenzar MUCHO más abajo para evitar colisión inicial
        water_start_x_map = 0
        water_start_y_map = self.level_height + 500  # Fuera del nivel visible inicialmente
        
        self.water = WaterEnemy((water_start_x_map, water_start_y_map), self.penguin)

        water_img_height = self.water.image.get_height()
        self.water.image = pygame.transform.scale(self.water.image, (WINDOW_WIDTH, water_img_height))
        self.water.rect = self.water.image.get_rect(topleft=(water_start_x_map, water_start_y_map))
        self.water.mask = pygame.mask.from_surface(self.water.image)

        self.all_sprites.add(self.penguin, layer=6)
        self.all_sprites.add(self.water, layer=12)
        self.setup_decor("Decoración")

        self.damage_sprites.add(self.water)
        
        print(f"Tamaño del nivel: {self.level_width}x{self.level_height}")
        print(f"Posición inicial del pingüino: ({8*TILE}, {28*TILE})")
        print(f"Posición inicial del agua: ({water_start_x_map}, {water_start_y_map})")
        print(f"Sprites en damage_sprites: {len(self.damage_sprites)}")
        
        # DEBUG: Verificar posiciones y máscaras
        print(f"Penguin rect: {self.penguin.rect}")
        print(f"Water rect: {self.water.rect}")
        print(f"Penguin mask count: {self.penguin.mask.count() if hasattr(self.penguin, 'mask') else 'No mask'}")
        print(f"Water mask count: {self.water.mask.count() if hasattr(self.water, 'mask') else 'No mask'}")
        
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
        for sprite in self.all_sprites:
            if sprite not in (self.penguin, self.water): 
                if hasattr(sprite, 'rect') and sprite.rect is not None:
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

    def collide_with_mask(self, sprite1, sprite2):
        if not hasattr(sprite1, 'mask') or not hasattr(sprite2, 'mask'):
            return False

        if not sprite1.rect.colliderect(sprite2.rect):
            return False
        
        # CORRECCIÓN: Usar los atributos correctos del rect
        offset_x = sprite2.rect.x - sprite1.rect.x
        offset_y = sprite2.rect.y - sprite1.rect.y

        return sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y)) is not None

    def handle_water_collision(self):
        # Solo verificar colisión si el pingüino está vivo y no muriendo
        if not self.penguin.alive or self.penguin.is_dying:
            return False
    
        # Verificar colisión rectangular primero (más eficiente)
        water_collision_rect = False
        for water in self.damage_sprites:
            if self.penguin.rect.colliderect(water.rect):
                water_collision_rect = True
                break
        
        if not water_collision_rect:
            return False
    
        # Luego verificar colisión por máscara pixel-perfect
        for water in self.damage_sprites:
            if self.collide_with_mask(self.penguin, water):
                print(f"¡COLISIÓN DETECTADA con agua mediante máscara!")
                self.penguin.damage()
                return True
    
        return False
    
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
                     
            # Actualizar jugador si está vivo o muriendo
            if self.penguin.alive or self.penguin.is_dying:
                self.penguin.update(self.collision_sprites, dt)

                # Solo verificar colisión con agua si está vivo (no muriendo)
                if self.penguin.alive:
                    self.handle_water_collision()

                # Actualizar el agua (debería subir gradualmente)
                if self.water:
                    self.water.update(dt)   

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
            if self.penguin.alive or self.penguin.is_dying:
                adjusted_pos = (
                    self.penguin.rect.x - self.camera_x,
                    self.penguin.rect.y - self.camera_y
                )
                self.level_surface.blit(self.penguin.image, adjusted_pos)

            # Dibujar agua en posición relativa a la cámara
            if self.water and hasattr(self.water, 'rect') and self.water.rect:
                adjusted_water_pos = (
                    0,  # El agua ocupa todo el ancho
                    self.water.rect.y - self.camera_y
                )
                self.level_surface.blit(self.water.image, adjusted_water_pos)

            # Aplicar zoom a la superficie del nivel
            pygame.transform.scale(
                self.level_surface,
                (int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom)),
                self.zoomed_surface
            )

            # Dibujar la superficie con zoom centrada en la pantalla
            self.game_screen.fill((0, 0, 0))  # Fondo negro para bordes
            self.game_screen.blit(self.zoomed_surface, (-self.x_offset, -self.y_offset))

            pygame.display.flip()

        return "LEVEL_2"

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(131,208,212)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))