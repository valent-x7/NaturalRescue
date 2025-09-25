import sys
import os
from ui.button import Button
import pygame
import math

sys.path.append(os.path.abspath(".."))
import settings as main_settings

sys.path.append(os.path.abspath("."))
import settings as menu_settings

# ? Variable global para definir el scroll
scroll = 0

# ? Fondo principal
bg = pygame.image.load(os.path.join(os.path.dirname(__file__),
                           "..", "..", "assets", "images", "FonditoPro.png"))
bg_scaled = pygame.transform.scale(bg, (main_settings.WINDOW_WIDTH, main_settings.WINDOW_HEIGHT))
# Conseguimos el ancho del fondo
bg_width = bg_scaled.get_width()

# ? Pinguino y mono
chango = pygame.image.load("./img/chango.png")
pinguino = pygame.image.load("./img/pinguino.png")

# Tamaño de la imagen
pinguino_rect = pinguino.get_rect()

# Calculamos una posición para el pingüino y asignamos una posición fija para el chango.
posicion_y = 400
pinguino_x = main_settings.WINDOW_WIDTH - pinguino_rect.width - 80
chango_x = 900

# ? Dibujamos el menu principal
def draw_menu(screen, events, font_title, play_btn : Button, tut_btn : Button, set_btn : Button, salir_btn : Button):
    global scroll

    # ? Scroll del background
    # Redondeamos cuantas veces cabe el ancho del fondo en la pantalla, le agregamos 1
    tiles = math.ceil(main_settings.WINDOW_WIDTH / bg_width) + 1

    # Recorremos los tiles para dibujar el fondo varias veces
    for i in range(0, tiles):
        screen.blit(bg_scaled, (i * bg_width + scroll, 0))

    # Disminuimos el scroll
    scroll -= 2

    # Si el valor absoluto del scroll es mayor al ancho del fondo
    if abs(scroll) > bg_width:
        scroll = 0

    # ? Título del videojuego
    title_surf = font_title.render("Titulo provisional", True, (255, 255, 255))
    title_rect = title_surf.get_frect(center = (main_settings.WINDOW_WIDTH / 2, 100))
    screen.blit(title_surf, title_rect)

    # ? Dibujamos botones del menu
    play_btn.draw()
    tut_btn.draw()
    set_btn.draw()
    salir_btn.draw()

    # ? Dibujamos el pingüino y el chango en las posiciones calculadas y asignadas previamente.
    screen.blit(pinguino, (pinguino_x, posicion_y))
    screen.blit(chango, (chango_x, posicion_y))

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
