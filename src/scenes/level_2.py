import pygame
from settings import *
from os import getcwd, path
from sprites import *
from ui.button import ImageButtonUI, ButtonUI
from pytmx import load_pygame
from ui.timebar import TimeBar
from ui.utils import draw_text, get_text
from ui.item import EggItem, LivesDisplay
from textwrap import wrap

class Level_two:

    def __init__(self, game, screen):
        self.game_screen = screen
        self.game = game
        self.wd = getcwd()

        # Spritesheets y recursos
        self.penguin_spritesheet = Spritesheet(
            path.join(self.wd, "img", "penguin_spritesheet.png")
        )
        self.penguin_icon_path = path.join(
            self.wd, "assets", "images", "items", "penguinheart.png"
        )
        map_path = path.join(self.wd, "assets", "maps", "tmx", "ice.tmx")
        self.map = load_pygame(map_path)
        self.level_width = self.map.width * TILE
        self.level_height = self.map.height * TILE

        self.translations = self.game.translations
        # --- Cámara y Zoom ---
        self.zoom = 2.5
        self.visible_w = int(WINDOW_WIDTH / self.zoom)
        self.visible_h = int(WINDOW_HEIGHT / self.zoom)

        # --- Fondos con parallax ---
        bg_original = pygame.image.load(
            path.join(self.wd, "img", "bgiceberg.png")
        ).convert()
        iceberg_bg = pygame.image.load(
            path.join(self.wd, "img", "icebergbg.png")
        ).convert_alpha()

        ZOOMED_W, ZOOMED_H = int(WINDOW_WIDTH * self.zoom), int(
            WINDOW_HEIGHT * self.zoom
        )
        self.bg_far = pygame.transform.scale(
            bg_original, (ZOOMED_W * 0.6, ZOOMED_H * 0.6)
        )
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

        # <--- CAMBIO IMPORTANTE: Pasamos self.game al Pingüino
        self.penguin = Penguin(
            self.game, *self.penguin_start_pos, self.penguin_spritesheet
        )

        self.all_sprites.add(self.penguin, layer=6)
        self.dynamic_sprites.add(self.penguin)

        # --- Helicóptero (meta) ---
        # (Si el helicóptero tiene sonido, también pásale self.game, si no, déjalo así)
        self.helicopter = Helicopter((TILE * 31, -TILE * 3), self.penguin)

        self.all_sprites.add(self.helicopter, layer=10)
        self.dynamic_sprites.add(self.helicopter)
        self.win_sprites.add(self.helicopter)

        # --- Huevos ---
        self.eggs_group = pygame.sprite.Group()
        for pos in [
            (40 * TILE, 23 * TILE),
            (56 * TILE, 8 * TILE),
            (7 * TILE, 16 * TILE),
            (18 * TILE, 4 * TILE),
            (58 * TILE, 16 * TILE),
        ]:
            egg = Egg(pos)
            self.all_sprites.add(egg, layer=12)
            self.eggs_group.add(egg)
            self.dynamic_sprites.add(egg)

        # --- Enemigo Agua ---
        self.setup_water()

        # --- UI ---
        self.setup_ui()

        # --- Cámara y caché ---
        self.level_surface = pygame.Surface(
            (self.visible_w, self.visible_h), pygame.SRCALPHA
        )
        self.static_sprites_cache = pygame.Surface(
            (self.level_width, self.level_height), pygame.SRCALPHA
        )
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
        self.water = WaterEnemy(self.game, start_pos, self.penguin, self.game.current_difficulty)
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
        self.egg_item = EggItem(os.path.join(self.wd, "assets", "images", "items", "egg.png"))
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 100, "#00d5ff")
        self.lives_display = LivesDisplay(self.penguin_icon_path)

        # ? Botones de Reanudar, pausar y quitar
        self.pause_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "paused.png"), (WINDOW_WIDTH - 105, 40), (96, 96))
        self.resume_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "resume.png"), (WINDOW_WIDTH - 169, 40), (96, 96))
        self.quit_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "quit.png"), (WINDOW_WIDTH - 233, 40), (96, 96))
        # ? PopUp
        self.scrim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.scrim.fill((0, 0, 0, 150))
        self.popup_rect = pygame.FRect(0, 0, WINDOW_WIDTH / 2 + 125, WINDOW_HEIGHT / 3)
        self.popup_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        # -> PopUpButtons
        self.exit_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 - 155, WINDOW_HEIGHT / 2 + 85), "#e32227", "#f24449", "idk", 200, 45)
        self.go_back_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 + 155, WINDOW_HEIGHT / 2 + 85), "#228b22", "#2ecc40", "idk", 200, 45)

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

    def update(self, dt, paused, showing_quit_pop):
        """Actualiza toda la lógica del nivel."""
        if not paused and not showing_quit_pop:
            self.all_sprites.update(dt, self.collision_sprites)

            next_state = None  # ← estado de cambio

            if self.penguin.alive:
                self.handle_egg_collision()
                self.handle_water_collision()

                result = self.handle_helicopter_collision()
                if result == "WINSCREEN":
                    next_state = "WINSCREEN"

            self.update_camera()
            self.timebar.update()

            return next_state  # ← devolvemos el estado si aplica

    # ====================== DIBUJO ======================

    def draw_level(self, game):
        """Dibuja todo el nivel en pantalla."""
        far_x = -self.camera_x * self.parallax_bg_factor
        near_x = -self.camera_x * self.parallax_ice_factor
        far_x = max(-self.bg_far.get_width() + WINDOW_WIDTH, min(0, far_x))
        near_x = max(-self.bg_near.get_width() + WINDOW_WIDTH, min(0, near_x))

        self.game_screen.blit(self.bg_far, (far_x, -64))
        self.game_screen.blit(self.bg_near, (near_x, -512))
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
        self.egg_item.draw(self.game_screen, get_text(self.translations, self.game.current_lang, "Huevos"), self.penguin.eggs)

        # --- Botones de UI --- #
        self.resume_button.draw() # -> Reanudar
        self.pause_button.draw() # -> Pausar
        self.quit_button.draw() # -> Quitar

        self.draw_lives()
        self.draw_messages(self.game, self.game_screen, ["mission-text-2"])

        if game.paused: # -> Juego pausado
            draw_text(self.game_screen, TITLE_FONT_PATH, 64,
                    get_text(self.translations, game.current_lang, "paused-title"),
                    "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
            draw_text(self.game_screen, TITLE_FONT_PATH, 36,
                    get_text(self.translations, game.current_lang, "paused-description"),
                    "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

        if game.showing_quit_pop: # -> PopUp de salida
            self.game_screen.blit(self.scrim, [0, 0])
            pygame.draw.rect(self.game_screen, "#282D32", self.popup_rect)
            pygame.draw.rect(self.game_screen, "#969696", self.popup_rect, 2)

            draw_text(self.game_screen, TITLE_FONT_PATH, 24, # -> Titulo
                    get_text(self.translations, game.current_lang, "exit-game-notice-title") , "yellow",
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 80)
            draw_text(self.game_screen, TITLE_FONT_PATH, 20, # -> Descripción
                    get_text(self.translations, game.current_lang, "exit-game-notice-description") , "white",
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 30)
            draw_text(self.game_screen, TITLE_FONT_PATH, 18, # -> Elección
                    get_text(self.translations, game.current_lang, "exit-game-notice-prompt") , "#C8C8C8",
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2  + 20)

            self.exit_btn.draw()
            self.go_back_btn.draw()
            draw_text(self.game_screen, TITLE_FONT_PATH, 14, get_text(self.translations, game.current_lang, "exit-btn-exit"), "white", WINDOW_WIDTH / 2 - 155, WINDOW_HEIGHT / 2 + 85)
            draw_text(self.game_screen, TITLE_FONT_PATH, 14, get_text(self.translations, game.current_lang, "exit-btn-go-back"), "white", WINDOW_WIDTH / 2 + 155, WINDOW_HEIGHT / 2 + 85)

    # ====================== LOOP PRINCIPAL ======================

    def run(self, game):
        """Bucle principal del nivel."""
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(60) / 1000.0

            for e in pygame.event.get():
                if game.showing_quit_pop:
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_y:
                            game.showing_quit_pop = False
                            game.paused = False
                            pygame.mixer.stop()
                            game.unload_current_level() # -> Eliminar nivel
                            return "MENU" # -> Salir al menú

                        elif e.key == pygame.K_n:
                            game.showing_quit_pop = False

                    elif self.exit_btn.is_clicked(e):
                        game.showing_quit_pop = False
                        game.paused = False
                        pygame.mixer.stop()
                        game.unload_current_level() # -> Eliminar nivel
                        return "MENU" # -> Salir al menú

                    elif self.go_back_btn.is_clicked(e):
                        game.showing_quit_pop = False

                else:
                    if e.type == pygame.QUIT:
                        return "SALIR"
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_m and not game.paused:
                            self.water.water_sfx.stop()
                            game.showing_quit_pop = True
                        elif e.key == pygame.K_p and not game.showing_quit_pop:
                            game.paused = not game.paused # -> Invertir el valor de pausa

                        elif e.key == pygame.K_ESCAPE:
                            return "SALIR"

                    elif self.resume_button.is_clicked(e) and game.paused:
                        game.paused = False

                    elif self.pause_button.is_clicked(e) and not game.paused:
                        game.paused = True # -> Pausar juego

                    elif self.quit_button.is_clicked(e) and not game.paused:
                        game.showing_quit_pop = True

            # Lógica y renderizado
            next_state = self.update(dt, game.paused, game.showing_quit_pop)
            if next_state == "WINSCREEN":
                return "WINSCREEN"

            self.draw_level(game)
            pygame.display.flip()

            if not self.penguin.alive:
                self.water.water_sfx.stop()
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
                self.water.rect.y += 32
                self.water.y_float += 32
                self.penguin.eggs += 1

        if self.penguin.eggs >= 5:
            self.penguin.can_win = True

    def handle_helicopter_collision(self):
        if self.penguin.can_win:
            if self.collide_with_mask(self.penguin, self.helicopter):
                self.water.water_sfx.stop()
                return "WINSCREEN"
        return None

    def reset_level(self):
        self.penguin.reset(*self.penguin_start_pos)
        self.water.reset()
        self.camera_x, self.camera_y = 0, max(0, self.level_height - self.visible_h)

    def draw_lives(self):
        self.lives_display.draw(self.game_screen, self.penguin.current_lives)

    def draw_messages(self, game, screen, messages):
        #  Mostrar texto en rectángulo por 5 segundos
        if not hasattr(self, "message_state"):
            self.message_state = {
                "messages_list": messages,
                "index": 0,
                "start-time": pygame.time.get_ticks()
            }

        state = self.message_state

        if state["index"] >= len(state["messages_list"]):
            return

        elapsed = (pygame.time.get_ticks() - state["start-time"]) / 1000

        if elapsed >= 6:
            state["index"] += 1
            state["start-time"] = pygame.time.get_ticks()

            if state["index"] >= len(state["messages_list"]):
                return

        key_message = state["messages_list"][state["index"]]

        message = get_text(
            self.translations,
            game.current_lang,
            key_message
        )

        # Dividir el texto en líneas cortas
        wrapped_text = wrap(message, width=50)
        font = pygame.font.Font(TITLE_FONT_PATH, 22)
        line_height = font.size("Tg")[1]
        text_height = line_height * len(wrapped_text) + 20
        text_width = max(font.size(line)[0] for line in wrapped_text) + 40

        # Crear rectángulo semitransparente
        rect_x = (WINDOW_WIDTH - text_width) // 2
        rect_y = 30
        rect_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
        rect_surface.fill((0, 0, 0, 160))  # Negro con transparencia

        # Dibujar rectángulo
        screen.blit(rect_surface, (rect_x, rect_y))

        # Dibujar texto dentro del rectángulo
        y_offset = rect_y + 10
        for line in wrapped_text:
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=y_offset)
            screen.blit(text_surface, text_rect)
            y_offset += line_height
