# -> Aquí se haran las configuraciones del juego
from settings import *
from ui.utils import draw_text, set_language, get_text, load_language
from ui.button import Button
from math import ceil

# Cargamos el diccionario de traducciones
translations = load_language("languajes.json")

# ? Scroll capa 2
scroll_capa2 = 0

def draw_settings(screen, game, events, bg_width, capa1, capa2, arrow_img, english_button: Button, spanish_button : Button):
    
    global scroll_capa2

    screen.blit(capa1, (0, 0))

    tiles = ceil(WINDOW_WIDTH / bg_width) + 1

    # ? Dibujamos capa 2
    for i in range(0, tiles + 1):
        screen.blit(capa2, (i * bg_width + scroll_capa2, 0))

    # Modificamos scroll
    scroll_capa2 -= 2.5

    # Lo reseteamos
    if abs(scroll_capa2) > bg_width:
        scroll_capa2 = 0

    # Titulo de settings
    draw_text(screen, TITLE_FONT_PATH, 52, get_text(translations, game.current_lang, "settings-title"), "#FFFFFF", WINDOW_WIDTH / 2, 150)
 
    # Subtitulo de idioma
    draw_text(screen, TITLE_FONT_PATH, 42, get_text(translations, game.current_lang, "settings-language"), "#FFFFFF", WINDOW_WIDTH / 2, 300)

    arrow_rect = arrow_img.get_frect()

    # ? Definimos la pos de la flecha
    arrow_rect.centerx = WINDOW_WIDTH / 2 - arrow_rect.width - 140

    # Defimos y en base al lenguaje
    if game.current_lang == "en":
        arrow_rect.centery = 400
    else:
        arrow_rect.centery = 520

    screen.blit(arrow_img, arrow_rect)

    # Dibujamos botones
    english_button.draw()
    spanish_button.draw()

    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            
        elif english_button.is_clicked(event):
            set_language("config.json", "en")
            game.current_lang = "en"
            game.setup_menu()
            game.setup_settings()

        elif spanish_button.is_clicked(event):
            set_language("config.json", "es")
            game.current_lang = "es"
            game.setup_menu()
            game.setup_settings()
            
    return "SETTINGS"