from settings import *

def draw_text(screen, text, color, y):
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_frect()
    
    text_rect.centerx = WINDOW_WIDTH / 2
    text_rect.centery = y

    screen.blit(text_surface, text_rect)