import pygame
from settings import *
from ui.utils import draw_text, get_text, draw_text_space

class GameOver:
    def __init__(self, game, screen: pygame.Surface, level_id):
        self.game_screen = screen
        self.level_id = level_id

        self.translations = game.translations

    def run(self, game, events):
        self.game_screen.fill("black")

        draw_text(self.game_screen, TITLE_FONT_PATH, 80, get_text(self.translations, game.current_lang, f"gameover-title-{self.level_id}"), "white", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 - 120)
        draw_text_space(self.game_screen, TITLE_FONT_PATH, 50, get_text(self.translations, game.current_lang, f"gameover-subtitle-{self.level_id}"), "white", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 30)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-m-to-menu"), "white", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 265)
        draw_text(self.game_screen, TITLE_FONT_PATH, 36, get_text(self.translations, game.current_lang, "press-r-to-restart"), "white", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 200)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "MENU"
                elif e.key == pygame.K_r:
                    return "RESTART_LEVEL"
                
        return "GAMEOVER"