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

# ? Dibujamos el menu principal
def draw_menu(screen, events):
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

    # ? Fuentes de texto estilo 8 bit

    # Fuente GRANDE para el título
    fuente_titulo = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 64)

    # Fuente PEQUEÑA para los botones
    fuente_botones = pygame.font.Font("src/menus/fuentestexto/prstartk.ttf", 24)

    # ? Título del videojuego
    title_text = fuente_titulo.render("Título provisional", True, (255, 255, 255))
    text_rect = title_text.get_rect(center=(main_settings.WINDOW_WIDTH / 2, 100))
    screen.blit(title_text, text_rect)

    # ? Botones del menu
    play_btn = Button(screen, (main_settings.WINDOW_WIDTH // 4, 400), 
                      fuente_botones, 300, 90, 'Jugar', 4, "assets/images/play_icon.png", 20, '#34D399', '#10B981')
    tutorial_btn = Button(screen, (main_settings.WINDOW_WIDTH // 4, 520), 
                          fuente_botones, 300, 90, 'Tutorial', 4, "assets/images/tutorial_icon.png", -2, '#FACC15', '#EAB308')
    settings_btn = Button(screen, (main_settings.WINDOW_WIDTH // 4, 640), 
                          fuente_botones, 300, 90, 'Settings', 4, "assets/images/settings_icon.png", -2, '#38BDF8', '#0EA5E9')
    salir_btn = Button(screen, (main_settings.WINDOW_WIDTH // 4, 760), 
                       fuente_botones, 300, 90, 'Salir', 4, "assets/images/salir_icon.png", 20, "#FB923C", "#F97316")

    play_btn.draw()
    tutorial_btn.draw()
    settings_btn.draw()
    salir_btn.draw()

    # ? Personajes en la pantalla del menú
    chango = pygame.image.load("./img/chango.png")
    pinguino = pygame.image.load("./img/pinguino.png")

    # ? Tamaño de la imagen
    pinguino_rect = pinguino.get_rect()

    # ? Calculamos una posición para el pingüino y asignamos una posición fija para el chango.
    posicion_y = 400
    pinguino_x = main_settings.WINDOW_WIDTH - pinguino_rect.width - 80
    chango_x = 900

    # ? Dibujamos el pingüino y el chango en las posiciones calculadas y asignadas previamente.
    screen.blit(pinguino, (pinguino_x, posicion_y))
    screen.blit(chango, (chango_x, posicion_y))

    # ? Recorremos los eventos
    for event in events:
        if play_btn.is_clicked(event):
            return "LEVEL_SELECT"

        elif tutorial_btn.is_clicked(event):
            return "TUTORIAL"

        elif settings_btn.is_clicked(event):
            return "SETTINGS"
        
        elif salir_btn.is_clicked(event):
            return "SALIR"

    return "MENU"
