import sys
import os
from ui.button import Button
import pygame

sys.path.append(os.path.abspath(".."))
import settings as main_settings

sys.path.append(os.path.abspath("."))
import settings as menu_settings

# ? Dibujamos el menu principal
def draw_menu(screen, events):

    bg = pygame.image.load("./img/bg.png")
    bg = pygame.transform.scale(bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
    screen.blit(bg, (0,0))

    # ? Botones del menu
    play_btn = Button(screen, (0, 310), main_settings.FONT, 250, 50, 'Jugar', '#22d3ee', '#06b6d4')
    tutorial_btn = Button(screen, (0, 380), main_settings.FONT, 250, 50, 'Tutorial', '#ef4444', '#dc2626')
    settings_btn = Button(screen, (0, 450), main_settings.FONT, 250, 50, 'Settings', '#a8a29e', '#78716c')

    play_btn.draw()
    tutorial_btn.draw()
    settings_btn.draw()

    # ? Recorremos los eventos
    for event in events:
        if play_btn.is_clicked(event):
            return "PLAYING"

        elif tutorial_btn.is_clicked(event):
            return "TUTORIAL"

        elif settings_btn.is_clicked(event):
            return "SETTINGS"

    return "MENU"
