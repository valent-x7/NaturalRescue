import pygame
from settings import *
from ui.utils import draw_text, get_text

def draw_winscreen(screen, events, translations, current_lang):
    screen.fill("white")

    draw_text(screen, TITLE_FONT_PATH, 80, get_text(translations, current_lang, "wingame_title"), "black", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/3-90)
    draw_text(screen, TITLE_FONT_PATH, 60, get_text(translations, current_lang, "wingame_subtitle"), "black", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/3)
    draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, current_lang, "press-m-to-menu"), "black", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/2)
    draw_text(screen, TITLE_FONT_PATH, 36, get_text(translations, current_lang, "press-r-to-restart"), "black", WINDOW_WIDTH/2+80, WINDOW_HEIGHT/2 + 50)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            if event.key == pygame.K_r:
                return "RESTART_LEVEL"
            
    return "WINSCREEN"