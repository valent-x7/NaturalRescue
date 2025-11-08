import pygame
from settings import *
from os import getcwd, path
from sprites import *
from pytmx import load_pygame

# NOTA: Se asume que las clases Spritesheet, Penguin, Egg, WaterEnemy, Sprite, 
# CollisionSprite, and DamageSprite_2 están definidas en 'sprites.py' y 
# las constantes TILE, WINDOW_WIDTH, WINDOW_HEIGHT están en 'settings.py'.

class Level_two:
    def __init__(self, game, screen):
        self.game_screen = screen
        self.game = game
        self.wd = getcwd()
        self.penguin_spritesheet = Spritesheet(path.join(self.wd, "img", "penguin_spritesheet.png"))
        
        map = load_pygame(path.join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        self.level_width = map.width * TILE
        self.level_height = map.height * TILE
        
        self.zoom = 1.8
        ZOOMED_W = int(WINDOW_WIDTH * self.zoom)
        ZOOMED_H = int(WINDOW_HEIGHT * self.zoom)

        # Cargar y escalar fondos (solo una vez)
        bg_original = pygame.image.load(path.join(self.wd, 'img', 'bgiceberg.png')).convert()
        self.bg_og = pygame.transform.scale(bg_original, (ZOOMED_W, ZOOMED_H))

        iceberg_bg = pygame.image.load(path.join(self.wd, 'img', 'icebergbg.png')).convert_alpha()
        self.ice_bg = pygame.transform.scale(iceberg_bg, (ZOOMED_W, ZOOMED_H))

        self.bg_width = ZOOMED_W
        self.bg_height = ZOOMED_H

        self.parallax_bg_factor = 0.2
        self.parallax_ice_factor = 0.5

        # --- Grupos de Sprites ---
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.static_sprites = pygame.sprite.Group() # Nuevo grupo para sprites estáticos (para caché)
        self.dynamic_sprites = pygame.sprite.Group() # Nuevo grupo para sprites dinámicos (para dibujo por frame)

        # --- Setup de Mapas y Entidades ---
        self.setup_map(["FondoRoca", "Estructura", "Agua"])
        self.setup_decor("Decoración") # Llama a setup_decor ANTES de crear al pingüino

        self.penguin = Penguin(8*TILE, 28*TILE, self.penguin_spritesheet)
        self.all_sprites.add(self.penguin, layer=6)
        self.dynamic_sprites.add(self.penguin) # El pingüino es dinámico

        EGG_POSITIONS = [
            (40*TILE, 23*TILE),
            (56*TILE, 8*TILE),
            (7*TILE, 16*TILE),
            (18*TILE, 4*TILE),
            (58*TILE, 16*TILE)
        ]

        self.eggs_group = pygame.sprite.Group()
        for pos in EGG_POSITIONS:
            egg = Egg(pos)
            self.all_sprites.add(egg, layer=12)
            self.eggs_group.add(egg)
            self.dynamic_sprites.add(egg) # Los huevos son dinámicos (o al menos se deben dibujar por separado de la caché)
        
        # Configuración del Agua (WaterEnemy)
        water_start_x_map = 0
        water_start_y_map = self.level_height

        self.water = WaterEnemy((water_start_x_map, water_start_y_map), self.penguin)

        # Re-escalado de frames del agua
        water_img_height = self.water.image.get_height()
        scaled_width = self.level_width 
        self.water.frames = [
            pygame.transform.scale(frame, (scaled_width, water_img_height)) 
            for frame in self.water.frames
        ]
        self.water.image = self.water.frames[self.water.current_frame]
        self.water.rect = self.water.image.get_rect(topleft=(water_start_x_map, water_start_y_map))
        
        self.all_sprites.add(self.water, layer=12)
        self.damage_sprites.add(self.water)
        self.dynamic_sprites.add(self.water) # El agua es dinámica/animada
        
        self.level_surface = pygame.Surface((int(WINDOW_WIDTH / self.zoom), int(WINDOW_HEIGHT / self.zoom)), pygame.SRCALPHA)
        self.zoomed_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)) # Simplificado, ya que blitteamos directamente a game_screen

        # --- Inicialización de Cámara y Caché ---
        self.camera_x = 0
        self.camera_y = self.level_height - (WINDOW_HEIGHT / self.zoom)
        self.camera_y = max(0, self.camera_y)
        
        # Caché estática del mapa - ¡Clave para la optimización!
        self.static_sprites_cache = pygame.Surface((self.level_width, self.level_height), pygame.SRCALPHA)
        self.create_static_cache()
        
        # Offsets para centrar (aunque con el reescalado final no son estrictamente necesarios)
        self.x_offset = (self.zoomed_surface.get_width() - WINDOW_WIDTH) // 2
        self.y_offset = (self.zoomed_surface.get_height() - WINDOW_HEIGHT) // 2
        
        # Pre-cálculo de máscaras (solo una vez)
        self.precalculate_masks()


    def setup_map(self, layersList):
        map = load_pygame(path.join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        for layer_name in layersList:
            layer = map.get_layer_by_name(layer_name)
            for x, y, image in layer.tiles():
                pos = (x * TILE, y * TILE)
                if layer_name == "Estructura":
                    sprite = CollisionSprite(
                        (self.all_sprites, self.collision_sprites, self.static_sprites), # Añadido a static_sprites
                        "Estructura",
                        pos,
                        image
                    )
                elif layer_name == "Agua":
                    sprite = DamageSprite_2(
                        (self.all_sprites, self.damage_sprites, self.static_sprites), # Añadido a static_sprites (solo el tile)
                        pos,
                        image
                    )
                else:
                    sprite = Sprite(self.all_sprites, pos, image)
                    self.static_sprites.add(sprite) # FondoRoca (estático)

    def setup_decor(self, Layer):
        map = load_pygame(path.join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        layer = map.get_layer_by_name(Layer)
        for x, y, image in layer.tiles():
            pos = (x * TILE, y * TILE)
            decor_sprite = Sprite(self.all_sprites, pos, image)
            self.all_sprites.add(decor_sprite, layer=12)
            self.static_sprites.add(decor_sprite) # Decoración es estática

    ## 🚀 Optimización: Crear la caché estática (mapa, colisiones, decoración)
    def create_static_cache(self):    
        # Blittear TODOS los sprites estáticos a una sola superficie grande
        for sprite in self.static_sprites:
             if hasattr(sprite, 'rect') and sprite.rect is not None:
                self.static_sprites_cache.blit(sprite.image, sprite.rect.topleft)

    ## 🧠 Optimización: Pre-calcular máscaras de colisión (solo una vez)
    def precalculate_masks(self):
        # La máscara del pingüino se recalcula en su update si cambia de frame/imagen
        if hasattr(self.penguin, 'image'):
            self.penguin.mask = pygame.mask.from_surface(self.penguin.image)

        # Máscaras de colisión de daño (agua/pinchos del mapa)
        for sprite in self.damage_sprites:
            if hasattr(sprite, 'image'):
                sprite.mask = pygame.mask.from_surface(sprite.image)

        # Máscaras de coleccionables (huevos)
        for egg in self.eggs_group:
            if hasattr(egg, 'image'):
                egg.mask = pygame.mask.from_surface(egg.image)

    def update_camera(self):
        visible_width = WINDOW_WIDTH / self.zoom
        visible_height = WINDOW_HEIGHT / self.zoom
        target_x = self.penguin.rect.centerx - (visible_width / 2)
        target_y = self.penguin.rect.centery - (visible_height / 2)
        
        # Suavizado de cámara (opcional, pero mejora la experiencia)
        # self.camera_x += (target_x - self.camera_x) * 0.1 
        # self.camera_y += (target_y - self.camera_y) * 0.1 
        self.camera_x = target_x
        self.camera_y = target_y
        
        # Límites de cámara
        camera_x_max = self.level_width - visible_width
        self.camera_x = max(0, min(self.camera_x, camera_x_max))

        camera_y_max = self.level_height - visible_height
        self.camera_y = max(0, min(self.camera_y, camera_y_max))
        
    def collide_with_mask(self, sprite1, sprite2):
        if not hasattr(sprite1, 'mask') or not hasattr(sprite2, 'mask'):
            # Si un sprite no tiene máscara (ej: sprite de mapa estático sin colisión)
            return False 
        if not sprite1.rect.colliderect(sprite2.rect):
            return False
        
        offset_x = sprite2.rect.x - sprite1.rect.x
        offset_y = sprite2.rect.y - sprite1.rect.y
        return sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y)) is not None

    def handle_water_collision(self):
        if not self.penguin.alive or self.penguin.is_dying:
            return False
    
        # Colisión con el WaterEnemy (el gran bloque de agua animado/móvil)
        if self.water in self.damage_sprites and self.collide_with_mask(self.penguin, self.water):
            self.penguin.damage()
            return True
        
        # Colisión con los tiles de Agua estáticos del mapa
        for water_tile in [s for s in self.damage_sprites if not isinstance(s, WaterEnemy)]:
             if self.collide_with_mask(self.penguin, water_tile):
                 self.penguin.damage()
                 return True

        return False
    
    def handle_egg_collision(self):
        # Usar pygame.sprite.spritecollide para colisión de rectángulos primero
        # y luego verificar la colisión de máscara si es necesario
        collided_eggs = pygame.sprite.spritecollide(self.penguin, self.eggs_group, False)

        for egg in collided_eggs:
            if self.collide_with_mask(self.penguin, egg):
                self.eggs_group.remove(egg)
                self.all_sprites.remove(egg)
                self.dynamic_sprites.remove(egg)
                self.penguin.collect()
                return True # Asumiendo que solo se recoge un huevo por frame
        return False

    def draw_level2(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "SALIR" 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        running = False
                        return "LEVEL_SELECT"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        return "SALIR"
                    elif event.key == pygame.K_r:
                        return "RESTART"
            
            # --- Lógica de Actualización ---
            self.all_sprites.update(dt, self.collision_sprites)
            if self.penguin.alive:
                self.handle_egg_collision()
                self.handle_water_collision()
            
            # Condición de Muerte
            if not self.penguin.alive and not self.penguin.is_dying:
                return "RESTART"
            
            self.update_camera()

            # --- Bucle de Dibujo Optimizado ---
            
            # 1. Dibujar Parallax (Fondos)
            self.game_screen.fill((0, 0, 0)) # Limpiar la pantalla principal
            
            far_x_offset = -self.camera_x * self.parallax_bg_factor
            near_x_offset = -self.camera_x * self.parallax_ice_factor
            
            far_x_offset = max(-self.bg_width + WINDOW_WIDTH, min(0, far_x_offset))
            near_x_offset = max(-self.bg_width + WINDOW_WIDTH, min(0, near_x_offset))
            
            self.game_screen.blit(self.bg_og, (far_x_offset, 0))
            self.game_screen.blit(self.ice_bg, (near_x_offset, 0))
            
            # 2. Copiar la sección visible del mapa estático (Caché) a la superficie de nivel
            self.level_surface.fill((0, 0, 0, 0)) # Limpiar la superficie de nivel (transparente)
            
            # Rectángulo que define la sección del mundo (cache) visible por la cámara
            src_rect = pygame.Rect(
                self.camera_x, 
                self.camera_y, 
                WINDOW_WIDTH / self.zoom, 
                WINDOW_HEIGHT / self.zoom
            )
            
            # Blittear la parte estática del mapa desde la caché
            self.level_surface.blit(self.static_sprites_cache, (0, 0), src_rect)
            
            # 3. Dibujar Sprites Dinámicos (Pingüino, Huevos, Agua animada)
            # Solo se blittean los sprites dinámicos, el resto ya está en la caché.
            # Esto reduce drásticamente el número de blits por frame.
            for sprite in self.dynamic_sprites:
                # Calculamos la posición ajustada al centro de la cámara
                adjusted_pos = (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y)
                
                # Para sprites que tienen que reescalar su imagen (como el agua en el nivel_width)
                if isinstance(sprite, WaterEnemy) and hasattr(sprite, 'rect') and sprite.rect:
                    # El agua se dibuja desde x=0 de la cache, ajustando solo la Y
                    adjusted_water_pos = (0 - self.camera_x, sprite.rect.y - self.camera_y)
                    self.level_surface.blit(sprite.image, adjusted_water_pos)
                    continue

                # Dibujar todos los demás sprites dinámicos (pingüino, huevos)
                self.level_surface.blit(sprite.image, adjusted_pos)
            
            # 4. Escalar y Dibujar a la Pantalla Principal
            scaled_level = pygame.transform.scale(
                self.level_surface,
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
            self.game_screen.blit(scaled_level, (0, 0))
            
            pygame.display.flip()

        new_state = self.check_new_states()
        if new_state != "LEVEL_2":
            return new_state

        return "LEVEL_2"
    
    def check_new_states(self):
        if not self.penguin.alive:
            return "GAMEOVER"
        else:
            return "LEVEL_2"