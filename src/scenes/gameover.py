import pygame
from settings import *
from ui.utils import draw_text, get_text

def draw_gameover(screen, events, translations, current_lang):
    screen.fill("black")

    draw_text(screen, TITLE_FONT_PATH, 80, "GAME OVER", "white", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/3)

    draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, current_lang, "gameover-instructions"), "white", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/2)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            if event.key == pygame.K_r:
                return "LEVEL_SELECT"
            
    return "GAMEOVER"