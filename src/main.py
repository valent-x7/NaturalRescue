import pygame
from scenes.intro import playIntro

pygame.init()

from game import Game

g = Game("MENU")

if __name__ == "__main__":
    playIntro()
    g.run()