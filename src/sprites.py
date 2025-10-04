import pygame
from settings import *
import os
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
    def __init__(self, spritesheet, x, y, groups, collision_sprites, damage_sprites, plant_spots):
        super().__init__(groups)
        self.spritesheet = spritesheet
        self.width = TILE
        self.height = TILE
        self.health = MONKEY_HEALTH
        self.seeds = MONKEY_SEEDS

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

        # Cooldown de disparo
        self.cooldown_shot = 500
        self.last_shot = 0

        self.collision_sprites = collision_sprites
        self.damage_sprites = damage_sprites
        self.plant_spots = plant_spots

        self.all_solid_sprites = list(self.collision_sprites) + list(self.damage_sprites) + list(self.plant_spots)

        # ? Sonido de daño
        working_directory = os.getcwd()
        self.hit_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "hit.mp3"))

        self.vec = pygame.Vector2()
        self.last_axis = None

        self.moving = False # -> Por defecto el mono no se mueve

    def plant(self):
        if self.seeds > 0:
            self.seeds -= 1
            print("Arbol plantado, te quedan", self.seeds)
        else:
            print("No tienes mas semillas")

    def update(self, delta_time, events): 
        self.moving = False

        self.input(events)
        self.move(delta_time)
        self.animate(self.moving)

    # Disparar bellotas
    def shoot(self, groups, player, mouse_pos, camera_offset, zoom):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.cooldown_shot:
            # ? Creamos bellota
            Acorn.launch(groups, player, mouse_pos, camera_offset, zoom, self.collision_sprites)
            self.last_shot = current_time

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

        for sprite in self.all_solid_sprites:
            # ? Checamos si hay colisión
            if sprite.rect.colliderect(self.hitbox_rect):

                # Tipo de sprite
                is_SpriteDamage = getattr(sprite, "sprite_type", None) == "Damage"

                # Push si es de daño
                push_offset = 5 if is_SpriteDamage else 0

                # ? Colisión horizontal
                if direction == "horizontal":
                    if self.vec.x > 0:
                        self.hitbox_rect.right = sprite.rect.left - push_offset
                    if self.vec.x < 0:
                        self.hitbox_rect.left = sprite.rect.right + push_offset
                # ? Colisión vertical
                else:
                    if self.vec.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top - push_offset
                    if self.vec.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom + push_offset
                
                # Si es de daño bajamos vida y activamos sonido
                if is_SpriteDamage:
                    self.hit_sound.play()
                    self.health -= 10

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
        self.sprite_type = "Collision"
        self.mask = None
        self.image = image
        self.rect = self.image.get_frect(topleft = position)

# ? Sprites de daño
class DamageSprite(pygame.sprite.Sprite):
    def __init__(self, groups, position, image):
        super().__init__(groups)
        self.sprite_type = "Damage"
        self.image = image
        self.rect = self.image.get_frect(topleft = position)

# ? Sprites de lugar de cultivo
class PlantSpot(pygame.sprite.Sprite):
    def __init__(self, groups, x, y):
        super().__init__(groups)

        self.sprite_type = "Collision"

        # Working Directory
        working_directory = os.getcwd()

        # Sonido al plantar
        self.shine_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "shine.mp3"))

        self.is_used = False
        self.death_spot_path = os.path.join(working_directory, "assets", "images", "DeadSpot.png")
        self.spot_path = os.path.join(working_directory, "assets", "images", "brote.png")
        self.image = pygame.image.load(self.death_spot_path).convert_alpha()
        self.rect = self.image.get_frect(topleft = (x - (TILE / 2), y - (TILE / 2)))

    # Checar si el rect colisiona con el jugador
    def check_collision(self, player):
        if player.rect.colliderect(self.rect):
            return True

    # Actualizar la imagen y plantar árbol
    def update(self, player):
        keystate = pygame.key.get_pressed()
        if self.check_collision(player) and keystate[pygame.K_h] and not self.is_used:
            self.is_used = True
            self.shine_sound.play()
            player.plant() # Plantamos
            self.image = pygame.image.load(self.spot_path).convert_alpha() # Cambiamos imagen

# ? Clase de los sprites!!
class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.camera_offset = pygame.Vector2(0, 0)
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        self.zoom = 2

    def update(self, delta_time, events, player = None):
        for sprite in self.sprites():
            if isinstance(sprite, PlantSpot):
                sprite.update(player)
            else:
                sprite.update(delta_time, events)

    # ? Metodo para centrar la camara en el jugador
    def center_on_target(self, target, map_width, map_height):
        # ? Obtenemos los valores reales, basados en el zoom!!
        screen_w = self.display_surface.get_width() / self.zoom
        screen_h = self.display_surface.get_height() / self.zoom

        # Offset calculado para centrar al jugador
        x = target.rect.centerx - (screen_w / 2)
        y = target.rect.centery - (screen_h / 2)

        # ? Limitar movimiento de la cámara
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
        # Superficie base del tamaño de la ventana
        surface = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)

        # ? Dibujar sprites con offset
        for sprite in self.sprites():
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.camera_offset
            surface.blit(sprite.image, offset_rect)

        # ? Escalar la superficie
        scaled_surf = pygame.transform.scale_by(surface, self.zoom)

        # Dibujar superficie
        self.display_surface.blit(scaled_surf, (0, 0))

# ? Clase Bellota
class Acorn(pygame.sprite.Sprite):
    def __init__(self, groups, pos, direction, collision_sprites):
        super().__init__(groups)

        # ? Imagen y gráficos
        working_directory = os.getcwd()
        image_path = os.path.join(working_directory, "assets", "images", "items", "bellota.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (16, 16)).convert_alpha()

        # Rectangulo
        self.rect = self.image.get_frect(center = pos)

        # ? Dirección de la bellota
        if direction.length_squared() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2(0, 0)

        # ? Tiempo de vida y colisión
        self.time_to_live = 1000
        self.collision_sprites = collision_sprites

    def update(self, dt, events = None):
        # Descontamos tiempo de vida
        self.time_to_live -= (dt * 1000)

        # Eliminamos sprite si su tiempo de vida pasó o colisiona
        if self.time_to_live <= 0 or self.check_collisions():
            self.kill()
            print("Bellota eliminada!!!")
        else:
            # Movemos sprite
            self.rect.center += self.direction * ACORN_SPEED * dt
    
    # ? Si choca con un sprite de collision
    def check_collisions(self):
        return pygame.sprite.spritecollideany(self, self.collision_sprites)

    # ? Este metodo creará una clase Acorn
    @classmethod 
    def launch(cls, groups, player, mouse_pos, camera_offset, zoom, collision_sprites):
        # Definimos la posición del jugador
        player_pos = pygame.Vector2(player.rect.center)

        # ? La posición real del mouse cuidando el zoom!!
        mouse_x = (mouse_pos[0] / zoom) + camera_offset.x
        mouse_y = (mouse_pos[1] / zoom) + camera_offset.y

        # Directión objetivo
        target_pos = pygame.Vector2(mouse_x, mouse_y)

        # Dirección
        direction = target_pos - player_pos

        # ? Creamos bellota (Grupo, posicion jugador, dirección, sprites de colisión)
        return cls(groups, player_pos, direction, collision_sprites)