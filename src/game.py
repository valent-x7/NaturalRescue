from settings import *
from menus.menu import MainMenu
from menus.settings import SettingsMenu
from menus.tutorial import Tutorial
from sprites import *
from ui.utils import *
from menus.level_select import LevelSelectMenu
import settings as main_settings
from scenes.gameover import draw_gameover
from scenes.level_one import LevelOne
from scenes.level_2 import draw_level2
from scenes.winscreen import draw_winscreen

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
    def __init__(self, state="MENU"):
        self.SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        width, height = self.SCREEN.get_size()
        main_settings.WINDOW_WIDTH = width
        main_settings.WINDOW_HEIGHT = height
        self.clock = pygame.time.Clock()
        self.running = True
        self.monkey_spritesheet = Spritesheet("./img/monkey_spritesheet.png")

        self.state = state  # -> Estado del juego

        # Config del lenguaje del juego
        self.current_lang = load_config("config.json")
        self.translations = translations

        # Estado de pausa
        self.paused = False

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

        # ? Mostrar tutorial al inicio de cada nivel
        self.show_tutorial = True

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
        print("🔧 Iniciando carga de assets del tutorial...")
        try:
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
            }
            print("✅ Tutorial assets cargados correctamente")
        except Exception as e:
            print(f"❌ Error al cargar assets del tutorial: {e}")
            import traceback

            traceback.print_exc()
            self.state = "MENU"  # Si falla, vuelve al menú

    def run(self):

        while self.running:

            # Usamos delta Time
            self.dt = self.clock.tick(60) / 1000  # Segundos por Frame

            # Reproducir música según el estado
            if self.state == "MENU":
                if getattr(self, "entered_gameover", False):
                    self.entered_gameover = False
                if getattr(self, "current_music", None) != "menu":
                    self.play_music("assets/music/menu.ogg")
                    self.current_music = "menu"

            elif self.state == "LEVEL_SELECT":
                if getattr(self, "entered_gameover", False):
                    self.entered_gameover = False
                if getattr(self, "current_music", None) != "level_select":
                    self.play_music("assets/music/levelselect.ogg")
                    self.current_music = "level_select"

            elif self.state == "SETTINGS":
                if getattr(self, "current_music", None) != "settings":
                    self.play_music("assets/music/settings.ogg")
                    self.current_music = "settings"

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

            # Obtener Eventos
            events = pygame.event.get()

            # ? Manejar estados del juego
            if self.state == "MENU":
                # ? Musica
                if getattr(self, "current_music", None) != "menu":
                    self.play_music("assets/music/menu.ogg")
                    self.current_music = "menu"

                if not self.Main_Menu:
                    self.Main_Menu = MainMenu(self, self.SCREEN)
                self.state = self.Main_Menu.run(self, events)

            elif self.state == "LEVEL_SELECT":  # -> Selector de nivel
                if not self.Level_Select_Menu:
                    self.Level_Select_Menu = LevelSelectMenu(self, self.SCREEN)
                self.state = self.Level_Select_Menu.run(self, events)

            # Bandera para saber si ya mostramos el tutorial
            if not hasattr(self, "tutorial_done"):
                self.tutorial_done = False

            # Nivel 1
            elif self.state == "LEVEL_1":
                # Si el tutorial aún no se ha mostrado, pasamos a esa pantalla
                if not self.tutorial_done:
                    self.state = "TUTORIAL_LEVEL_1"
                else:
                    self.state = "LEVEL_1_RUNNING"

            # Estado del tutorial antes del Nivel 1
            elif self.state == "TUTORIAL_LEVEL_1":
                # Si no existe aún la instancia del tutorial, la creamos
                if not hasattr(self, "tutorial_instance"):
                    self.setup_tutorial()  # Cargar recursos si es necesario
                    self.tutorial_instance = Tutorial(
                        self.translations,  # Diccionario de traducciones
                        self.current_lang,  # Idioma actual
                        self.tutorial_assets,  # Imágenes o textos del tutorial
                    )
                    pygame.mixer.music.stop()  # Detenemos música del menú, si había

                # Dibujamos el tutorial y obtenemos su resultado
                result = self.tutorial_instance.draw(
                    self.SCREEN, events, self.current_lang
                )

                # Si el jugador presiona Enter, el tutorial devuelve "LEVEL"
                if result == "LEVEL":
                    self.tutorial_done = True  # Marcamos que ya se mostró el tutorial
                    self.state = "LEVEL_1_RUNNING"  # Cambiamos al estado del nivel 1
                    self.play_music("assets/music/level_one_music.ogg")
                    self.current_music = "level1"
                    del self.tutorial_instance  # Eliminamos el tutorial de memoria

                # Si el jugador decide regresar al menú (por ejemplo, presionando ESC)
                elif result == "MENU":
                    self.state = "MENU"
                    if hasattr(self, "tutorial_instance"):
                        del self.tutorial_instance

            # Estado del nivel 1 en ejecución
            elif self.state == "LEVEL_1_RUNNING":
                if not hasattr(self, "Level_One") or self.Level_One is None:
                    self.Level_One = LevelOne(self, self.SCREEN)

                # Ejecutar run() y capturar el nuevo estado (asegurando que existe)
                new_state = self.Level_One.run(self, events) if self.Level_One else None

                # Solo cambiar de estado si hay uno nuevo válido
                if new_state and new_state != "LEVEL_1_RUNNING":
                    self.state = new_state

            # Nivel 2
            elif self.state == "LEVEL_2":
                self.state = draw_level2(self.SCREEN)

            # Nivel 3
            elif self.state == "LEVEL_3":
                pass

            # Ajustes
            elif self.state == "SETTINGS":
                self.state = self.Settings_Menu.run(self, events)

            # Salir del juego
            elif self.state == "SALIR":
                self.running = False

            elif self.state == "WINSCREEN":
                new_state = draw_winscreen(
                    self.SCREEN, events, translations, self.current_lang
                )

                if new_state == "MENU":
                    self.state = "MENU"
                    self.entered_gameover = False

                elif new_state == "RESTART_LEVEL":
                    self.state = "LEVEL_1"
                    self.entered_gameover = False

                    if hasattr(self, "Level_One"):
                        del self.Level_One

                    self.Level_One = LevelOne(
                        self, self.SCREEN
                    )  # -> Nivel limpio y nuevo

                    # Forzar que la música del nivel 1 vuelva a sonar
                    self.play_music("assets/music/level_one_music.ogg")
                    self.current_music = "level1"

            elif self.state == "GAMEOVER":  # -> Pantalla de Game Over
                new_state = draw_gameover(
                    self.SCREEN, events, translations, self.current_lang
                )

                # Solo revisamos new_state dentro del mismo bloque
                if new_state == "MENU":
                    self.state = "MENU"
                    self.entered_gameover = False

                elif new_state == "RESTART_LEVEL":
                    self.state = "LEVEL_1"
                    self.entered_gameover = False

                    if hasattr(self, "Level_One"):
                        del self.Level_One  # Fuerza a recrear el nivel

                    self.Level_One = LevelOne(
                        self, self.SCREEN
                    )  # -> Nivel limpio y nuevo

                    # Forzar que la música del nivel 1 vuelva a sonar
                    self.play_music("assets/music/level_one_music.ogg")
                    self.current_music = "level1"

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
