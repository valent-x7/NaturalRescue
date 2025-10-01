import pygame
pygame.init()

from game import Game

g = Game("MENU")

if __name__ == "__main__":
    g.run()