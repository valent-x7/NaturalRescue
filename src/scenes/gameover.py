import pygame
from settings import *
from ui.utils import draw_text, get_text

def draw_gameover(screen, events, translations, current_lang):
    screen.fill("black")

    draw_text(screen, TITLE_FONT_PATH, 80, get_text(translations, current_lang, "gameover-title"), "white", WINDOW_WIDTH/2, WINDOW_HEIGHT/3)
    draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, current_lang, "press-m-to-menu"), "white", WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
    draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, current_lang, "press-r-to-restart"), "white", WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            if event.key == pygame.K_r:
                return "RESTART_LEVEL"
            
    return "GAMEOVER"
