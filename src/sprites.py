import pygame
from settings import *
import math
import random

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height], pygame.SRCALPHA)
        sprite.blit(self.sheet, (0,0), (x,y,width,height))
        return sprite
    
class Monkey(pygame.sprite.Sprite):
    def __init__(self, spritesheet, x, y):
        super().__init__()
        self.spritesheet = spritesheet
        self.x = x * TILE
        self.y = y * TILE
        self.width = TILE
        self.height = TILE

        self.down_animation = [self.spritesheet.get_sprite(0,0, self.width, self.height), 
                               self.spritesheet.get_sprite(32, 0, self.width, self.height),
                               self.spritesheet.get_sprite(64, 0, self.width, self.height)]
        
        self.left_animation = [self.spritesheet.get_sprite(0, 32, self.width, self.height), 
                               self.spritesheet.get_sprite(32, 32, self.width, self.height),
                               self.spritesheet.get_sprite(64, 32, self.width, self.height)]
        
        self.right_animation = [self.spritesheet.get_sprite(0, 64, self.width, self.height), 
                               self.spritesheet.get_sprite(32, 64, self.width, self.height),
                               self.spritesheet.get_sprite(64, 64, self.width, self.height)]
        
        self.up_animation = [self.spritesheet.get_sprite(0, 96, self.width, self.height), 
                               self.spritesheet.get_sprite(32, 96, self.width, self.height),
                               self.spritesheet.get_sprite(64, 96, self.width, self.height)]
        
        self.image = self.down_animation[1]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

        self.direction = "down"
        self.frame = 1
        self.animation_speed = 0.12

    def update(self, keys_pressed, delta_time): 
        moving = False

        # ? Definimos la velocidad usando dt
        speed = MONKEY_SPEED * delta_time

        if keys_pressed[pygame.K_s]:
            self.rect.y += speed
            self.direction = "down"
            moving = True
        elif keys_pressed[pygame.K_w]:
            self.rect.y -= speed
            self.direction = "up"
            moving = True
        elif keys_pressed[pygame.K_a]:
            self.rect.x -= speed
            self.direction = "left"
            moving = True
        elif keys_pressed[pygame.K_d]:
            self.rect.x += speed
            self.direction = "right"
            moving = True

        if moving: 
            self.frame += self.animation_speed
            if self.direction == "down":
                self.image = self.down_animation[int(self.frame) % len(self.down_animation)]
            elif self.direction == "up":
                self.image = self.up_animation[int(self.frame) % len(self.up_animation)]
            elif self.direction == "left":
                self.image = self.left_animation[int(self.frame) % len(self.left_animation)]
            elif self.direction == "right":
                self.image = self.right_animation[int(self.frame) % len(self.right_animation)]
        else:
            if self.direction == "down":
                self.image = self.down_animation[1]
            elif self.direction == "up":
                self.image = self.up_animation[1]
            elif self.direction == "right":
                self.image = self.right_animation[1]
            elif self.direction == "left":
                self.image = self.left_animation[1]
        
        
