from settings import *
from sprites import *
from ui.healthbar import HealthBar
from ui.timebar import TimeBar
from ui.item import TreeSprout, PlayerWaterBar, AcornItem, ResourceCounter
from ui.button import ImageButtonUI, ButtonUI
from pytmx import load_pygame
from os import getcwd
from os.path import join
from ui.utils import get_text, draw_text, draw_text_optimized
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

        self.setup_sprites() # -> Preparar elementos para Sprites
        self.setup_map() # -> Crear mapa
        self.setup_ui() # -> Crear elementos de UI
        
        self.translations = game.translations # -> Traducciones

        self.setup_fonts() # -> Fonts del juego
        self.setup_text(game.current_lang)

        # ? Message
        self.message_surface = None 
        self.message_rect_pos = None

        self.was_paused = False
        self.game_over = False
        self.finished_level = False

    def run(self, game, events):
        self.game_screen.fill("black")

        should_be_paused = game.paused or game.showing_quit_pop

        if should_be_paused != self.was_paused:
            if should_be_paused:
                pygame.mixer.pause()
                pygame.mixer.music.pause()
            else:
                pygame.mixer.unpause()
                pygame.mixer.music.unpause()
            self.was_paused = should_be_paused

        # ? Dibujamos juego
        if game:
            # -> Definimos la vida en base a la del jugador
            self.healthbar.hp = self.player.health

            # ? Si el juego NO esta pausado
            if not should_be_paused:
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
            self.treesprout_item.draw(self.game_screen, self.txt_tree_sprout,
                                      self.player.seeds) # -> Brotes de árbol
            self.waterbar_item.draw(self.game_screen, self.txt_water_tank, 
                                    get_text(self.translations, game.current_lang, water_item_key)) # -> Tanque de agua
            self.acorn_item.draw(self.game_screen, self.txt_acorn, self.player.acorns)
            self.plantSpotsCounter.draw(self.game_screen, self.txt_trees, self.player.trees) 
            self.resume_button.draw()
            self.pause_button.draw()
            self.quit_button.draw()

            # -> Check new state
            new_state = self.check_new_state()

            self.draw_message(game, self.game_screen)

            # ? Si el juego esta pausado
            if game.paused:
                draw_text_optimized(self.game_screen, self.paused_title_font, self.txt_paused_title, "white", 
                                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4) # -> Titulo pausa
                draw_text_optimized(self.game_screen, self.paused_description_font, self.txt_paused_description, "white", 
                                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3) # -> Descripción pausa

        for event in events:
            if game.showing_quit_pop:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        game.showing_quit_pop = False
                        game.paused = False
                        pygame.mixer.stop()
                        game.unload_current_level() # -> Eliminar nivel
                        return "MENU" # -> Salir al menú
                    elif event.key == pygame.K_n:
                        game.showing_quit_pop = False
                
                elif self.exit_btn.is_clicked(event):
                    game.showing_quit_pop = False
                    game.paused = False
                    pygame.mixer.stop()
                    game.unload_current_level() # -> Eliminar nivel
                    return "MENU" # -> Salir al menú
                
                elif self.go_back_btn.is_clicked(event):
                    game.showing_quit_pop = False

            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m and not game.paused:
                        game.showing_quit_pop = True
                    elif event.key == pygame.K_p and not game.showing_quit_pop:
                        game.paused = not game.paused # -> Invertimos el valor de pausa
            
                elif self.resume_button.is_clicked(event) and game.paused: # -> Reanudar
                    game.paused = False

                elif self.pause_button.is_clicked(event) and not game.paused: # -> Pausar
                    game.paused = True

                elif self.quit_button.is_clicked(event) and not game.paused: # -> Salir
                    game.showing_quit_pop = True

                # ? Crear bellotas
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game.paused:
                    self.player.shoot((self.all_sprites, self.acorn_sprites), self.player, event.pos,
                                    self.all_sprites.camera_offset, self.all_sprites.zoom, self.banana_img, self.banana_throw_sound, self.banana_impact_sound)
                
                # ? Crear enemigos
                elif event.type == self.enemy_event and len(self.enemy_sprites) < 5:
                    Enemy((self.all_sprites, self.enemy_sprites), choice(self.spawn_enemies_cords), self.player,
                        self.collision_sprites, self.water_sprites, self.plant_spots, self.acorn_sprites, self.tornado_frames,
                        self.smog_frames, self.tornado_sizzle_sound, self.tornado_swoosh_sound, game.current_difficulty)
                
        if game.showing_quit_pop: # -> PopUp de salida
            self.game_screen.blit(self.scrim, [0, 0])
            pygame.draw.rect(self.game_screen, "#3E2A1E", self.popup_rect)
            pygame.draw.rect(self.game_screen, "#969696", self.popup_rect, 2)

            draw_text_optimized(self.game_screen, self.quit_title_font, self.txt_exit_title, "#F7E251", WINDOW_WIDTH / 2, 
                                WINDOW_HEIGHT / 2 - 80) # -> Titulo
            draw_text_optimized(self.game_screen, self.quit_description_font, self.txt_exit_description, "#FDF6E3", WINDOW_WIDTH / 2, 
                                WINDOW_HEIGHT / 2 - 30) # -> Descripción
            draw_text_optimized(self.game_screen, self.quit_choice_font, self.txt_exit_choice, "#A49B8D", WINDOW_WIDTH / 2, 
                                WINDOW_HEIGHT / 2 + 30) # -> Elección
            
            self.exit_btn.draw()
            self.go_back_btn.draw()

            draw_text_optimized(self.game_screen, self.quit_action_font, self.txt_btn_exit, "white", WINDOW_WIDTH / 2 - 155,
                                WINDOW_HEIGHT / 2 + 85)
            draw_text_optimized(self.game_screen, self.quit_action_font, self.txt_btn_go_back, "white", WINDOW_WIDTH / 2 + 155,
                                WINDOW_HEIGHT / 2 + 85)

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
                CollisionSpriteRect((self.collision_sprites), obj.x, obj.y, obj.width, obj.height)
            
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
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 225, "#2AFE00") # -> Tiempo

        self.treesprout_item = TreeSprout(join(self.wd, "assets", "images", "items", "brote.png")) # -> Brote de arbol
        self.waterbar_item = PlayerWaterBar() # -> Tanque de agua
        self.acorn_item = AcornItem(join(self.wd, "assets", "images", "items", "platano.png")) # -> Platano
        self.pause_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "paused.png"), (WINDOW_WIDTH - 105, 40), (96, 96))
        self.resume_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "resume.png"), (WINDOW_WIDTH - 169, 40), (96, 96))
        self.quit_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "quit.png"), (WINDOW_WIDTH - 233, 40), (96, 96))

        # ? Resources UI
        self.plantSpotsCounter = ResourceCounter(os.path.join(self.wd, "assets", "images", "items", "broteview.png"), (48, 148), (48, 48), len(self.plant_spots))

        # ? PopUp
        self.scrim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.scrim.fill((0, 0, 0, 150))
        self.popup_rect = pygame.FRect(0, 0, WINDOW_WIDTH / 2 + 125, WINDOW_HEIGHT / 3)
        self.popup_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        # -> PopUpButtons
        self.exit_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 - 155, WINDOW_HEIGHT / 2 + 85), "#C65D26", "#E07A40", "idk", 200, 45)
        self.go_back_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 + 155, WINDOW_HEIGHT / 2 + 85), "#5DA9E0", "#7DC0F0", "idk", 200, 45)

    def setup_sprites(self):
        # ? --- Platanos ---
        banana_img = pygame.image.load(os.path.join(self.wd , "assets", "images", "items", "platano.png"))
        self.banana_img = pygame.transform.scale(banana_img, (28, 28)).convert_alpha()
        self.banana_throw_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "throw.ogg"))
        self.banana_throw_sound.set_volume(0.4)
        self.banana_impact_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "impact.ogg"))
        self.banana_impact_sound.set_volume(0.8)

        # ? --- Tornados ---
        self.tornado_frames = [pygame.image.load(os.path.join(self.wd, "assets", "images", "enemies", "tornado", f"{i}.png")).convert_alpha() for i in range(1, 5)]
        self.smog_frames = [pygame.image.load(os.path.join(self.wd, "assets", "images", "enemies", "smog", f"{i}.png")).convert_alpha() for i in range(1, 4)]
        self.tornado_sizzle_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "sizzle.mp3"))
        self.tornado_swoosh_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "swoosh.mp3"))

    def setup_fonts(self):
        self.message_font = pygame.font.Font(TITLE_FONT_PATH, 22) # -> Font mensaje inicial

        self.paused_title_font = pygame.font.Font(TITLE_FONT_PATH, 64) # -> Font titulo de pausa
        self.paused_description_font = pygame.font.Font(TITLE_FONT_PATH, 36) # -> Font descripción de pausa

        # ? --- Quit Fonts ---
        self.quit_title_font = pygame.font.Font(TITLE_FONT_PATH, 24) # -> Quit Showing Title
        self.quit_description_font = pygame.font.Font(TITLE_FONT_PATH, 20) # -> Quit Showing Description
        self.quit_choice_font = pygame.font.Font(TITLE_FONT_PATH, 18) # -> Quit Showing Choice
        self.quit_action_font = pygame.font.Font(TITLE_FONT_PATH, 14) # -> Quit Showing Action

    def check_new_state(self):
        if self.player.trees >= 6:
            self.finished_level = True
            return "WINSCREEN" # -> Return winscreen state
        elif self.healthbar.hp <= 0 or self.timebar.t <= 0:
            self.game_over = True
            return "GAMEOVER" # -> Return gameover state
        return "LEVEL_1" # -> Return same state
    
    def setup_text(self, lang):
        # ? --- UI text ---
        self.txt_tree_sprout = get_text(self.translations, lang, "tree-sprout")
        self.txt_water_tank = get_text(self.translations, lang, "water-tank")
        self.txt_acorn = get_text(self.translations, lang, "acorn")
        self.txt_trees = get_text(self.translations, lang, "trees")

        # ? -> --- Paused Menu ---
        self.txt_paused_title = get_text(self.translations, lang, "paused-title")
        self.txt_paused_description = get_text(self.translations, lang, "paused-description")

        # ? -> --- Quit Showing Menu ---
        self.txt_exit_title = get_text(self.translations, lang, "exit-game-notice-title")
        self.txt_exit_description = get_text(self.translations, lang, "exit-game-notice-description")
        self.txt_exit_choice = get_text(self.translations, lang, "exit-game-notice-prompt")

        self.txt_btn_exit = get_text(self.translations, lang, "exit-btn-exit")
        self.txt_btn_go_back = get_text(self.translations, lang, "exit-btn-go-back")

    def draw_message(self, game, screen):
        if not hasattr(game, "tutorial_start_time"):
            game.tutorial_start_time = pygame.time.get_ticks()

        elapsed = (pygame.time.get_ticks() - game.tutorial_start_time) / 1000

        if elapsed >= 10: # -> Salimos del metodo
            self.message_surface = None
            return

        # * Creamos mensaje
        if self.message_surface is None:
            message = get_text(self.translations, game.current_lang, "mission-text")
            
            # Calcular líneas
            wrapped_text = wrap(message, width=50)
            line_height = self.message_font.size("Tg")[1]
            text_width = max(self.message_font.size(line)[0] for line in wrapped_text) + 40
            text_height = line_height * len(wrapped_text) + 20

            # Crear rectángulo semitransparente
            self.message_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            self.message_surface.fill((0, 0, 0, 160))

            y_offset = 10
            center_x = text_width // 2
            
            for line in wrapped_text:
                text_render = self.message_font.render(line, True, (255, 255, 255))
                text_rect = text_render.get_rect(centerx=center_x, y=y_offset)
                self.message_surface.blit(text_render, text_rect)
                y_offset += line_height
            
            screen_x = (WINDOW_WIDTH - text_width) // 2
            screen_y = 30
            self.message_rect_pos = (screen_x, screen_y)

        # -> Si hay mensaje lo dibujamos
        if self.message_surface:
            screen.blit(self.message_surface, self.message_rect_pos)