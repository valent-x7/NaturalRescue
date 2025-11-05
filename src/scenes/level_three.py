from settings import *
from sprites import *
from pytmx import load_pygame
from ui.healthbar import HealthBar
from ui.timebar import TimeBar
from ui.item import PuriCapsuleItem, ResourceCounter
from ui.button import ImageButtonUI, ButtonUI
from ui.utils import draw_text, get_text
from os import getcwd
from os.path import join
from random import choice
from textwrap import wrap

class LevelThree:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen # -> Game Screen
        self.wd = getcwd() # -> Working Directory

        # ? Scientist Sprites
        self.scientist_spritesheet = Spritesheet(join(self.wd, "img", "scientist_spritesheet.png"))

        self.all_sprites = AllSprites3() # -> All sprites Group
        self.collision_sprites = pygame.sprite.Group() # -> Sprites de colisión
        self.damage_sprites = pygame.sprite.Group() # -> Sprites de daño
        self.valve_sprites = pygame.sprite.Group() # -> Valvulas
        self.capsules_sprites = pygame.sprite.Group() # -> Capsulas
        self.enemy_sprites = pygame.sprite.Group() # -> Enemigos
        self.acid_sprites = pygame.sprite.Group() # -> Acido

        self.setup_images() # -> Setup Images
        self.setup_map() # -> Setup map
        self.setup_ui() # -> UI Elements

        self.translations = game.translations # -> Traducciones

    def run(self, game, events):
        self.game_screen.fill("black")

        # ? Events
        for event in events:
            if game.showing_quit_pop:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        game.showing_quit_pop = False
                        game.paused = False
                        return "MENU" # -> Salir al menú
                    elif event.key == pygame.K_n:
                        game.showing_quit_pop = False
                    
                elif self.exit_btn.is_clicked(event):
                    game.showing_quit_pop = False
                    game.paused = False
                    return "MENU" # -> Salir al menú
            
                elif self.go_back_btn.is_clicked(event):
                    game.showing_quit_pop = False

            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        game.showing_quit_pop = True
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused # -> Invertimos el valor de pausa

                elif self.resume_button.is_clicked(event) and game.paused:
                    game.paused = False

                elif self.pause_button.is_clicked(event) and not game.paused:
                    game.paused = True

                elif self.quit_button.is_clicked(event) and not game.paused:
                    game.showing_quit_pop = True
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game.paused:
                    self.player.shoot((self.all_sprites, self.all_sprites.depth_sprites, self.capsules_sprites), self.player, event.pos,
                                    self.all_sprites.camera_offset, self.all_sprites.zoom)
                
                elif event.type == self.enemy_event and len(self.enemy_sprites) < 3:
                    Ghost((self.all_sprites, self.all_sprites.depth_sprites, self.enemy_sprites), choice(self.enemy_spawn_coords),
                        self.player, self.capsules_sprites, game.current_difficulty)

        self.healthbar.hp =  self.player.health
        if not game.paused and not game.showing_quit_pop:
                pygame.mixer.unpause() # -> Reanudar todos los sonidos
                pygame.mixer.music.unpause() # Reanudar música
                self.player.input(events)
                self.all_sprites.update(game.dt, events, self.player)
                self.timebar.update()
        else:
            pygame.mixer.pause() # -> Pausar sonidos
            pygame.mixer.music.pause() # -> Pausar música

        self.all_sprites.center_on_target(self.player)
        self.all_sprites.draw_sprites()
        self.game_screen.blit(self.vignette, [0, 0])

        # ? Draw UI
        self.timebar.draw(self.game_screen)
        self.healthbar.draw(self.game_screen)
        self.puricapsule_item.draw(self.game_screen, get_text(self.translations, game.current_lang, "puricapsule"), self.player.capsules)
        self.ghosts_counter.draw(self.game_screen, get_text(self.translations, game.current_lang, "purified-ghosts"), self.player.ghosts)
        self.valves_counter.draw(self.game_screen, get_text(self.translations, game.current_lang, "valves"), self.player.valves)
        self.resume_button.draw() # -> Botón de reanudar
        self.pause_button.draw() # -> Botón de pausar
        self.quit_button.draw() # -> Botón de GRRR

        self.draw_messages(game, self.game_screen, ["mission-text-3", "mission-text-3-warning"], paused=game.paused, showing_popup=game.showing_quit_pop)

        self.check_doors_state(game.current_lang, game.dt)
        new_state = self.check_new_state() # -> Check new state

        if game.paused: # -> Juego pausado
                draw_text(self.game_screen, TITLE_FONT_PATH, 64,
                        get_text(self.translations, game.current_lang, "paused-title"),
                        "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
                draw_text(self.game_screen, TITLE_FONT_PATH, 36,
                        get_text(self.translations, game.current_lang, "paused-description"),
                        "#FFFFFF", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

        if game.showing_quit_pop: # -> PopUp de salida
            self.game_screen.blit(self.scrim, [0, 0])
            pygame.draw.rect(self.game_screen, "#282D32", self.popup_rect)
            pygame.draw.rect(self.game_screen, "#969696", self.popup_rect, 2)

            draw_text(self.game_screen, TITLE_FONT_PATH, 24, # -> Titulo
                      get_text(self.translations, game.current_lang, "exit-game-notice-title") , "yellow",
                      WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 60)
            draw_text(self.game_screen, TITLE_FONT_PATH, 20, # -> Descripción
                    get_text(self.translations, game.current_lang, "exit-game-notice-description") , "white",
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
            draw_text(self.game_screen, TITLE_FONT_PATH, 18, # -> Elección
                    get_text(self.translations, game.current_lang, "exit-game-notice-prompt") , "#C8C8C8",
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2  + 60)
            
            self.exit_btn.draw()
            self.go_back_btn.draw()
            draw_text(self.game_screen, TITLE_FONT_PATH, 14, get_text(self.translations, game.current_lang, "exit-btn-exit"), "white", WINDOW_WIDTH / 2 - 175, WINDOW_HEIGHT / 2 + 125)
            draw_text(self.game_screen, TITLE_FONT_PATH, 14, get_text(self.translations, game.current_lang, "exit-btn-go-back"), "white", WINDOW_WIDTH / 2 + 175, WINDOW_HEIGHT / 2 + 125)
        
        return new_state

    def setup_map(self):
        # -> Map Direction
        map = load_pygame(join(self.wd, "assets", "maps", "tmx", "lab.tmx"))

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

            elif obj.name == "Acid":
                Acid((self.all_sprites, self.all_sprites.background_sprites, self.acid_sprites), (obj.x, obj.y))
            
            elif obj.name == "Door":
                door = LabDoor((self.all_sprites, self.all_sprites.background_sprites, self.collision_sprites), (obj.x, obj.y))

                if hasattr(obj, "properties") and "required_ghosts" in obj.properties:
                    door.required_ghosts = obj.properties["required_ghosts"]

        # ? Create Player
        player_obj = map.get_object_by_name("Player")
        self.player = Scientist(self.scientist_spritesheet, (self.all_sprites, self.all_sprites.depth_sprites),
                                (player_obj.x, player_obj.y), self.collision_sprites, self.acid_sprites)
        
        # ? Enemy Event
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 4000) # -> Evento de enemigos cada 4 sg

    def setup_images(self):
        vignette = pygame.image.load(os.path.join(self.wd, "assets", "images", "screens", "vignette.png"))
        self.vignette= pygame.transform.scale(vignette, (WINDOW_WIDTH, WINDOW_HEIGHT)).convert_alpha()

        scientist_img = pygame.image.load(join(self.wd, "img", "scientist.png"))
        self.scientist_image = pygame.transform.scale(scientist_img, (42, 42)).convert_alpha()

    def setup_ui(self):
        self.healthbar = HealthBar(64, 78, 64 * 6, 32, SCIENTIST_HEALTH, self.scientist_image) # -> Barra de vida
        self.puricapsule_item = PuriCapsuleItem(os.path.join(self.wd, "assets", "images", "items", "puricapsula.png"))
        self.ghosts_counter = ResourceCounter(os.path.join(self.wd, "assets", "images", "items", "ghost.png"), (242, 148))
        self.valves_counter = ResourceCounter(os.path.join(self.wd, "assets", "images", "items", "valve.png"), (48, 148), len(self.valve_sprites))
        self.timebar = TimeBar(0, 0, WINDOW_WIDTH, 32, 225)
        self.pause_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "paused.png"), (WINDOW_WIDTH - 105, 40), (96, 96))
        self.resume_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "resume.png"), (WINDOW_WIDTH - 169, 40), (96, 96))
        self.quit_button = ImageButtonUI(self.game_screen, os.path.join(self.wd, "assets", "images", "quit.png"), (WINDOW_WIDTH - 233, 40), (96, 96))

        # ? PopUp
        self.scrim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.scrim.fill((0, 0, 0, 150))
        self.popup_rect = pygame.FRect(0, 0, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)
        self.popup_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        # -> PopUpButtons
        self.exit_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 - 175, WINDOW_HEIGHT / 2 + 125), "#e32227", "#f24449", "idk", 200, 45)
        self.go_back_btn = ButtonUI(self.game_screen, (WINDOW_WIDTH / 2 + 175, WINDOW_HEIGHT / 2 + 125), "#228b22", "#2ecc40", "idk", 200, 45)

    def draw_messages(self, game, screen, messages, paused = False, showing_popup = False):
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

        if not paused and not showing_popup:
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

    def check_new_state(self):
        if self.player.valves >= 5:
            # self.finished_level = True
            return "WINSCREEN" # -> Return winscreen state
        # elif self.healthbar.hp <= 0 or self.timebar.t <= 0:
        elif self.healthbar.hp <= 0:
            if self.player.footsteps_sound.get_num_channels():
                self.player.footsteps_sound.stop()
            # self.game_over = True
            return "GAMEOVER" # -> Return gameover state
        return "LEVEL_3" # -> Return same state
    
    def check_doors_state(self, current_lang, delta_time):
        for door in self.collision_sprites:
            if isinstance(door, LabDoor):
                screen_x = (door.rect.x - self.all_sprites.camera_offset.x) * self.all_sprites.zoom
                screen_y = (door.rect.y - self.all_sprites.camera_offset.y) * self.all_sprites.zoom
                ghosts = max(0, door.required_ghosts - self.player.ghosts)
                draw_text(self.game_screen, TITLE_FONT_PATH, 12, 
                          get_text(self.translations, current_lang, "purify-ghosts").format(count = ghosts),
                            "yellow", screen_x, screen_y - 30 * self.all_sprites.zoom)
                
                # ? Cada puerta tiene un requisito de fantasmas
                if hasattr(door, "required_ghosts") and self.player.ghosts >= door.required_ghosts:
                    door.open(delta_time)