import sys
import os
from ui.button import Button
import pygame
import math

sys.path.append(os.path.abspath(".."))
import settings as main_settings

sys.path.append(os.path.abspath("."))
import settings as menu_settings

# ? Variables de scroll
scroll_capa2 = 0
scroll_capa3 = 0
scroll_capa4 = 0
scroll_capa5 = 0

# ? Dibujamos el menu principal
def draw_menu(screen, events, bg_width, capa1, capa2, capa3, capa4, capa5, chango, pinguino, pos_y, chango_x, pinguino_x, font_title, play_btn : Button, tut_btn : Button, set_btn : Button, salir_btn : Button):
    global scroll_capa2, scroll_capa3, scroll_capa4, scroll_capa5

    # ? Scroll del background
    # Redondeamos cuantas veces cabe el ancho del fondo en la pantalla, le agregamos 1
    tiles = math.ceil(main_settings.WINDOW_WIDTH / bg_width) + 1

    # Fondito (Capa 1)
    screen.blit(capa1, (0, 0))

    # Dibujamos capa 2
    for i in range(0, tiles + 1):
        screen.blit(capa2, (i * bg_width + scroll_capa2, 0))

    # Dibujamos capa 3
    for i in range(0, tiles + 1):
        screen.blit(capa3, (i * bg_width + scroll_capa3, 0))

    # Dibujamos capa 4
    for i in range(0, tiles + 1):
        screen.blit(capa4, (i * bg_width + scroll_capa4, 0))

    # Dibujamos capa 5
    for i in range(0, tiles + 1):
        screen.blit(capa5, (i * bg_width + scroll_capa5, 0))
    
    # Modificamos scroll
    scroll_capa2 -= 0.2
    scroll_capa3 -= 0.5
    scroll_capa4 -= 1.5
    scroll_capa5 -= 2.5

    # Reseteamos el scroll
    if abs(scroll_capa2) > bg_width:
        scroll_capa2 = 0

    elif abs(scroll_capa3) > bg_width:
        scroll_capa3 = 0

    elif abs(scroll_capa4) > bg_width:
        scroll_capa4 = 0

    elif abs(scroll_capa5) > bg_width:
        scroll_capa5 = 0

    # ? Título del videojuego
    title_surf = font_title.render("Natural rescue", True, (255, 255, 255))
    title_rect = title_surf.get_frect(center = (main_settings.WINDOW_WIDTH / 2, 100))
    screen.blit(title_surf, title_rect)

    # ? Dibujamos botones del menu
    play_btn.draw()
    tut_btn.draw()
    set_btn.draw()
    salir_btn.draw()

    # ? Dibujamos el pingüino y el chango en las posiciones calculadas y asignadas previamente.
    screen.blit(pinguino, (pinguino_x, pos_y))
    screen.blit(chango, (chango_x, pos_y))

    # ? Recorremos los eventos
    for event in events:
        if play_btn.is_clicked(event):
            return "LEVEL_SELECT"

        elif tut_btn.is_clicked(event):
            return "TUTORIAL"

        elif set_btn.is_clicked(event):
            return "SETTINGS"
        
        elif salir_btn.is_clicked(event):
            return "SALIR"

    return "MENU"
