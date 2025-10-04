from settings import *
from menus.menu import draw_menu
from menus.settings import draw_settings
from menus.tutorial import draw_tutorial
from scenes.play import draw_game
from sprites import *
from ui.button import Button
from ui.utils import *
from ui.healthbar import HealthBar
from ui.timebar import TimeBar
from ui.item import TreeSprout
from menus.level_select import draw_level_select
import settings as main_settings
import os
import json
from pytmx import load_pygame
from scenes.gameover import draw_gameover

# Cargamos traducciones
translations = load_language("languajes.json")

class Game:
    
    # Música
    def play_music(self, filepath, loop=-1, fade_ms=500):
        try:
            # Si hay música sonando, hacemos fadeout
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
            # Cargamos y reproducimos la nueva música
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(loop)
        except Exception as e:
            print("Error al reproducir la música:", e)

    def play_music_once(self, path, key):
        if getattr(self, "current_music", None) != key:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(loops=0)  # solo una vez
                self.current_music = key
            except Exception as e:
                print("Error al reproducir música:", e)

    # Ponemos un parametro para no iniciar siempre con el estado de Menu
    def __init__(self, state = "MENU"):
        self.SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        width, height = self.SCREEN.get_size()
        main_settings.WINDOW_WIDTH = width
        main_settings.WINDOW_HEIGHT = height
        self.clock = pygame.time.Clock()
        self.running = True
        self.monkey_spritesheet = Spritesheet('./img/monkey_spritesheet.png')

        self.state = state # -> Estado del juego

        # Config del lenguaje del juego
        self.current_lang = load_config("config.json")

        # Estado de pausa
        self.paused = False

        # Creamos instancias del menú
        self.setup_menu()

    # ? Este método creará las instancias del menu (botones y fuentes)
    def setup_menu(self):
        # Letra del titulo
        self.fuente_titulo = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 64)
        # Letra de los botones
        self.fuente_botones = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 24)

        # ? Definimos el directorio para las imagenes
        working_directory = os.getcwd()

        # ? Capas del fondo
        # Capa 1
        capa1 = pygame.image.load(os.path.join(working_directory, "assets", "images", "menu",
                                                    "background_menu1.png")).convert()
        capa1 = pygame.transform.scale(capa1, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
        self.capa1 = capa1.convert()
        self.bg_menu_width = capa1.get_width() # Ancho del fondo

        # Capa 2
        capa2 = pygame.image.load(os.path.join(working_directory, "assets", "images", "menu",
                                                    "background_menu2.png")).convert_alpha()
        capa2 = pygame.transform.scale(capa2, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
        self.capa2 = capa2.convert_alpha()

        # Capa 3
        capa3 = pygame.image.load(os.path.join(working_directory, "assets", "images", "menu",
                                                    "background_menu3.png")).convert_alpha()
        capa3 = pygame.transform.scale(capa3, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
        self.capa3 = capa3.convert_alpha()

        # Capa 4
        capa4 = pygame.image.load(os.path.join(working_directory, "assets", "images", "menu",
                                                    "background_menu4.png")).convert_alpha()
        capa4 = pygame.transform.scale(capa4, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
        self.capa4 = capa4.convert_alpha()

        # Capa 5
        capa5 = pygame.image.load(os.path.join(working_directory, "assets", "images", "menu",
                                                    "background_menu5.png")).convert_alpha()
        capa5 = pygame.transform.scale(capa5, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
        self.capa5 = capa5.convert_alpha()

        # ? Imagenes del mono y pinguino
        self.mono = pygame.image.load(os.path.join(working_directory, "img", "chango.png")).convert_alpha()
        self.pinguino = pygame.image.load(os.path.join(working_directory, "img", "pinguino.png")).convert_alpha()

        # Tamaño del pinguino
        self.pinguino_rect = self.pinguino.get_frect()

        # Calculamos una posición para el pingüino y asignamos una posición fija para el chango.
        self.position_y = 400
        self.pinguino_x = main_settings.WINDOW_WIDTH - self.pinguino_rect.width - 80
        self.chango_x = 900

        # ? Instancias de los botones
        # Usamos el directorio de trabajo y con join lo unimos para crear la ruta
        self.play_btn = Button(self.SCREEN, (main_settings.WINDOW_WIDTH // 4, 400), 
                               self.fuente_botones, 300, 90, get_text(translations, self.current_lang, "play"), 4, 
                               os.path.join(working_directory, "assets", "images", "play_icon.png"), 20, '#34D399', '#10B981')
        self.tutorial_btn = Button(self.SCREEN, (main_settings.WINDOW_WIDTH // 4, 520), 
                               self.fuente_botones, 300, 90, get_text(translations, self.current_lang, "tutorial"), 4, 
                               os.path.join(working_directory, "assets", "images", "tutorial_icon.png"), 0, '#FACC15', '#EAB308')
        self.settings_btn = Button(self.SCREEN, (main_settings.WINDOW_WIDTH // 4, 640), 
                               self.fuente_botones, 300, 90, get_text(translations, self.current_lang, "settings"), 4, 
                               os.path.join(working_directory, "assets", "images", "settings_icon.png"), 0, '#38BDF8', '#0EA5E9')
        self.exit_btn = Button(self.SCREEN, (main_settings.WINDOW_WIDTH // 4, 760), 
                               self.fuente_botones, 300, 90, get_text(translations, self.current_lang, "exit"), 4, 
                               os.path.join(working_directory, "assets", "images", "salir_icon.png"), 20, '#FB923C', '#F97316')

    # ? Este metodo creará las instancias de ajustes
    def setup_settings(self):

        # Definimos el directorio
        working_directory = os.getcwd()

        # ? Cargamos capa 1
        capa1 = pygame.image.load(os.path.join(working_directory, "assets", "images", "ajustes", "background_settings1.png")).convert()
        self.settings_capa1 = pygame.transform.scale(capa1, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert()
        self.settings_bg_width = self.settings_capa1.get_width()

        # ? Cargamos capa 2
        capa2 = pygame.image.load(os.path.join(working_directory, "assets", "images", "ajustes", "background_settings2.png")).convert_alpha()
        self.settings_capa2 = pygame.transform.scale(capa2, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT)).convert_alpha()

        # ? Cargamos imagen de flecha
        arrow_image = pygame.image.load(os.path.join(working_directory, "assets", "images", "ajustes", "flecha.png")).convert_alpha()
        self.arrow_image = pygame.transform.scale(arrow_image, (96, 96)).convert_alpha()

        # ? Creamos botones

        self.english_button = Button(self.SCREEN, (main_settings.WINDOW_WIDTH / 2, 400), 
                                    self.fuente_botones, 320, 90, get_text(translations, self.current_lang, "settings-to-english"), 4,
                                    os.path.join(working_directory, "assets", 'images', "ajustes", "ukFlag.png"), 10, "#4D96FF", "#6DAFFF")
        self.spanish_button = Button(self.SCREEN, (main_settings.WINDOW_WIDTH / 2, 520), 
                                    self.fuente_botones, 320, 90, get_text(translations, self.current_lang, "settings-to-spanish"), 4,
                                    os.path.join(working_directory, "assets", 'images', "ajustes", "spainFlag.png"), 10, "#38B000", "#70E000")

    # ? Este metodo creará las instancias de tutorial
    def setup_tutorial(self):
        self.tutorial_assets = {
        "keys": {
            "W": pygame.image.load("assets/images/keys/key_w.png").convert_alpha(),
            "A": pygame.image.load("assets/images/keys/key_a.png").convert_alpha(),
            "S": pygame.image.load("assets/images/keys/key_s.png").convert_alpha(),
            "D": pygame.image.load("assets/images/keys/key_d.png").convert_alpha(),
            "H": pygame.image.load("assets/images/keys/key_h.png").convert_alpha(),  
            "R": pygame.image.load("assets/images/keys/key_r.png").convert_alpha(), 
            "P": pygame.image.load("assets/images/keys/key_p.png").convert_alpha()   
        },
        "monkey": {
            "W": pygame.image.load("assets/images/chango/chango_up.png").convert_alpha(),
            "A": pygame.image.load("assets/images/chango/chango_left.png").convert_alpha(),
            "S": pygame.image.load("assets/images/chango/chango_down.png").convert_alpha(),
            "D": pygame.image.load("assets/images/chango/chango_right.png").convert_alpha()
        },
        "extras": {
            "H_brote": pygame.image.load("assets/images/items/brote.png").convert_alpha(),
            "R_restart": pygame.image.load("assets/images/keys/restart.png").convert_alpha(),
            "P_pause": self.combine_pause_images(
                "assets/images/keys/pause1.png",
                "assets/images/keys/pause2.png"
            )
        }
    }

    # Función para combinar dos imágenes de pausa en un solo Surface
    def combine_pause_images(self, path1, path2):
     img1 = pygame.image.load(path1).convert_alpha()
     img2 = pygame.image.load(path2).convert_alpha()

    # Recortamos el rect que ocupa realmente la imagen (quita transparencia)
     rect1 = img1.get_bounding_rect()
     rect2 = img2.get_bounding_rect()
     img1 = img1.subsurface(rect1)
     img2 = img2.subsurface(rect2)

    # Creamos surface con ancho sumado (sin espacio extra)
     width = img1.get_width() + img2.get_width() + 2
     height = max(img1.get_height(), img2.get_height())
     combined = pygame.Surface((width, height), pygame.SRCALPHA)

    # Dibujamos pegadas
     combined.blit(img1, (0, 0))
     combined.blit(img2, (img1.get_width() + 2, 0))

     return combined




    def run(self):

        while self.running:

            # ? Usamos delta Time
            dt = self.clock.tick(60) / 1000 # Segundos por Frame

            # -------------------
            # Reproducir música según el estado
            # -------------------
            if self.state == 'MENU':
                if getattr(self, "entered_gameover", False):
                    self.entered_gameover = False
                if getattr(self, 'current_music', None) != "menu":
                    self.play_music("assets/music/menu.ogg")
                    self.current_music = "menu"

            elif self.state == "LEVEL_SELECT":
                if getattr(self, "entered_gameover", False):
                    self.entered_gameover = False
                if getattr(self, 'current_music', None) != "level_select":
                    self.play_music("assets/music/levelselect.ogg")
                    self.current_music = "level_select"

            elif self.state == "TUTORIAL":
                if getattr(self, 'current_music', None) != "tutorial":
                    self.play_music("assets/music/tutorial.ogg")
                    self.current_music = "tutorial"
                    self.setup_tutorial()

            elif self.state == "SETTINGS":
                if getattr(self, 'current_music', None) != "settings":
                    self.play_music("assets/music/settings.ogg")
                    self.current_music = "settings"
                    self.setup_settings()

            elif self.state == "PLAYING" or self.state == "LEVEL_1":
                if getattr(self, 'current_music', None) != "level1":
                    self.play_music("assets/music/level1.ogg")
                    self.current_music = "level1"
                if not hasattr(self, 'all_sprites'):
                    self.new()

            elif self.state == "GAMEOVER":
                # reproducir música de Game Over solo una vez al entrar
                if not getattr(self, "entered_gameover", False):
                    pygame.mixer.music.stop()
                    try:
                        pygame.mixer.music.load("assets/sound/gameover.ogg")
                        pygame.mixer.music.play(loops=0)  # una sola vez
                    except Exception as e:
                        print("Error al reproducir música Game Over:", e)
                    self.entered_gameover = True

            # -------------------
            # Obtener Eventos
            # -------------------
            events = pygame.event.get()

            if self.state == 'MENU':
                self.state = draw_menu(self.SCREEN, events, self.bg_menu_width, self.capa1, self.capa2, self.capa3, 
                                       self.capa4, self.capa5, self.mono, self.pinguino, self.position_y, self.chango_x, 
                                       self.pinguino_x, self.fuente_titulo, self.play_btn, 
                                       self.tutorial_btn, self.settings_btn, self.exit_btn)

            elif self.state == "LEVEL_SELECT":
                 self.state = draw_level_select(self.SCREEN, events, translations, self.current_lang)  

            elif self.state == "PLAYING":
                if not hasattr(self, 'all_sprites'):
                    self.new()
                self.state = draw_game(self.SCREEN, events, translations, self.player_TimeBar, self.player_healthbar, self, dt)

            # Nivel 1
            elif self.state == "LEVEL_1":
                self.state = "PLAYING"

            # Nivel 2
            elif self.state == "LEVEL_2":
                pass

            # Nivel 3
            elif self.state == "LEVEL_3":
                pass

            # Tutorial del juego
            elif self.state == "TUTORIAL":
                self.setup_tutorial()
                self.state = draw_tutorial(self.SCREEN, events, translations, self.current_lang, self.tutorial_assets)

            # Ajustes
            elif self.state == "SETTINGS":
                self.setup_settings()
                self.state = draw_settings(self.SCREEN, self, events, self.settings_bg_width, self.settings_capa1, self.settings_capa2, 
                                           self.arrow_image, self.english_button, self.spanish_button)

            # Salir del juego
            elif self.state == "SALIR":
                self.running = False

            elif self.state == "GAMEOVER":
               new_state = draw_gameover(self.SCREEN, events, translations, self.current_lang)

               # Solo revisamos new_state dentro del mismo bloque
               if new_state == "MENU":
                   self.state = "MENU"
                   self.entered_gameover = False

               elif new_state == "RESTART_LEVEL":
                self.state = "PLAYING"
                self.entered_gameover = False

                if hasattr(self, 'all_sprites'):
                   del self.all_sprites  # Fuerza a recrear el nivel

                # Forzar que la música del nivel 1 vuelva a sonar
                self.play_music("assets/music/level1.ogg")
                self.current_music = "level1"

            # Checar eventos del menú
            self.check_events(events)

            pygame.display.flip()
        
        pygame.quit()
    
    def new(self):
        self.playing = True

        # Grupos de sprites
        self.all_sprites = AllSprites() # -> Todos los sprites
        self.collision_sprites = pygame.sprite.Group() # -> Sprites limitadores o de colisión
        self.water_collision_sprites = pygame.sprite.Group() # -> Sprites de colisión de agua
        self.damage_sprites = pygame.sprite.Group() # -> Sprites que hacen daño
        self.plant_spots = pygame.sprite.Group() # -> Lugares de plantación

        self.setup_map()

    def setup_map(self):

        # Directorio
        working_directory = os.getcwd()

        map = load_pygame(os.path.join(working_directory, "assets", "maps", "tmx", "bosque.tmx"))
        
        # ? Layers o capas
        for layer_name in ["Ground", "Decoration", "WaterCollision", "Collision"]:
            layer = map.get_layer_by_name(layer_name)

            for x, y, image in layer.tiles():
                if layer.name == "Ground" or layer.name == "Decoration":
                    Sprite(self.all_sprites, (x * TILE, y * TILE), image)
                elif layer.name == "WaterCollision":
                    WaterCollisionSprite((self.all_sprites, self.water_collision_sprites), "Limit", (x * TILE, y * TILE), image)
                else:
                    CollisionSprite((self.all_sprites, self.collision_sprites), "Limit", (x * TILE, y * TILE), image)

        # ? Objectos
        for obj in map.objects:
            # Creamos árboles
            if obj.name == "Tree":
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    CollisionSprite((self.all_sprites, self.collision_sprites), "Tree", (obj.x, obj.y), image)
            # Creamos ramas
            elif obj.name == "Branch":
                if hasattr(obj, "gid") and obj.gid:
                    image = map.get_tile_image_by_gid(obj.gid)

                    DamageSprite((self.all_sprites, self.damage_sprites), (obj.x, obj.y), image)
            # Creamos lugares de cultivo
            elif obj.name == "Plant Position":
                PlantSpot((self.all_sprites, self.plant_spots), obj.x, obj.y)

        self.map_width = map.width * TILE
        self.map_height = map.height * TILE

        # ? Creamos el jugador en la posición indicada
        player_obj = map.get_object_by_name("Player")
        self.player = Monkey(self.monkey_spritesheet, player_obj.x, player_obj.y, self.all_sprites, self.collision_sprites, self.water_collision_sprites, self.damage_sprites, self.plant_spots)

        self.player_healthbar = HealthBar(64, 64, 64*6, 32, 100)
        self.player_TimeBar = TimeBar(0, 0, WINDOW_WIDTH + 100, 32, 150)

        # Item de los brotes de árbol en pantalla
        self.item = TreeSprout(os.path.join(working_directory, "assets", "images", "items", "brote.png"))

    # ? Checar eventos del menú
    def check_events(self, events):
        for event in events:
                # -> Cerrar PyGame
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
    
                # ? Teclas presionadas
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        sys.exit()
