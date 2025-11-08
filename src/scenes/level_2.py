import pygame
from settings import *
from os import getcwd, path
from sprites import *
from pytmx import load_pygame
from ui.timebar import TimeBar

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

        bg_original = pygame.image.load(path.join(self.wd, 'img', 'bgiceberg.png')).convert()
        self.bg_og = pygame.transform.scale(bg_original, (ZOOMED_W, ZOOMED_H))

        iceberg_bg = pygame.image.load(path.join(self.wd, 'img', 'icebergbg.png')).convert_alpha()
        self.ice_bg = pygame.transform.scale(iceberg_bg, (ZOOMED_W, ZOOMED_H))

        self.bg_width = ZOOMED_W
        self.bg_height = ZOOMED_H

        self.parallax_bg_factor = 0.2
        self.parallax_ice_factor = 0.5

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.static_sprites = pygame.sprite.Group()
        self.dynamic_sprites = pygame.sprite.Group()

        self.setup_map(["FondoRoca", "Estructura", "Agua"])
        self.setup_decor("Decoración")

        self.penguin_start_pos = (TILE *8, TILE*28)
        self.penguin = Penguin(self.penguin_start_pos[0], self.penguin_start_pos[1], self.penguin_spritesheet)
        self.all_sprites.add(self.penguin, layer=6)
        self.dynamic_sprites.add(self.penguin)

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
            self.dynamic_sprites.add(egg)
        
        water_start_x_map = 0
        water_start_y_map = self.level_height

        self.water = WaterEnemy((water_start_x_map, water_start_y_map), self.penguin)

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
        self.dynamic_sprites.add(self.water)
        
        self.level_surface = pygame.Surface((int(WINDOW_WIDTH / self.zoom), int(WINDOW_HEIGHT / self.zoom)), pygame.SRCALPHA)
        self.zoomed_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.camera_x = 0
        self.camera_y = self.level_height - (WINDOW_HEIGHT / self.zoom)
        self.camera_y = max(0, self.camera_y)

        self.setup_ui()
        
        self.static_sprites_cache = pygame.Surface((self.level_width, self.level_height), pygame.SRCALPHA)
        self.create_static_cache()
        
        self.x_offset = (self.zoomed_surface.get_width() - WINDOW_WIDTH) // 2
        self.y_offset = (self.zoomed_surface.get_height() - WINDOW_HEIGHT) // 2
        
        self.precalculate_masks()

    def setup_map(self, layersList):
        map = load_pygame(path.join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        for layer_name in layersList:
            layer = map.get_layer_by_name(layer_name)
            for x, y, image in layer.tiles():
                pos = (x * TILE, y * TILE)
                if layer_name == "Estructura":
                    sprite = CollisionSprite(
                        (self.all_sprites, self.collision_sprites, self.static_sprites),
                        "Estructura",
                        pos,
                        image
                    )
                elif layer_name == "Agua":
                    sprite = DamageSprite_2(
                        (self.all_sprites, self.damage_sprites, self.static_sprites),
                        pos,
                        image
                    )
                else:
                    sprite = Sprite(self.all_sprites, pos, image)
                    self.static_sprites.add(sprite)

    def setup_decor(self, Layer):
        map = load_pygame(path.join(self.wd, "assets", "maps", "tmx", "ice.tmx"))
        layer = map.get_layer_by_name(Layer)
        for x, y, image in layer.tiles():
            pos = (x * TILE, y * TILE)
            decor_sprite = Sprite(self.all_sprites, pos, image)
            self.all_sprites.add(decor_sprite, layer=12)
            self.static_sprites.add(decor_sprite)

    def setup_ui(self):
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 225, "#00d5ff")

    def create_static_cache(self):    
        for sprite in self.static_sprites:
             if hasattr(sprite, 'rect') and sprite.rect is not None:
                self.static_sprites_cache.blit(sprite.image, sprite.rect.topleft)

    def precalculate_masks(self):
        if hasattr(self.penguin, 'image'):
            self.penguin.mask = pygame.mask.from_surface(self.penguin.image)

        for sprite in self.damage_sprites:
            if hasattr(sprite, 'image'):
                sprite.mask = pygame.mask.from_surface(sprite.image)

        for egg in self.eggs_group:
            if hasattr(egg, 'image'):
                egg.mask = pygame.mask.from_surface(egg.image)

    def update_camera(self):
        visible_width = WINDOW_WIDTH / self.zoom
        visible_height = WINDOW_HEIGHT / self.zoom
        target_x = self.penguin.rect.centerx - (visible_width / 2)
        target_y = self.penguin.rect.centery - (visible_height / 2)
        
        self.camera_x = target_x
        self.camera_y = target_y
        
        camera_x_max = self.level_width - visible_width
        self.camera_x = max(0, min(self.camera_x, camera_x_max))

        camera_y_max = self.level_height - visible_height
        self.camera_y = max(0, min(self.camera_y, camera_y_max))
        
    def collide_with_mask(self, sprite1, sprite2):
        if not hasattr(sprite1, 'mask') or not hasattr(sprite2, 'mask'):
            return False 
        if not sprite1.rect.colliderect(sprite2.rect):
            return False
        
        offset_x = sprite2.rect.x - sprite1.rect.x
        offset_y = sprite2.rect.y - sprite1.rect.y
        return sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y)) is not None

    def handle_water_collision(self):
        if not self.penguin.alive or self.penguin.is_dying or self.penguin.invulnerable:
            return False
    
        if self.water in self.damage_sprites and self.collide_with_mask(self.penguin, self.water):
            self.penguin.damage()
            if self.penguin.current_lives > 0:
                self.reset_level()
            return True
        
        for water_tile in [s for s in self.damage_sprites if not isinstance(s, WaterEnemy)]:
             if self.collide_with_mask(self.penguin, water_tile):
                self.penguin.damage()
                if self.penguin.current_lives > 0:
                    self.reset_level()
                return True

        return False

    def reset_level(self):
        print(f"¡Vida perdida! Vidas restantes: {self.penguin.current_lives}")

        self.penguin.reset(self.penguin_start_pos[0], self.penguin_start_pos[1])

        for egg in self.eggs_group:
            if not egg.alive():
                self.eggs_group.add(egg)
                self.all_sprites.add(egg, layer=12)
                self.dynamic_sprites.add(egg)

        self.water.reset()
        
        self.camera_x = 0
        self.camera_y = self.level_height - (WINDOW_HEIGHT / self.zoom)
        self.camera_y = max(0, self.camera_y)
    
    def handle_egg_collision(self):
        collided_eggs = pygame.sprite.spritecollide(self.penguin, self.eggs_group, False)

        for egg in collided_eggs:
            if self.collide_with_mask(self.penguin, egg):
                self.eggs_group.remove(egg)
                self.all_sprites.remove(egg)
                self.dynamic_sprites.remove(egg)
                self.penguin.collect()
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
            
            self.all_sprites.update(dt, self.collision_sprites)
            if self.penguin.alive:
                self.handle_egg_collision()
                self.handle_water_collision()
            
            if not self.penguin.alive and not self.penguin.is_dying:
                return "GAMEOVER"
            
            self.update_camera()

            self.game_screen.fill((0, 0, 0))
            
            far_x_offset = -self.camera_x * self.parallax_bg_factor
            near_x_offset = -self.camera_x * self.parallax_ice_factor
            
            far_x_offset = max(-self.bg_width + WINDOW_WIDTH, min(0, far_x_offset))
            near_x_offset = max(-self.bg_width + WINDOW_WIDTH, min(0, near_x_offset))
            
            self.game_screen.blit(self.bg_og, (far_x_offset, 0))
            self.game_screen.blit(self.ice_bg, (near_x_offset, 0))
            
            self.level_surface.fill((0, 0, 0, 0))
            
            src_rect = pygame.Rect(
                self.camera_x, 
                self.camera_y, 
                WINDOW_WIDTH / self.zoom, 
                WINDOW_HEIGHT / self.zoom
            )
            
            self.level_surface.blit(self.static_sprites_cache, (0, 0), src_rect)
            
            for sprite in self.dynamic_sprites:
                adjusted_pos = (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y)
                
                if isinstance(sprite, WaterEnemy) and hasattr(sprite, 'rect') and sprite.rect:
                    adjusted_water_pos = (0 - self.camera_x, sprite.rect.y - self.camera_y)
                    self.level_surface.blit(sprite.image, adjusted_water_pos)
                    continue

                self.level_surface.blit(sprite.image, adjusted_pos)
            
            scaled_level = pygame.transform.scale(
                self.level_surface,
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
            self.game_screen.blit(scaled_level, (0, 0))
            
            self.timebar.draw(self.game_screen)
            self.timebar.update()
            self.draw_lives()
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
    
    def draw_lives(self):
        font = pygame.font.Font(None, 36)
        lives_text = f"Vidas: {self.penguin.current_lives}"
        text_surface = font.render(lives_text, True, (255, 255, 255))
        self.game_screen.blit(text_surface, (10, 40))