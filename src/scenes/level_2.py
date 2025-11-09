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

        # Spritesheets y recursos
        self.penguin_spritesheet = Spritesheet(path.join(self.wd, "img", "penguin_spritesheet.png"))
        map_path = path.join(self.wd, "assets", "maps", "tmx", "ice.tmx")
        self.map = load_pygame(map_path)
        self.level_width = self.map.width * TILE
        self.level_height = self.map.height * TILE

        # --- Cámara y Zoom ---
        self.zoom = 2.5
        self.visible_w = int(WINDOW_WIDTH / self.zoom)
        self.visible_h = int(WINDOW_HEIGHT / self.zoom)

        # --- Fondos con parallax ---
        bg_original = pygame.image.load(path.join(self.wd, 'img', 'bgiceberg.png')).convert()
        iceberg_bg = pygame.image.load(path.join(self.wd, 'img', 'icebergbg.png')).convert_alpha()

        ZOOMED_W, ZOOMED_H = int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom)
        self.bg_far = pygame.transform.scale(bg_original, (ZOOMED_W*0.6, ZOOMED_H*0.6))
        self.bg_near = pygame.transform.scale(iceberg_bg, (ZOOMED_W, ZOOMED_H))
        self.parallax_bg_factor = 0.2
        self.parallax_ice_factor = 0.5

        # --- Grupos de Sprites ---
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.static_sprites = pygame.sprite.Group()
        self.dynamic_sprites = pygame.sprite.Group()
        self.win_sprites = pygame.sprite.Group()

        # --- Cargar mapa ---
        self.setup_map(["FondoRoca", "Estructura", "Agua"])
        self.setup_decor("Decoración")

        # --- Jugador ---
        self.penguin_start_pos = (TILE * 8, TILE * 28)
        self.penguin = Penguin(*self.penguin_start_pos, self.penguin_spritesheet)
        self.all_sprites.add(self.penguin, layer=6)
        self.dynamic_sprites.add(self.penguin)

        # --- Helicóptero (meta) ---
        self.helicopter = Helicopter((TILE * 31, -TILE * 3), self.penguin)
        self.all_sprites.add(self.helicopter, layer=10)
        self.dynamic_sprites.add(self.helicopter)
        self.win_sprites.add(self.helicopter)

        # --- Huevos ---
        self.eggs_group = pygame.sprite.Group()
        for pos in [(40*TILE, 23*TILE), (56*TILE, 8*TILE), (7*TILE, 16*TILE), (18*TILE, 4*TILE), (58*TILE, 16*TILE)]:
            egg = Egg(pos)
            self.all_sprites.add(egg, layer=12)
            self.eggs_group.add(egg)
            self.dynamic_sprites.add(egg)

        # --- Enemigo Agua ---
        self.setup_water()

        # --- UI ---
        self.setup_ui()

        # --- Cámara y caché ---
        self.level_surface = pygame.Surface((self.visible_w, self.visible_h), pygame.SRCALPHA)
        self.static_sprites_cache = pygame.Surface((self.level_width, self.level_height), pygame.SRCALPHA)
        self.create_static_cache()
        self.camera_x, self.camera_y = 0, max(0, self.level_height - self.visible_h)
        self.precalculate_masks()

    # ====================== SETUPS ======================

    def setup_map(self, layersList):
        for layer_name in layersList:
            layer = self.map.get_layer_by_name(layer_name)
            for x, y, image in layer.tiles():
                pos = (x * TILE, y * TILE)
                if layer_name == "Estructura":
                    CollisionSprite((self.all_sprites, self.collision_sprites, self.static_sprites),
                                    "Estructura", pos, image)
                elif layer_name == "Agua":
                    DamageSprite_2((self.all_sprites, self.damage_sprites, self.static_sprites),
                                   pos, image)
                elif layer_name == "FondoRoca":
                    # Aseguramos que se dibuje al fondo y se cachee
                    fondo = Sprite(self.all_sprites, pos, image)
                    self.all_sprites.add(fondo, layer=1)
                    self.static_sprites.add(fondo)
                else:
                    Sprite(self.all_sprites, pos, image)

    def setup_decor(self, layer_name):
        layer = self.map.get_layer_by_name(layer_name)
        for x, y, image in layer.tiles():
            pos = (x * TILE, y * TILE)
            decor = Sprite(self.all_sprites, pos, image)
            self.all_sprites.add(decor, layer=12)
            self.static_sprites.add(decor)

    def setup_water(self):
        start_pos = (0, self.level_height)
        self.water = WaterEnemy(start_pos, self.penguin)
        scaled_width = self.level_width
        water_img_height = self.water.image.get_height()

        self.water.frames = [
            pygame.transform.scale(frame, (scaled_width, water_img_height))
            for frame in self.water.frames
        ]
        self.water.image = self.water.frames[self.water.current_frame]
        self.water.rect = self.water.image.get_rect(topleft=start_pos)
        self.all_sprites.add(self.water, layer=12)
        self.damage_sprites.add(self.water)
        self.dynamic_sprites.add(self.water)

    def setup_ui(self):
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 225, "#00d5ff")

    def create_static_cache(self):
        for sprite in self.static_sprites:
            if hasattr(sprite, 'rect') and sprite.rect:
                self.static_sprites_cache.blit(sprite.image, sprite.rect.topleft)

    def precalculate_masks(self):
        for group in [self.damage_sprites, self.eggs_group]:
            for s in group:
                if hasattr(s, 'image'):
                    s.mask = pygame.mask.from_surface(s.image)
        if hasattr(self.penguin, 'image'):
            self.penguin.mask = pygame.mask.from_surface(self.penguin.image)
        if hasattr(self.helicopter, 'image'):
            self.helicopter.mask = pygame.mask.from_surface(self.helicopter.image)

    # ====================== ACTUALIZACIÓN ======================

    def update(self, dt):
        """Actualiza toda la lógica del nivel."""
        self.all_sprites.update(dt, self.collision_sprites)

        next_state = None  # ← estado de cambio

        if self.penguin.alive:
            result = self.handle_egg_collision()
            if result == "WINSCREEN":
                next_state = "WINSCREEN"

            self.handle_water_collision()

        self.update_camera()
        self.timebar.update()

        return next_state  # ← devolvemos el estado si aplica

    # ====================== DIBUJO ======================

    def draw_level(self):
        """Dibuja todo el nivel en pantalla."""
        far_x = -self.camera_x * self.parallax_bg_factor
        near_x = -self.camera_x * self.parallax_ice_factor
        far_x = max(-self.bg_far.get_width() + WINDOW_WIDTH, min(0, far_x))
        near_x = max(-self.bg_near.get_width() + WINDOW_WIDTH, min(0, near_x))

        self.game_screen.blit(self.bg_far, (far_x, 0))
        self.game_screen.blit(self.bg_near, (near_x, 0))
        self.level_surface.fill((0, 0, 0, 0))

        src_rect = pygame.Rect(self.camera_x, self.camera_y, self.visible_w, self.visible_h)
        self.level_surface.blit(self.static_sprites_cache, (0, 0), src_rect)

        for sprite in self.dynamic_sprites:
            pos = (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y)
            if isinstance(sprite, WaterEnemy):
                pos = (0 - self.camera_x, sprite.rect.y - self.camera_y)
            self.level_surface.blit(sprite.image, pos)

        scaled_level = pygame.transform.scale(self.level_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game_screen.blit(scaled_level, (0, 0))
        self.timebar.draw(self.game_screen)
        self.draw_lives()

    # ====================== LOOP PRINCIPAL ======================

    def run(self):
        """Bucle principal del nivel."""
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(60) / 1000.0

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "SALIR"
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return "SALIR"
                    if e.key == pygame.K_m:
                        return "LEVEL_SELECT"
                    if e.key == pygame.K_r:
                        return "RESTART"

            # Lógica y renderizado
            next_state = self.update(dt)
            if next_state == "WINSCREEN":
                return "WINSCREEN"

            self.draw_level()
            pygame.display.flip()

            if not self.penguin.alive:
                return "GAMEOVER"

        return "LEVEL_2"


    # ====================== COLISIONES Y OTROS ======================

    def update_camera(self):
        visible_w, visible_h = self.visible_w, self.visible_h
        target_x = self.penguin.rect.centerx - visible_w / 2
        target_y = self.penguin.rect.centery - visible_h / 2
        self.camera_x = max(0, min(target_x, self.level_width - visible_w))
        self.camera_y = max(0, min(target_y, self.level_height - visible_h))

    def collide_with_mask(self, a, b):
        if not hasattr(a, 'mask') or not hasattr(b, 'mask'):
            return False
        if not a.rect.colliderect(b.rect):
            return False
        offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
        return a.mask.overlap(b.mask, offset) is not None

    def handle_water_collision(self):
        if not (self.penguin.alive and not self.penguin.is_dying and not self.penguin.invulnerable):
            return

        # Verificar colisiones con cualquier sprite de daño
        for dmg in self.damage_sprites:
            if self.collide_with_mask(self.penguin, dmg):
                self.penguin.damage()
                if self.penguin.current_lives > 0:
                    self.reset_level()
                break

    def handle_egg_collision(self):
        for egg in pygame.sprite.spritecollide(self.penguin, self.eggs_group, False):
            if self.collide_with_mask(self.penguin, egg):
                self.eggs_group.remove(egg)
                self.all_sprites.remove(egg)
                self.dynamic_sprites.remove(egg)
                self.penguin.collect()
                self.penguin.eggs += 1

        if self.penguin.eggs >= 5:
            print("Has terminado de recoger los huevos")
            self.penguin.can_win = True


    def reset_level(self):
        print(f"¡Vida perdida! Vidas restantes: {self.penguin.current_lives}")
        self.penguin.reset(*self.penguin_start_pos)
        self.water.reset()
        self.camera_x, self.camera_y = 0, max(0, self.level_height - self.visible_h)

    def draw_lives(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Vidas: {self.penguin.current_lives}", True, (255, 255, 255))
        self.game_screen.blit(text, (10, 40))
