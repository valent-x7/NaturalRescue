import pygame
pygame.init()

from game import Game

g = Game("PLAYING")

if __name__ == "__main__":
    g.run()