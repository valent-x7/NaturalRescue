import pygame
from settings import *
import math
import random

STEP_DURATION = 0.3 

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
        self.health = 150

        # Animaciones desde el spritesheet
        self.animations = {
            "down": [
                self.spritesheet.get_sprite(0, 0, self.width, self.height),
                self.spritesheet.get_sprite(32, 0, self.width, self.height),
                self.spritesheet.get_sprite(64, 0, self.width, self.height)
            ],
            "left": [
                self.spritesheet.get_sprite(0, 32, self.width, self.height),
                self.spritesheet.get_sprite(32, 32, self.width, self.height),
                self.spritesheet.get_sprite(64, 32, self.width, self.height)
            ],
            "right": [
                self.spritesheet.get_sprite(0, 64, self.width, self.height),
                self.spritesheet.get_sprite(32, 64, self.width, self.height),
                self.spritesheet.get_sprite(64, 64, self.width, self.height)
            ],
            "up": [
                self.spritesheet.get_sprite(0, 96, self.width, self.height),
                self.spritesheet.get_sprite(32, 96, self.width, self.height),
                self.spritesheet.get_sprite(64, 96, self.width, self.height)
            ]
        }

        self.image = self.animations["down"][1]

        # ---- ALINEAR POSICIÓN A LA CUADRÍCULA ----
        x = (x // TILE) * TILE
        y = (y // TILE) * TILE

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox_rect = self.rect.copy()
        self.start_pos = self.rect.topleft
        self.target_pos = self.rect.topleft

        # Movimiento
        self.vec = pygame.Vector2(0, 0)
        self.direction = "down"
        self.moving = False
        self.collision_sprites = collision_sprites
        self.progress = 0

        # Animación
        self.frame_index = 0
        self.animation_speed = 6  # frames por segundo

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.moving:
            if keys[pygame.K_w]:
                self.try_move(0, -1, "up")
            elif keys[pygame.K_s]:
                self.try_move(0, 1, "down")
            elif keys[pygame.K_a]:
                self.try_move(-1, 0, "left")
            elif keys[pygame.K_d]:
                self.try_move(1, 0, "right")

    def try_move(self, dx, dy, direction):
        # Calcular rect de destino
        new_rect = self.hitbox_rect.copy()
        new_rect.x += dx * TILE
        new_rect.y += dy * TILE

        # Colisiones por tiles sólidos
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(new_rect):
                return  # bloqueado

        # Movimiento permitido
        self.moving = True
        self.start_pos = self.hitbox_rect.topleft
        self.target_pos = (self.start_pos[0] + dx * TILE,
                           self.start_pos[1] + dy * TILE)
        self.direction = direction
        self.progress = 0

    def move(self, dt):
        if self.moving:
            self.progress += dt / STEP_DURATION
            if self.progress >= 1:
                self.progress = 1
                self.moving = False

            # Interpolación lineal
            new_x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * self.progress
            new_y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * self.progress

            # Alineamos siempre a múltiplos de TILE
            new_x = round(new_x / TILE) * TILE if not self.moving else int(new_x)
            new_y = round(new_y / TILE) * TILE if not self.moving else int(new_y)

            self.hitbox_rect.topleft = (new_x, new_y)
            self.rect.center = self.hitbox_rect.center

    def animate(self, dt):
        if self.moving:
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 0
            self.image = self.animations[self.direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.direction][1]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)

# ? Clase Sprite Normal
class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups, position, image):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

# ? Clase Sprite de Collisión     
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, groups, name, position, image):
        super().__init__(groups)
        self.name = name
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.mask = pygame.mask.from_surface(self.image)

# ? Clase de los sprites!!
class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.camera_offset = pygame.Vector2(0, 0)
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        self.zoom = 2

    # ? Metodo para centrar la camara en el jugador
    def center_on_target(self, target, map_width, map_height):
        screen_w = self.display_surface.get_width() / self.zoom
        screen_h = self.display_surface.get_height() / self.zoom

        x = target.rect.centerx - (screen_w / 2)
        y = target.rect.centery - (screen_h / 2)

        if map_width > screen_w:
            x = max(0, min(x, map_width - screen_w))
        else:
            x = (map_width - screen_w) / 2

        if map_height > screen_h:
            y = max(0, min(y, map_height - screen_h))
        else:
            y = (map_height - screen_h) / 2

        self.camera_offset.x = x
        self.camera_offset.y = y

    # ? Dibujar sprites
    def draw_sprites(self):
        surface = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)

        for sprite in self.sprites():
            offset_rect = sprite.rect.copy()
            offset_rect.topleft = (sprite.rect.x - self.camera_offset.x, sprite.rect.y - self.camera_offset.y)
            surface.blit(sprite.image, offset_rect)

        scaled_surf = pygame.transform.scale(
            surface,
            (int(surface.get_width() * self.zoom), int(surface.get_height() * self.zoom))
        )

        self.display_surface.blit(scaled_surf, (0, 0))

    # ? Actualizar todos los sprites con dt
    def update(self, dt):
        for sprite in self.sprites():
            sprite.update(dt)
