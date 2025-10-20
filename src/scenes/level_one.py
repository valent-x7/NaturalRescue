from settings import *
from sprites import *
from ui.healthbar import HealthBar
from ui.timebar import TimeBar
from ui.item import TreeSprout, PlayerWaterBar, AcornItem
from pytmx import load_pygame
from os import getcwd
from os.path import join
from ui.utils import get_text, draw_text
from random import choice
from textwrap import wrap

class LevelOne:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen # -> Pantalla del juego
        self.wd = getcwd() # -> Working Directory

        # ? Monkey Sprites
        self.monkey_spritesheet = Spritesheet(join(self.wd, "img", "monkey_spritesheet.png"))

        # -> Grupos de sprites
        self.all_sprites = AllSprites()
        self.water_sprites = pygame.sprite.Group() # -> Sprites de agua
        self.collision_sprites = pygame.sprite.Group() # -> Sprites de colisión
        self.damage_sprites = pygame.sprite.Group() # -> Sprites de daño
        self.plant_spots = pygame.sprite.Group() # -> Lugares de cultivo
        self.acorn_sprites = pygame.sprite.Group() # -> Bellotas
        self.enemy_sprites = pygame.sprite.Group() # -> Enemigos

        self.setup_map() # -> Crear mapa
        self.setup_ui() # -> Crear elementos de UI
        
        self.translations = game.translations # -> Traducciones

        self.game_over = False
        self.finished_level = False

    def run(self, game, events):
        self.game_screen.fill("black")

        # ? Dibujamos juego
        if game:
            # -> Definimos la vida en base a la del jugador
            self.healthbar.hp = self.player.health

            # ? Si el juego NO esta pausado
            if not game.paused:
                self.player.input(events)
                self.all_sprites.update(game.dt, events, self.player)
                self.timebar.update()
                self.waterbar_item.update(self.player.water_amount)

            self.all_sprites.center_on_target(self.player, self.map_width, self.map_height)
            self.all_sprites.draw_sprites()

            water_item_key = self.waterbar_item.get_status() # -> Definir clave del tanque de agua

            # ? Draw UI
            self.healthbar.draw(self.game_screen) # -> Vida
            self.timebar.draw(self.game_screen) # -> Barra de tiempo
            self.treesprout_item.draw(self.game_screen, get_text(self.translations, game.current_lang, "tree-sprout"),
                                      self.player.seeds) # -> Brotes de árbol
            self.waterbar_item.draw(self.game_screen, get_text(self.translations, game.current_lang, "water-tank"), 
                                    get_text(self.translations, game.current_lang, water_item_key)) # -> Tanque de agua
            self.acorn_item.draw(self.game_screen, get_text(self.translations, game.current_lang, "acorn"), self.player.acorns)
            
            # -> Check new state
            new_state = self.check_new_state()

            self.draw_message(game, self.game_screen)

            # ? Si el juego esta pausado
            if game.paused:
                draw_text(self.game_screen, TITLE_FONT_PATH, 64,
                        get_text(self.translations, game.current_lang, "paused-title"),
                        "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
                draw_text(self.game_screen, TITLE_FONT_PATH, 36,
                        get_text(self.translations, game.current_lang, "paused-description"),
                        "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    game.paused = False
                    return "LEVEL_SELECT" # -> Return level select state
                elif event.key == pygame.K_p:
                    game.paused = not game.paused # -> Invertimos el valor de pausa

            # ? Crear bellotas
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game.paused:
                self.player.shoot((self.all_sprites, self.acorn_sprites), self.player, event.pos,
                                  self.all_sprites.camera_offset, self.all_sprites.zoom)
            
            # ? Crear enemigos
            elif event.type == self.enemy_event and len(self.enemy_sprites) < 5:
                Enemy((self.all_sprites, self.enemy_sprites), choice(self.spawn_enemies_cords), self.player,
                      self.collision_sprites, self.water_sprites, self.plant_spots, self.acorn_sprites)
                
        return new_state

    def setup_image_for_ui(self):
        monkey_img = pygame.image.load(join(self.wd, "img", "chango.png"))
        self.monkey_image = pygame.transform.scale(monkey_img, (42, 42)).convert_alpha()

    def setup_map(self):
        # -> Get map direction
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "bosque.tmx"))

        # ? Layers
        for layer_name in ["Ground", "Decoration", "WaterCollision", "Collision"]:
            layer = map.get_layer_by_name(layer_name)

            # -> Create Sprites taking layer name
            for x, y, image in layer.tiles():
                if layer.name == "Ground" or layer.name == "Decoration" or layer.name == "Collision":
                    Sprite(self.all_sprites, (x * TILE, y * TILE), image)
                elif layer_name == "WaterCollision":
                    WaterCollisionSprite((self.all_sprites, self.water_sprites), "Limit",
                                         (x * TILE, y * TILE), image)

        # -> Enemies Coords
        self.spawn_enemies_cords = []

        # ? Objects
        for obj in map.objects:
            # -> Trees
            if obj.name in ["Tree", "Sign", "Bush"]:
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites, self.collision_sprites), "Collision", (obj.x, obj.y), image)

            # -> Branches
            elif obj.name == "Branch":
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    DamageSprite((self.all_sprites, self.damage_sprites), (obj.x, obj.y), image)

            # -> PlantSpots
            elif obj.name == "Plant Position":
                PlantSpot((self.all_sprites, self.plant_spots), obj.x, obj.y)
            
            elif obj.name == "ObjectCollision":
                CollisionSpriteRect((self.all_sprites, self.collision_sprites), obj.x, obj.y, obj.width, obj.height)
            
            # -> Enemies Coords
            elif obj.name == "Enemy":
                self.spawn_enemies_cords.append((obj.x, obj.y)) # -> Guardamos las coords en la lista

        self.map_width = map.width * TILE
        self.map_height = map.height * TILE

        # ? Create Player
        player_obj = map.get_object_by_name("Player")
        self.player = Monkey(self.monkey_spritesheet, player_obj.x, player_obj.y, self.all_sprites, self.collision_sprites, 
                            self.water_sprites, self.damage_sprites, self.plant_spots)
        
        # ? Enemy Event
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 3000) # -> Evento de enemigos cada 3 sg

    def setup_ui(self):
        self.setup_image_for_ui() # -> Imagenes para la UI

        self.healthbar = HealthBar(64, 78, 64 * 6, 32, MONKEY_HEALTH, self.monkey_image) # -> Barra de vida
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 225) # -> Tiempo

        self.treesprout_item = TreeSprout(join(self.wd, "assets", "images", "items", "brote.png")) # -> Brote de arbol
        self.waterbar_item = PlayerWaterBar() # -> Tanque de agua
        self.acorn_item = AcornItem(join(self.wd, "assets", "images", "items", "acorn.png")) # -> Bellota

    def check_new_state(self):
        if self.player.trees >= 6:
            self.finished_level = True
            return "WINSCREEN" # -> Return winscreen state
        elif self.healthbar.hp <= 0 or self.timebar.t <= 0:
            self.game_over = True
            return "GAMEOVER" # -> Return gameover state
        return "LEVEL_1" # -> Return same state
    
    def draw_message(self, game, screen):
        #  Mostrar texto en rectángulo por 5 segundos
        if not hasattr(game, "tutorial_start_time"):
            game.tutorial_start_time = pygame.time.get_ticks()

        elapsed = (pygame.time.get_ticks() - game.tutorial_start_time) / 1000
        if elapsed < 10:
            message = get_text(
                self.translations,
                game.current_lang,
                "mission-text"
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