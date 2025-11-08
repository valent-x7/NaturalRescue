import pygame
from os import getcwd
from settings import *
from ui.utils import draw_text, get_text, draw_text_space

class WinScreen:
    def __init__(self, game, screen: pygame.Surface, level_id):
        self.game_screen = screen
        self.level_id = level_id
        
        self.wd = getcwd() # -> Working directory

        self.translations = game.translations

        self.setup_images()

    def run(self, game, events):
        self.game_screen.blit(self.background, [0, 0])

        draw_text(self.game_screen, TITLE_FONT_PATH, 80, get_text(self.translations, game.current_lang, f"wingame_title-{self.level_id}"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 - 120)
        draw_text_space(self.game_screen, TITLE_FONT_PATH, 50, get_text(self.translations, game.current_lang, f"wingame_subtitle-{self.level_id}"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 30)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-m-to-menu"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 265)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-r-to-restart"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 200)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "MENU"
                elif e.key == pygame.K_r:
                    return "RESTART_LEVEL"
                
        return "WINSCREEN"
    
    def setup_images(self):
        background = pygame.image.load(join(self.wd, "assets", "images", "screens", f"fondowin{self.level_id}.png"))
        self.background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT)).convert_alpha()