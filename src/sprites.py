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
    def __init__(self, spritesheet, x, y, groups, collision_sprites):
        super().__init__(groups)
        self.spritesheet = spritesheet
        self.width = TILE
        self.height = TILE
        self.health = MONKEY_HEALTH

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
        self.rect = self.image.get_frect(topleft = (x - self.width // 2, y - self.height // 2))
        self.hitbox_rect = self.rect.inflate(-14, -10)

        self.mask = pygame.mask.from_surface(self.image)

        self.direction = "down"
        self.frame = 1
        self.animation_speed = 0.1

        self.collision_sprites = collision_sprites

        self.vec = pygame.Vector2()
        self.last_axis = None

        self.moving = False # -> Por defecto el mono no se mueve

    def update(self, delta_time, events): 
        self.moving = False

        self.input(events)
        self.move(delta_time)
        self.animate(self.moving)

    def input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_d):
                    self.last_axis = "x"
                elif event.key in (pygame.K_w, pygame.K_s):
                    self.last_axis = "y"

        keyState = pygame.key.get_pressed()
        self.vec.x = int(keyState[pygame.K_d]) - int(keyState[pygame.K_a]) # -> Izquierda o derecha
        self.vec.y = int(keyState[pygame.K_s]) - int(keyState[pygame.K_w]) # -> Arriba o abajo

        # ? Anulamos movimiento diagonal
        if self.vec.x != 0 and self.vec.y != 0:
            if self.last_axis == "x":
                self.vec.y = 0
            elif self.last_axis == "y":
                self.vec.x = 0
            else:
                self.vec.y = 0

    # ? Movimiento del personaje
    def move(self, dt):
        self.hitbox_rect.x += self.vec.x * MONKEY_SPEED * dt
        self.collision("horizontal")
        self.hitbox_rect.y += self.vec.y * MONKEY_SPEED * dt
        self.collision("vertical")
        self.rect.center = self.hitbox_rect.center

        # Variables para animación
        if self.vec.y == 1:
            self.direction = "down"
            self.moving = True
        elif self.vec.y == -1:
            self.direction = "up"
            self.moving = True
        elif self.vec.x == 1:
            self.direction = "right"
            self.moving = True
        elif self.vec.x == -1:
            self.direction = "left"
            self.moving = True

    def animate(self, moving):
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

    # ? Función para ver colisiones
    def collision(self, direction):
        for sprite in self.collision_sprites:

            # ? Colision rectangular
            if sprite.rect.colliderect(self.hitbox_rect):
                # ? Si es colision horizontal
                if direction == "horizontal":
                    if self.vec.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.vec.x < 0: self.hitbox_rect.left = sprite.rect.right
                # ? Si es colision vertical
                else:
                    if self.vec.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.vec.y < 0: self.hitbox_rect.top = sprite.rect.bottom

# ? Clase Sprite Normal
class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups, position, image):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = position)

# ? Clase Sprite de Collisión     
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, groups, name, position, image):
        super().__init__(groups)
        self.name = name
        self.mask = None
        self.image = image
        self.rect = self.image.get_frect(topleft = position)