from settings import *
from menus.menu import draw_menu
from menus.settings import draw_settings
from menus.tutorial import draw_tutorial
from scenes.play import draw_game
from sprites import *
from menus.level_select import draw_level_select

class Game:
    # Ponemos un parametro para no iniciar siempre con el estado de Menu
    def __init__(self, state = "MENU"):
        self.SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.monkey_spritesheet = Spritesheet('./img/monkey_spritesheet.png')

        self.state = state # -> Estado del juego

    def run(self):

        while self.running:

            # ? Usamos delta Time
            dt = self.clock.tick(60) / 1000 # Segundos por Frame

            # ? Obtener Eventos
            events = pygame.event.get()

            if self.state == 'MENU':
                self.state = draw_menu(self.SCREEN, events)

            elif self.state == "LEVEL_SELECT":
                 self.state = draw_level_select(self.SCREEN, events)  

            elif self.state == "PLAYING":
                if not hasattr(self, 'all_sprites'):
                    self.new()
                self.state = draw_game(self.SCREEN, events, self, dt)

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
                self.state = draw_tutorial(self.SCREEN, events)

            # Ajustes
            elif self.state == "SETTINGS":
                self.state = draw_settings(self.SCREEN, events)

            # Salir del juego
            elif self.state == "SALIR":
                self.running = False

            # Checar eventos del menú
            self.check_events(events)

            pygame.display.flip()
        
        pygame.quit()
    
    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()

        self.player = Monkey(self.monkey_spritesheet, 480, 640)
        self.all_sprites.add(self.player)


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