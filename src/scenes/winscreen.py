import pygame
from settings import *
from ui.utils import draw_text, get_text

class WinScreen:
    def __init__(self, game, screen: pygame.Surface):
        self.game_screen = screen

        self.translations = game.translations

    def run(self, game, events):
        self.game_screen.fill("white")

        draw_text(self.game_screen, TITLE_FONT_PATH, 80, get_text(self.translations, game.current_lang, "wingame-title"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 - 90)
        draw_text(self.game_screen, TITLE_FONT_PATH, 60, get_text(self.translations, game.current_lang, "wingame_subtitle"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-m-to-menu"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-r-to-restart"), "black", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "MENU"
                elif e.key == pygame.K_r:
                    return "RESTART_LEVEL"
                
        return "WINSCREEN"