from settings import *
from sprites import *
from pytmx import load_pygame
from ui.utils import draw_text, get_text
from os import getcwd
from os.path import join
from random import choice

class LevelThree:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen # -> Game Screen
        self.wd = getcwd() # -> Working Directory

        # ? Scientist Sprites
        self.scientist_spritesheet = Spritesheet(join(self.wd, "img", "scientist_spritesheet.png"))

        self.all_sprites = AllSprites3() # -> All sprites Group
        self.water_sprites = pygame.sprite.Group() # -> Sprites de agua
        self.collision_sprites = pygame.sprite.Group() # -> Sprites de colisión
        self.damage_sprites = pygame.sprite.Group() # -> Sprites de daño
        self.valve_sprites = pygame.sprite.Group() # -> Valvulas
        self.enemy_sprites = pygame.sprite.Group() # -> Enemigos

        self.setup_map() # -> Setup map

        self.translations = game.translations # -> Traducciones

    def run(self, game, events):
        self.game_screen.fill("black")

        if not game.paused:
                self.player.input(events)
                self.all_sprites.update(game.dt, events, self.player)

        self.all_sprites.center_on_target(self.player, self.map_width, self.map_height)
        self.all_sprites.draw_sprites()

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
                    return "MENU"
                elif event.key == pygame.K_p:
                    game.paused = not game.paused # -> Invertimos el valor de pausa
            
            elif event.type == self.enemy_event and len(self.enemy_sprites) < 3:
                Ghost((self.all_sprites, self.all_sprites.depth_sprites, self.enemy_sprites), choice(self.enemy_spawn_coords), self.player)
                
        return "LEVEL_3"

    def setup_map(self):
        # -> Map Direction
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "lab.tmx"))
        
        # > Medidas del mapa
        self.map_width = map.width * TILE
        self.map_height = map.height * TILE

        # ? Layers
        for layer_name in ["Ground", "Decoration"]:
            layer = map.get_layer_by_name(layer_name)

            # -> Create Sprites taking layer name
            for x, y, image in layer.tiles():
                if layer.name == "Ground" or layer.name == "Decoration":
                    Sprite(self.all_sprites.background_sprites, (x * TILE, y * TILE), image)

        self.enemy_spawn_coords = [] # -> Spawn de enemigos

        # ? Objects
        for obj in map.objects:
            # -> Collision Rects
            if obj.name == "ObjectCollision":
                CollisionSpriteRect((self.collision_sprites), obj.x, obj.y, obj.width, obj.height)
            
            elif obj.name == "LaboratoryObject": # -> Laboratory Objects
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites.background_sprites), "Collision", (obj.x, obj.y), image)
            
            elif obj.name == "DepthObject": # -> Objectos en base al centro de su eje y
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites.depth_sprites), "Collision", (obj.x, obj.y), image)
            
            elif obj.name == "Valve Position": # -> Valvulas
                Valve((self.all_sprites, self.all_sprites.depth_sprites, self.valve_sprites), (obj.x, obj.y))
            
            elif obj.name == "Ghost": # -> Coordenadas de enemigos
                self.enemy_spawn_coords.append((obj.x, obj.y))

        # ? Create Player
        player_obj = map.get_object_by_name("Player")
        self.player = Scientist(self.scientist_spritesheet, (self.all_sprites, self.all_sprites.depth_sprites),
                                (player_obj.x, player_obj.y), self.collision_sprites)
        
        # ? Enemy Event
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 3000) # -> Evento de enemigos cada 3 sg