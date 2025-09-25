import pygame, sys
from os.path import join

info = pygame.display.Info()

MONKEY_SPEED = 150
TILE = 32
WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h

FONT = pygame.font.Font(None, 42)