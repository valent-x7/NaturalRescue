import pygame, sys
from os.path import join

pygame.init()

info = pygame.display.Info()

WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h

FONT = pygame.font.Font(None, 42)