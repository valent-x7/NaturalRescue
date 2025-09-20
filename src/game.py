from settings import *
from menus.menu import draw_menu
from menus.settings import draw_settings
from menus.tutorial import draw_tutorial
from scenes.play import draw_game
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.running = True
        self.monkey_spritesheet = Spritesheet('./img/monkey_spritesheet.png')

        self.state = "MENU" # -> Estado del juego

    def run(self):

        while self.running:

            # ? Obtener Eventos
            events = pygame.event.get()

            if self.state == 'MENU':
                self.state = draw_menu(self.SCREEN, events)

            elif self.state == "PLAYING":
                if not hasattr(self, 'all_sprites'):
                    self.new()
                self.state = draw_game(self.SCREEN, events, self)

            elif self.state == "TUTORIAL":
                self.state = draw_tutorial(self.SCREEN, events)

            elif self.state == "SETTINGS":
                self.state = draw_settings(self.SCREEN, events)

            # Check Events
            self.check_events(events)

            pygame.display.flip()
        
        pygame.quit()
    
    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()

        self.player = Monkey(self.monkey_spritesheet, 480, 640)
        self.all_sprites.add(self.player)


    # ? Checar eventos
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