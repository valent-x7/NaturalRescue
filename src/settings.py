import pygame, sys
from os.path import join

info = pygame.display.Info()

MONKEY_SPEED = 176
MONKEY_HEALTH = 120
MONKEY_SEEDS = 6
MONKEY_ACORNS = 100
TILE = 32

ACORN_SPEED = 300

SCIENTIST_SPEED = 128
SCIENTIST_HEALTH = 120

WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h

TITLE_FONT_PATH = "src/menus/fuentestexto/prstartk.ttf"