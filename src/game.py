from settings import *
from menus.menu import MainMenu
from menus.settings import SettingsMenu
from menus.tutorial import Tutorial_levelone, Tutorial_leveltwo, Tutorial_levelthree
from sprites import *
from ui.utils import *
from menus.level_select import LevelSelectMenu
import settings as main_settings
from scenes.level_one import LevelOne
from scenes.level_2 import Level_two
from scenes.level_three import LevelThree
from scenes.gameover import GameOver
from scenes.winscreen import WinScreen

# Cargamos traducciones
translations = load_language("languajes.json")

class Game:

    # Música
    def play_music(self, filepath, loop=-1, fade_ms=500, volume = 0.5):
            # Si hay música sonando, hacemos fadeout
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
            # Cargamos y reproducimos la nueva música
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loop)


    def play_music_once(self, path, key):
        if getattr(self, "current_music", None) != key:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=0)  # solo una vez
            self.current_music = key

    # Ponemos un parametro para no iniciar siempre con el estado de Menu
    def __init__(self, state="MENU"):
        self.SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        width, height = self.SCREEN.get_size()
        main_settings.WINDOW_WIDTH = width
        main_settings.WINDOW_HEIGHT = height
        self.clock = pygame.time.Clock()
        self.running = True
        self.monkey_spritesheet = Spritesheet("./img/monkey_spritesheet.png")
        self.penguin_spritesheet = Spritesheet('./img/penguin_spritesheet.png')

        self.state = state  # -> Estado del juego

        # Config del lenguaje del juego
        self.current_lang = load_config("config.json")
        self.current_difficulty = load_difficulty("config.json")
        self.translations = translations

        # Estado de pausa
        self.paused = False
        self.showing_quit_pop = False

        # ? Nivel actual
        self.current_level = 1  # -> El primero por defecto

        # ? Creamos instancias de los estados (Menu, Settings, Tutorial, Level Select)
        self.Main_Menu = None
        # -> El estado de Settings siempre inicializado
        self.Settings_Menu = SettingsMenu(self, self.SCREEN)
        self.Level_Select_Menu = None
        self.Level_One = None
        self.Level_Two = None
        self.Level_Three = None
        self.WinScreen = None
        self.GameOverScreen = None

        # ? Instancias para los tutoriales
        self.Tutorial_One = None
        self.Tutorial_Two = None
        self.Tutorial_Three = None

        # ? Mostrar tutorial al inicio de cada nivel
        self.tutorial_1_done = False
        self.tutorial_2_done = False 
        self.tutorial_3_done = False

    # ? Cargar el lenguaje y crear botones
    def reload_language(self, lang):
        # ? Actualizar (crear) los botones en base al lenguaje
        if self.Main_Menu:
            self.Main_Menu.setup_buttons(lang)

        self.Settings_Menu.setup_buttons(lang)

        if self.Level_Select_Menu:
            self.Level_Select_Menu.setup_buttons(lang)

    # ? Este metodo creará las instancias de tutorial
    def setup_tutorial(self):
        self.tutorial_assets = {
                "keys": {
                    "W": pygame.image.load(
                        "assets/images/keys/key_w.png"
                    ).convert_alpha(),
                    "A": pygame.image.load(
                        "assets/images/keys/key_a.png"
                    ).convert_alpha(),
                    "S": pygame.image.load(
                        "assets/images/keys/key_s.png"
                    ).convert_alpha(),
                    "D": pygame.image.load(
                        "assets/images/keys/key_d.png"
                    ).convert_alpha(),
                    "H": pygame.image.load(
                        "assets/images/keys/key_h.png"
                    ).convert_alpha(),
                    "R": pygame.image.load(
                        "assets/images/keys/key_r.png"
                    ).convert_alpha(),
                    "P": pygame.image.load(
                        "assets/images/keys/key_p.png"
                    ).convert_alpha(),
                },
                "monkey": {
                    "W": pygame.image.load(
                        "assets/images/chango/chango_up.png"
                    ).convert_alpha(),
                    "A": pygame.image.load(
                        "assets/images/chango/chango_left.png"
                    ).convert_alpha(),
                    "S": pygame.image.load(
                        "assets/images/chango/chango_down.png"
                    ).convert_alpha(),
                    "D": pygame.image.load(
                        "assets/images/chango/chango_right.png"
                    ).convert_alpha(),
                },
                "extras": {
                    "H_brote": pygame.image.load(
                        "assets/images/keys/items.png"
                    ).convert_alpha(),
                    "R_restart": pygame.image.load(
                        "assets/images/keys/restart.png"
                    ).convert_alpha(),
                    "P_pause": pygame.image.load(
                        "assets/images/keys/pause.png"
                    ).convert_alpha(),
                },
                "arrows": {
                     "W": pygame.image.load(
                         "assets/images/keys/arrow_up.png"
                         ).convert_alpha(),
                     "A": pygame.image.load(
                         "assets/images/keys/arrow_left.png"
                         ).convert_alpha(),
                     "S": pygame.image.load(
                         "assets/images/keys/arrow_down.png"
                         ).convert_alpha(),
                     "D": pygame.image.load(
                         "assets/images/keys/arrow_right.png"
                         ).convert_alpha(),
            }
        }

    def run(self):

        while self.running:

            # Usamos delta Time
            self.dt = self.clock.tick(60) / 1000  # Segundos por Frame

            # Obtener Eventos
            events = pygame.event.get()

            if self.state == "MENU":
                if getattr(self, "current_music", None) != "menu":
                    self.play_music("assets/music/menu.ogg")
                    self.current_music = "menu"

                if not self.Main_Menu:
                    self.Main_Menu = MainMenu(self, self.SCREEN)

                self.state = self.Main_Menu.run(self, events)

            elif self.state == "SETTINGS":
                if getattr(self, "current_music", None) != "settings":
                    self.play_music("assets/music/settings.ogg")
                    self.current_music = "settings"

                self.state = self.Settings_Menu.run(self, events)

            elif self.state == "SALIR":
                self.running = False

            elif self.state == "LEVEL_SELECT":
                if getattr(self, "current_music", None) != "level_select":
                    self.play_music("assets/music/levelselect.ogg")
                    self.current_music = "level_select"

                if not self.Level_Select_Menu:
                    self.Level_Select_Menu = LevelSelectMenu(self, self.SCREEN)

                self.state = self.Level_Select_Menu.run(self, events)

            elif self.state == "START_LEVEL_1":
                self.current_level = 1
                # -> Si existe nivel 1 y tiene gameover en true mandarlo a gameover directo
                if hasattr(self, "Level_One") and getattr(self.Level_One, "game_over", False):
                    self.state = "GAMEOVER"

                elif hasattr(self, "Level_One") and getattr(self.Level_One, "finished_level", False):
                    self.state = "WINSCREEN"

                elif not self.tutorial_1_done:
                    self.state = "TUTORIAL_1"

                else:
                    self.state = "LEVEL_1"

            elif self.state == "START_LEVEL_2":
                self.current_level = 2
                if not self.tutorial_2_done:
                    self.state = "TUTORIAL_2"
                else:
                    self.state = "LEVEL_2"

            elif self.state == "START_LEVEL_3":
                self.current_level = 3
                if not self.tutorial_3_done:
                    self.state = "TUTORIAL_3"
                else:
                    self.state = "LEVEL_3"

            elif self.state == "TUTORIAL_1":
                if not self.Tutorial_One: 
                    if not hasattr(
                        self, "tutorial_assets"
                    ):  # Carga assets si es necesario
                        self.setup_tutorial()
                    self.Tutorial_One = Tutorial_levelone(  # Usa la clase correcta
                        self.translations,
                        self.current_lang,
                        self.tutorial_assets,
                    )

                if getattr(self, "current_music", None) != "tutorial":
                    self.play_music("assets/music/tutorial.ogg")
                    self.current_music = "tutorial"

                # Ejecuta el draw de la instancia
                self.state = self.Tutorial_One.draw(
                    self, self.SCREEN, events, self.current_lang
                )

            elif self.state == "TUTORIAL_2":
                if not self.Tutorial_Two:
                    if not hasattr(self, "tutorial_assets"):
                        self.setup_tutorial()
                    self.Tutorial_Two = Tutorial_leveltwo(  # Usa la clase correcta
                        self.translations,
                        self.current_lang,
                        self.tutorial_assets,
                    )

                if getattr(self, "current_music", None) != "tutorial":
                    self.play_music("assets/music/tutorial.ogg")
                    self.current_music = "tutorial"

                self.state = self.Tutorial_Two.draw(
                    self, self.SCREEN, events, self.current_lang
                )

            elif self.state == "TUTORIAL_3":
                if not self.Tutorial_Three:
                    if not hasattr(self, "tutorial_assets"):
                        self.setup_tutorial()
                    self.Tutorial_Three = Tutorial_levelthree(  # Usa la clase correcta
                        self.translations,
                        self.current_lang,
                        self.tutorial_assets,
                    )

                if getattr(self, "current_music", None) != "tutorial":
                    self.play_music("assets/music/tutorial.ogg")
                    self.current_music = "tutorial"

                self.state = self.Tutorial_Three.draw(
                    self, self.SCREEN, events, self.current_lang
                )
            
            # ? Niveles
            elif self.state == "LEVEL_1":
                if getattr(self, "current_music", None) != "level_1":
                    self.play_music("assets/music/level_one_music.ogg")
                    self.current_music = "level_1"

                if not self.Level_One:
                    self.Level_One = LevelOne(self, self.SCREEN)

                self.state = self.Level_One.run(self, events)

            elif self.state == "LEVEL_2":   
                if getattr(self, "current_music", None) != "level_3":
                    self.play_music("assets/music/tutorial.ogg", volume=0.1)
                    self.current_music = "level_3"


                if not self.Level_Two:
                    self.Level_Two = Level_two(self, self.SCREEN)
                self.state = self.Level_Two.run()

            elif self.state == "LEVEL_3":
                if getattr(self, "current_music", None) != "level_3":
                    self.play_music("assets/music/level_three_music.mp3", volume=0.1)
                    self.current_music = "level_3"

                if not self.Level_Three:
                    self.Level_Three = LevelThree(self, self.SCREEN)

                self.state = self.Level_Three.run(self, events)

            elif self.state == "GAMEOVER":
                if not getattr(self, "entered_gameover", False):
                    self.play_music_once("assets/sound/gameover.ogg", "gameover")
                    self.entered_gameover = True

                if not self.GameOverScreen: # -> Si no hay GameOverScreen lo creamos
                    self.GameOverScreen = GameOver(self, self.SCREEN, self.current_level)

                new_state = self.GameOverScreen.run(self, events) # -> Metodo run del GameOverScreen

                if new_state == "MENU":
                    self.state = "MENU"
                    self.entered_gameover = False
                    self.unload_current_level()
                    self.GameOverScreen = None

                elif new_state == "RESTART_LEVEL":
                    self.entered_gameover = False
                    self.restart_current_level()
                    self.GameOverScreen = None

            elif self.state == "WINSCREEN":
                if not getattr(self, "entered_winscreen", False):
                    self.play_music_once("assets/sound/win.ogg", "winscreen")
                    self.entered_winscreen = True

                if not self.WinScreen: # -> Si no hay WinScreen definido lo creamos
                    self.WinScreen = WinScreen(self, self.SCREEN, self.current_level)

                new_state = self.WinScreen.run(self, events) # -> Metodo Run del WinScreen

                if new_state == "MENU":
                    self.state = "MENU"
                    self.entered_winscreen = False
                    self.unload_current_level()
                    self.WinScreen = None

                elif new_state == "RESTART_LEVEL":
                    self.entered_winscreen = False
                    self.restart_current_level()
                    self.WinScreen = None

            # Checar eventos del menú
            self.check_events(events)

            pygame.display.flip()

        pygame.quit()

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

    # ? Borrar nivel
    def unload_current_level(self):
        if self.current_level == 1:
            if hasattr(self, "Level_One"):
                del self.Level_One
                self.Level_One = None
        elif self.current_level == 2:
            if hasattr(self, "Level_Two"):
                del self.Level_Two
                self.Level_Two = None
        elif self.current_level == 3:
            if hasattr(self, "Level_Three"):
                del self.Level_Three
                self.Level_Three = None

    # ? Reiniciar nivel en base del id
    def restart_current_level(self):
        self.unload_current_level()

        if self.current_level == 1:
            self.state = "START_LEVEL_1"
        elif self.current_level == 2:
            self.state = "START_LEVEL_2"
        elif self.current_level == 3:
            self.state = "START_LEVEL_3"