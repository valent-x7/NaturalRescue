from settings import *
from sprites import *
from pytmx import load_pygame
from os import getcwd
from os.path import join

class LevelThree:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen # -> Game Screen
        self.wd = getcwd() # -> Working Directory

        # ? Monkey Sprites
        self.monkey_spritesheet = Spritesheet(join(self.wd, "img", "monkey_spritesheet.png"))

        self.all_sprites = AllSprites3() # -> All sprites Group
        self.water_sprites = pygame.sprite.Group() # -> Sprites de agua
        self.collision_sprites = pygame.sprite.Group() # -> Sprites de colisión
        self.damage_sprites = pygame.sprite.Group() # -> Sprites de daño
        self.plant_spots = pygame.sprite.Group() # -> Lugares de cultivo

        self.setup_map() # -> Setup map

        self.translations = game.translations # -> Traducciones

    def run(self, game, events):
        self.game_screen.fill("black")

        if not game.paused:
                self.player.input(events)
                self.all_sprites.update(game.dt, events, self.player)

        self.all_sprites.center_on_target(self.player, self.map_width, self.map_height)
        self.all_sprites.draw_sprites()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "MENU"
                
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

        # ? Objects
        for obj in map.objects:
            # -> Collision Rects
            if obj.name == "ObjectCollision":
                CollisionSpriteRect((self.collision_sprites), obj.x, obj.y, obj.width, obj.height)
            
            elif obj.name == "LaboratoryObject":
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites.background_sprites), "Collision", (obj.x, obj.y), image)
            
            elif obj.name == "DepthObject":
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites.depth_sprites), "Collision", (obj.x, obj.y), image)

        # ? Create Player
        player_obj = map.get_object_by_name("Player")
        self.player = Monkey(self.monkey_spritesheet, player_obj.x, player_obj.y, (self.all_sprites, self.all_sprites.depth_sprites), self.collision_sprites, 
                            self.water_sprites, self.damage_sprites, self.plant_spots)