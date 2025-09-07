from settings import *
from button import Button
from utils import draw_text

# ? Dibujamos el juego
def draw_game(screen, events):
    
    screen.fill('#38bdf8')

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"
            
    return "PLAYING"

# ? Dibujamos el menu principal
def draw_menu(screen, events):

    screen.fill('#bef264')

    # ? Botones del menu
    play_btn = Button(screen, (0, 310), FONT, 250, 50, 'Jugar', '#22d3ee', '#06b6d4')
    tutorial_btn = Button(screen, (0, 380), FONT, 250, 50, 'Tutorial', '#ef4444', '#dc2626')
    settings_btn = Button(screen, (0, 450), FONT, 250, 50, 'Settings', '#a8a29e', '#78716c')

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
            print('Settings')

    return "MENU"

def draw_tutorial(screen, events):
    screen.fill("#e7e5e4")
    
    draw_text(screen, 'Use the Keys To Move', "#FFFFFF", 250)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "MENU"

    return "TUTORIAL"