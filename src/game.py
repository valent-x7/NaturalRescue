from settings import *
from menus.menu import draw_menu
from menus.settings import draw_settings
from menus.tutorial import draw_tutorial
from scenes.play import draw_game

class Game:
    def __init__(self):
        pygame.init()

        self.SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

        self.running = True
        self.state = "MENU" # -> Estado del juego

    def run(self):

        while self.running:

            # ? Obtener Eventos
            events = pygame.event.get()

            if self.state == 'MENU':
                self.state = draw_menu(self.SCREEN, events)

            elif self.state == "PLAYING":
                self.state = draw_game(self.SCREEN, events)

            elif self.state == "TUTORIAL":
                self.state = draw_tutorial(self.SCREEN, events)

            elif self.state == "SETTINGS":
                self.state = draw_settings(self.SCREEN, events)

            # Check Events
            self.check_events(events)

            pygame.display.flip()
        
        pygame.quit()

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