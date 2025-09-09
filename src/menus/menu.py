from settings import *
from ui.button import Button

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
            return "SETTINGS"

    return "MENU"
