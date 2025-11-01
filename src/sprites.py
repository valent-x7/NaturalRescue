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
    def __init__(self, spritesheet, x, y, groups, collision_sprites, water_collision_sprites, damage_sprites, plant_spots):
        super().__init__(groups)
        self.spritesheet = spritesheet
        self.width = TILE
        self.height = TILE
        self.health = MONKEY_HEALTH
        self.seeds = MONKEY_SEEDS
        self.acorns = MONKEY_ACORNS
        self.trees = 0

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
        self.animation_speed = 8

        # Cooldown de disparo
        self.cooldown_shot = 500
        self.last_shot = 0

        # Cooldown de riego
        self.can_water = True
        self.water_cooldown = 500
        self.last_water_time = 0

        self.collision_sprites = collision_sprites
        self.water_collision_sprites = water_collision_sprites
        self.damage_sprites = damage_sprites
        self.plant_spots = plant_spots

        self.all_solid_sprites = list(self.collision_sprites) + list(self.water_collision_sprites) + list(self.damage_sprites) + list(self.plant_spots)

        # ? Sonidos
        working_directory = os.getcwd()
        self.hit_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "hit.mp3")) # Sonido de daño
        self.refill_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "refill.mp3")) # Refill

        self.vec = pygame.Vector2()
        self.last_axis = None

        self.moving = False # -> Por defecto el mono no se mueve

        # ? Inmunidad
        self.invincible = False
        self.invincibily_duration = 1000 # -> # 1 segundo
        self.hit_time = 0

        # ? Recursos de agua del jugador
        self.water_amount = 0
        self.max_player_water = 50

    def plant(self):
        if self.seeds > 0:
            self.seeds -= 1
            print("Arbol plantado, te quedan", self.seeds)
        elif self.seeds == 0:
            pass

        else:
            print("No tienes mas semillas")

    def update(self, delta_time, events):
        current_time = pygame.time.get_ticks()

        self.moving = False

        self.update_invincibility(current_time)
        self.input(events)
        self.check_water_interaction(current_time)
        self.move(delta_time)
        self.animate(self.moving, delta_time)

    # ? Checar interacción con el agua
    def check_water_interaction(self, current_time):
        keystate = pygame.key.get_pressed()

        # Si el jugador colisiona con el agua!
        is_colliding = pygame.sprite.spritecollideany(self, self.water_collision_sprites)

        # Si colisiona, presiona h y puede interactuar con agua
        if is_colliding and keystate[pygame.K_h] and self.can_water:

            # ? Aplicamos cooldown para que no presione h infinitamente
            self.can_water = False
            self.last_water_time = current_time

            # ? Llenar agua
            if self.water_amount < self.max_player_water:
                self.refill_sound.play() # Tocamos sonido de refill
                self.water_amount += 25
                print(self.water_amount)

    # Disparar bellotas
    def shoot(self, groups, player, mouse_pos, camera_offset, zoom):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.cooldown_shot and self.acorns > 0:
            # ? Creamos bellota
            Acorn.launch(groups, player, mouse_pos, camera_offset, zoom, self.collision_sprites)
            self.last_shot = current_time
            self.acorns -= 1

    def input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
                    self.last_axis = "x"
                elif event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                    self.last_axis = "y"

        keyState = pygame.key.get_pressed()

        # -> Izquierda o derecha
        self.vec.x = (int(keyState[pygame.K_d]) or int(keyState[pygame.K_RIGHT])) - (int(keyState[pygame.K_a]) or int(keyState[pygame.K_LEFT]))
        # -> Arriba o abajo
        self.vec.y = (int(keyState[pygame.K_s]) or int(keyState[pygame.K_DOWN])) - (int(keyState[pygame.K_w]) or int(keyState[pygame.K_UP]))

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

    def animate(self, moving, delta_time):
        if moving: 
            self.frame += self.animation_speed * delta_time
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

    # Checar si estamos inmunes
    def update_invincibility(self, current_time):
        if self.invincible:
            if current_time - self.hit_time >= self.invincibily_duration:
                self.invincible = False

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
                
                # Si es de daño y no estamos inmunes
                if is_SpriteDamage and not self.invincible:
                    self.hit_sound.play()
                    self.health -= 10

                    # ? Activamos inmunidad
                    self.invincible = True
                    self.hit_time = pygame.time.get_ticks()
                
                # Si estamos inmunes
                # elif is_SpriteDamage and self.invincible:
                #     pass

class Penguin(pygame.sprite.Sprite):
    def __init__(self, x, y, spritesheet):
        super().__init__()
        self.spritesheet = spritesheet
        self.w = TILE
        self.h = TILE
        self.moving = False
        self.direction = 'down'
        self.frame = 1
        self.animation_speed = 8

        self.y_vel = 0
        self.on_ground = False
        self.x_vel = 0  

        self.alive = True

        self.down_animation = [self.spritesheet.get_sprite(0,0, self.w, self.h), 
                               self.spritesheet.get_sprite(32, 0, self.w, self.h),
                               self.spritesheet.get_sprite(64, 0, self.w, self.h)]
        
        self.left_animation = [self.spritesheet.get_sprite(0, 32, self.w, self.h), 
                               self.spritesheet.get_sprite(32, 32, self.w, self.h),
                               self.spritesheet.get_sprite(64, 32, self.w, self.h)]
        
        self.right_animation = [self.spritesheet.get_sprite(0, 64, self.w, self.h), 
                               self.spritesheet.get_sprite(32, 64, self.w, self.h),
                               self.spritesheet.get_sprite(64, 64, self.w, self.h)]
        
        self.up_animation = [self.spritesheet.get_sprite(0, 96, self.w, self.h), 
                               self.spritesheet.get_sprite(32, 96, self.w, self.h),
                               self.spritesheet.get_sprite(64, 96, self.w, self.h)]
        
        self.image = self.down_animation[1]
        self.frame = 1
        
        self.rect = self.image.get_frect(topleft = (x - self.w // 2, y - self.h // 2))
        self.hitbox_rect = self.rect.inflate(-14, -10)
    
    def animate(self, moving, delta_time):
        if moving: 
            self.frame += self.animation_speed * delta_time
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

    def damage(self):
        self.alive = False
        self.kill()

    def update(self, platforms, delta_time):

        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        self.animate(self.moving, delta_time)

        self.moving = False
        self.x_vel = 0  # Resetear velocidad horizontal cada frame

        # Movimiento horizontal
        if keys[pygame.K_a]:
            self.direction = 'left'
            self.moving = True
            self.x_vel = -3
        if keys[pygame.K_d]:
            self.direction = 'right'
            self.moving = True
            self.x_vel = 3

        # Salto
        if keys[pygame.K_w] and self.on_ground:
            self.direction = 'up'
            self.moving = True
            self.y_vel = -10
            self.on_ground = False

        # Aplicar gravedad
        self.y_vel += 0.55
        
        # MOVIMIENTO HORIZONTAL CON DETECCIÓN DE COLISIONES
        self.rect.x += self.x_vel
        
        # Verificar colisiones horizontales
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.x_vel > 0:  # Moviéndose a la derecha
                    self.rect.right = platform.rect.left
                elif self.x_vel < 0:  # Moviéndose a la izquierda
                    self.rect.left = platform.rect.right
        
        # MOVIMIENTO VERTICAL CON DETECCIÓN DE COLISIONES
        self.rect.y += self.y_vel
        
        # Verificar colisiones verticales
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_vel > 0:  # Cayendo
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0
                    self.on_ground = True
                elif self.y_vel < 0:  # Saltando
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0
        
        # Actualizar hitbox (si la usas para algo)
        self.hitbox_rect.center = self.rect.center

class Scientist(pygame.sprite.Sprite):
    def __init__(self, spritesheet: Spritesheet, groups, position, collision_sprites):
        super().__init__(groups)
        self.wd = os.getcwd()

        self.collision_sprites = collision_sprites

        # ? Frames (imagenes)
        self.down_frames = [spritesheet.get_sprite(0, 0, TILE, TILE),
                            spritesheet.get_sprite(32, 0, TILE, TILE),
                            spritesheet.get_sprite(64, 0, TILE, TILE)]
        
        self.left_frames = [spritesheet.get_sprite(0, 32, TILE, TILE),
                            spritesheet.get_sprite(32, 32, TILE, TILE),
                            spritesheet.get_sprite(64, 32, TILE, TILE)]
        
        self.right_frames = [spritesheet.get_sprite(0, 64, TILE, TILE),
                            spritesheet.get_sprite(32, 64, TILE, TILE),
                            spritesheet.get_sprite(64, 64, TILE, TILE)]
        
        self.up_frames = [spritesheet.get_sprite(0, 96, TILE, TILE),
                            spritesheet.get_sprite(32, 96, TILE, TILE),
                            spritesheet.get_sprite(64, 96, TILE, TILE)]
    
        self.current_frame = 1
        self.direction_frame = "down" # -> Imagen (Player caminando hacia abajo)
        self.image = self.down_frames[self.current_frame] # -> Imagen de inicio

        self.rect = self.image.get_frect(topleft = (position[0] - TILE // 2, position[1] - TILE // 2)) # -> Rect
        self.hitbox_rect = self.rect.inflate(-14, -10) # -> Hitbox Rect

        # ? Sounds
        self.footsteps_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "footsteps_metal.mp3"))
        self.ouch_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "ouch.mp3"))

        # ? Attributes
        self.valves = 0 # -> Valves closed
        self.can_be_damaged = True # -> Puede ser dañado
        self.last_time_damaged = 0
        self.damage_cooldown = 2000 # -> Cooldown
        self.moving = False # -> Por defecto el jugador no se mueve
        self.direction_vector = pygame.Vector2() # -> Vector de dirección
        self.last_axis = None # -> Ultima tecla
        self.health = SCIENTIST_HEALTH
        self.speed = SCIENTIST_SPEED
        self.animation_speed = 14

    # ? Actualizar jugador
    def update(self, delta_time, events):
        self.moving = False
        self.check_damage()
        self.input(events)
        self.move(delta_time)
        self.animate(self.moving, delta_time)

    def input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
                    self.last_axis = "x"
                elif event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                    self.last_axis = "y"

        keyState = pygame.key.get_pressed()

        # -> Izquierda o derecha
        self.direction_vector.x = (int(keyState[pygame.K_d]) or int(keyState[pygame.K_RIGHT])) - (int(keyState[pygame.K_a]) or int(keyState[pygame.K_LEFT]))
        # -> Arriba o abajo
        self.direction_vector.y = (int(keyState[pygame.K_s]) or int(keyState[pygame.K_DOWN])) - (int(keyState[pygame.K_w]) or int(keyState[pygame.K_UP]))

        # ? Anulamos movimiento diagonal
        if self.direction_vector.x != 0 and self.direction_vector.y != 0:
            if self.last_axis == "x":
                self.direction_vector.y = 0
            elif self.last_axis == "y":
                self.direction_vector.x = 0
            else:
                self.direction_vector.y = 0

    # ? Mover jugador
    def move(self, delta_time):
        self.hitbox_rect.x += self.direction_vector.x * self.speed * delta_time
        self.collision("horizontal")
        self.hitbox_rect.y += self.direction_vector.y * self.speed * delta_time
        self.collision("vertical")
        self.rect.center = self.hitbox_rect.center

        # Variables para animación
        if self.direction_vector.y == 1:
            self.direction_frame = "down"
            self.moving = True
        elif self.direction_vector.y == -1:
            self.direction_frame = "up"
            self.moving = True
        elif self.direction_vector.x == 1:
            self.direction_frame = "right"
            self.moving = True
        elif self.direction_vector.x == -1:
            self.direction_frame = "left"
            self.moving = True

    # ? Checar colisiones
    def collision(self, direction):
        for sprite in self.collision_sprites:
            # * Si hay colisión
            if sprite.rect.colliderect(self.hitbox_rect):
                # ? Colisión horizontal
                if direction == "horizontal":
                    if self.direction_vector.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction_vector.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                # ? Colisión vertical
                elif direction == "vertical":
                    if self.direction_vector.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction_vector.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom                       

    # ? Animar jugador
    def animate(self, moving, delta_time):
        if moving:
            self.current_frame += self.animation_speed * delta_time # -> Aumentamos frame
            
            if self.direction_frame == "down":
                self.image = self.down_frames[int(self.current_frame) % len(self.down_frames)]
            elif self.direction_frame == "up":
                self.image = self.up_frames[int(self.current_frame) % len(self.up_frames)]
            elif self.direction_frame == "right":
                self.image = self.right_frames[int(self.current_frame) % len(self.right_frames)]
            elif self.direction_frame == "left":
                self.image = self.left_frames[int(self.current_frame) % len(self.left_frames)]

            if not self.footsteps_sound.get_num_channels(): # -> Sonido de pasos
                self.footsteps_sound.play(-1)
        
        else:
            if self.direction_frame == "down":
                self.image = self.down_frames[1]
            elif self.direction_frame == "up":
                self.image = self.up_frames[1]
            elif self.direction_frame == "right":
                self.image = self.right_frames[1]
            elif self.direction_frame == "left":
                self.image = self.left_frames[1]

            self.footsteps_sound.stop() # -> Detener el sonido de pasos

    def check_damage(self):
        if not self.can_be_damaged:
            self.image.set_alpha(150)
            now = pygame.time.get_ticks()
            # -> Ultima vez que recibió daño
            if now - self.last_time_damaged >= self.damage_cooldown:
                self.can_be_damaged = True
                self.image.set_alpha(255) # -> Efecto de transparencia
        else:
            self.image.set_alpha(255)

# ? Clase Sprite Normal
class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups, position, image):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = position)

# ? Clase Sprite de Collisión de Agua   
class WaterCollisionSprite(pygame.sprite.Sprite):
    def __init__(self, groups, name, position, image):
        super().__init__(groups)
        self.name = name
        self.sprite_type = "Water Collision"
        self.mask = None
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

# ? Sprite de colisión por rect (Mejor colisión)
class CollisionSpriteRect(pygame.sprite.Sprite):
    def __init__(self, groups, x, y, width, height):
        super().__init__(groups)
        self.sprite_type = "Collision"
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # self.image.fill('red')

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

        # Imagenes de estado
        self.image_states = {
            "full": os.path.join(working_directory, "assets", "images", "brote_full.png"),
            "high": os.path.join(working_directory, "assets", "images", "brote_high.png"),
            "mid": os.path.join(working_directory, "assets", "images", "brote_mid.png"),
            "low": os.path.join(working_directory, "assets", "images", "brote_low.png"),
            "born": os.path.join(working_directory, "assets", "images", "brote_born.png"),
            "dead": os.path.join(working_directory, "assets", "images", "DeadSpot.png"),
        }

        # ? Cargar imagenes de estado
        self.loaded_images = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in self.image_states.items()
        }

        # ? Sonidos
        self.shine_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "shine.mp3")) # Plantar
        self.error_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "error.mp3")) # Error al plantar
        self.upgrade_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "upgrade.mp3")) # Mejora de planta
        self.success_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "success.mp3")) # Planta completa

        # Atributos
        self.is_used = False # -> El spot esta usado ?
        self.is_complete = False # -> El spot esta completado ? 
        self.max_water = 100
        self.current_water = 0

        # ? Imagen inicial
        self.image = self.loaded_images["dead"]
        
        self.rect = self.image.get_frect(topleft = (x - (TILE / 2), y - (TILE / 2)))

    # Checar si el rect colisiona con el jugador
    def check_collision(self, player):
        if player.rect.colliderect(self.rect):
            return True
        
    # Devolver la imagen en base al porcentaje de agua
    def get_image_by_water(self):
        if self.max_water <= 0:
            return self.image_states["dead"]
        
        if self.is_complete: # -> Si ya está completo
            return self.loaded_images["full"]

        if self.current_water > 75 and self.is_used:
            key = "full" # -> Devuelve brote.full
        elif self.current_water > 50 and self.is_used:
            key = "high" # -> Devuelve brote.high
        elif self.current_water > 25 and self.is_used:
            key = "mid" # -> Devuelve brote.mid
        elif self.current_water > 0 and self.is_used:
            key = "low" # -> Devuelve brote.low
        elif self.current_water == 0 and self.is_used:
            key = "born" # -> Devuelve brote born
        else:
            key = "dead" # -> Spot vacío

        return self.loaded_images[key] # Devuelve la imagen ya cargada con convert_alpha

    # Actualizar la imagen y plantar árbol
    def update(self, player, dt):
        keystate = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # ? Cooldown de riego de player
        if not player.can_water and current_time - player.last_water_time >= player.water_cooldown:
            player.can_water = True # El jugador ahora puede plantar

        if self.is_complete:
            return # -> Si esta completo, no hacemos nada

        if self.check_collision(player) and keystate[pygame.K_h] and player.can_water:

            # Cooldown de riego
            player.can_water = False
            player.last_water_time = current_time # Guardamos el tiempo actual

            if not self.is_used: # -> Si el espacio no esta usado
                self.is_used = True # -> Plantar
                self.shine_sound.play()
                player.plant()
                self.current_water = 0

            else: # -> Si ya esta usado
                # ? Spot a llenar
                if player.water_amount > 0 and self.current_water < self.max_water:
                    player.water_amount -= 25 # Restamos agua al jugador
                    self.upgrade_sound.play()
                    self.current_water += 25 # Añadimos el agua al spot
                    self.current_water = min(self.current_water, self.max_water)  # Que no exceda el máximo

                    # ? Si ya se llenó al regar
                    if self.current_water == self.max_water:
                        self.success_sound.play() # -> Sonido de éxito
                        player.trees += 1 # -> Le sumamos al jugador
                        print(f"Árbol(es) completado(s): {player.trees}")
                        self.is_complete = True # -> Completado
                
                else: # -> Si no hay agua para regar
                    self.error_sound.play()

            # ? Cambiamos imagen si o si
            self.image = self.get_image_by_water()

# ? Valvula
class Valve(pygame.sprite.Sprite):
    def __init__(self, groups, position):
        super().__init__(groups)
        self.wd = os.getcwd() # -> Get working direction

        self.frames = [pygame.image.load(os.path.join(self.wd, "assets", "images", "valve", f"{i}.png")).convert_alpha() for i in range(1, 7)]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_frect(topleft = (position))
        self.hitbox_rect = self.rect.inflate(-5, -20)

        # ? Atributes
        self.animation_speed = 10
        self.is_leaking = True # -> Tiene fuga activada

    def update(self, player, delta_time):
        keystate = pygame.key.get_pressed()

        if self.check_player_collision(player) and keystate[pygame.K_h]:
            self.is_leaking = False

        self.animate(delta_time)

    def check_player_collision(self, player):
        if player.rect.colliderect(self.hitbox_rect):
            return True

    def animate(self, delta_time):
        if self.is_leaking:
            self.current_frame += self.animation_speed * delta_time
            self.image = self.frames[int(self.current_frame) % len(self.frames)]
        else:
            self.image = self.frames[0]

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
                sprite.update(player, delta_time)
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
        
# ? Clase de los sprites!!
class AllSprites3(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.camera_offset = pygame.Vector2(0, 0)
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        self.background_sprites = pygame.sprite.Group()
        self.depth_sprites = pygame.sprite.Group()

        self.zoom = 2

    def update(self, delta_time, events, player = None):
        for sprite in self.sprites():
            if isinstance(sprite, Valve):
                sprite.update(player, delta_time)
            else:
                sprite.update(delta_time, events)

    # ? Metodo para centrar la camara en el jugador
    def center_on_target(self, target):
        # ? Obtenemos los valores reales, basados en el zoom!!
        screen_w = self.display_surface.get_width() / self.zoom
        screen_h = self.display_surface.get_height() / self.zoom

        # Offset calculado para centrar al jugador
        self.camera_offset.x = target.rect.centerx - (screen_w / 2)
        self.camera_offset.y = target.rect.centery - (screen_h / 2)

    # ? Dibujar sprites
    def draw_sprites(self):
        # Superficie base del tamaño de la ventana
        surface = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)

        # ? Dibujar sprites con offset
        for sprite in self.background_sprites:
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.camera_offset
            surface.blit(sprite.image, offset_rect)

        for sprite in sorted(self.depth_sprites, key = lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.camera_offset
            surface.blit(sprite.image, offset_rect)

        # ? Escalar la superficie
        scaled_surf = pygame.transform.scale_by(surface, self.zoom)

        # Dibujar superficie
        self.display_surface.blit(scaled_surf, (0, 0))


# ? Clase Platano
class Acorn(pygame.sprite.Sprite):
    def __init__(self, groups, pos, direction, collision_sprites):
        super().__init__(groups)

        # ? Imagen y gráficos
        working_directory = os.getcwd()
        image_path = os.path.join(working_directory, "assets", "images", "items", "platano.png")
        original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (28, 28)).convert_alpha()
        self.image = self.original_image

        # ? Audio del platano
        self.throw_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "throw.ogg"))
        self.throw_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(os.path.join(working_directory, "assets", "sound", "impact.ogg"))
        self.impact_sound.set_volume(0.8)

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

        # ? Rotación
        self.angle = 0
        self.rotation_speed = 360

        # ? Sonido de throw
        self.throw_sound.play()

    def update(self, dt, events = None):
        # Descontamos tiempo de vida
        self.time_to_live -= (dt * 1000)

        self.rotate_image(dt) # -> Rotamos imagen

        # Eliminamos sprite si su tiempo de vida pasó o colisiona
        if self.time_to_live <= 0 or self.check_collisions():
            self.kill()
            self.impact_sound.play()
            print("Bellota eliminada!!!")
        else:
            # Movemos sprite
            self.rect.center += self.direction * ACORN_SPEED * dt

    def rotate_image(self, delta_time): # -> Rotar imagen del projectil
        self.angle += self.rotation_speed * delta_time
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_frect(center = self.rect.center)
    
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
    
# ? Sprite de enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos, player, collision_sprites, water_sprites, plant_spots, acorn_group, difficulty = "normal"):
        super().__init__(groups)
        self.player = player # -> Jugador

        # ? Lógica de evasión
        self.is_evading = False
        self.evade_timer = 0
        self.evade_duration = 500

        # ? Lógica de daño
        self.can_damage = True
        self.damage_cooldown = 2000 # -> 1500 segundos
        self.damage_timer = 0
        self.base_damage = 5 if difficulty == "normal" else 10

        # ? Creamos un grupo de sprites de colisión
        self.collision_sprites = collision_sprites
        self.water_sprites = water_sprites
        self.plant_spots = plant_spots
        self.all_solid_sprites = list(self.collision_sprites) + list(self.plant_spots) # -> El Solid
        # + list(self.water_sprites)
        self.acorn_group = acorn_group # -> Grupo de las bellotas

        # ? Imagenes y rect inicial
        wd = os.getcwd() # -> Directorio

        tornado_frames = [x for x in range(1, 5)]
        img_path_1 = [os.path.join(wd, "assets", "images", "enemies", "tornado", f"{tornado}.png") for tornado in tornado_frames]

        smog_frames = [x for x in range(1, 4)]
        img_path_2 = [os.path.join(wd, "assets", "images", "enemies", "smog", f"{smog}.png") for smog in smog_frames]

        num = random.randint(1, 2)
        images_path = img_path_1 if num == 1 else img_path_2

        self.tornado_frames = [pygame.image.load(image).convert_alpha() for image in images_path]

        # ? Sonidos de enemigo (smog / tornado)
        self.sizzle_sound = pygame.mixer.Sound(os.path.join(wd, "assets", "sound", "sizzle.mp3"))
        self.swoosh_sound = pygame.mixer.Sound(os.path.join(wd, "assets", "sound", "swoosh.mp3"))

        # Vida
        self.health = 3

        # ? Imagen y frame
        self.frame = 1
        self.image = self.tornado_frames[self.frame]

        self.rect = self.image.get_frect(center = pos) # -> Posición inicial
        self.hitbox_rect = self.rect.inflate(-14, -10) # Hitbox rect -> Donde se checarán colisiones

        self.animation_speed = random.randint(14, 16) # -> Velocidad de animación
        self.speed = random.randint(80, 96) if difficulty == "normal" else random.randint(86, 102) # -> Velocidad del enemigo
        self.direction_vec = pygame.Vector2() # -> Vector de movimiento

    # ? Actualizar sprite
    def update(self, delta_time, events = None,):
        # ? Restamos el tiempo para evadir
        if self.evade_timer > 0:
            self.evade_timer -= delta_time * 1000
            if self.evade_timer <= 0:
                self.is_evading = False

        self.check_acorn_collisions() # -> Colisiones con bellotas
        self.check_player_collision(delta_time) # -> Colisiones con jugador
        self.animate(delta_time) # -> Animar tornado
        self.move(delta_time) # -> Movemos enemigo

    # ? Movimiento del enemigo
    def move(self, delta_time):
        player_position = pygame.Vector2(self.player.rect.center)
        enemy_position = pygame.Vector2(self.rect.center)
        direction_vector = (player_position - enemy_position) # -> Definimos dirección del enemigo

        self.direction_vec = direction_vector.normalize() if direction_vector.length() > 0 else direction_vector

        # -> Si esta evadiendo colisión
        if self.is_evading:
            self.direction_vec = self.direction_vec.rotate(random.choice([90, -90])) # -> Cambiamos dirección del vector
            self.is_evading = False

        # ? Mover hitbox rect del enemigo
        self.hitbox_rect.centerx += self.direction_vec.x * self.speed * delta_time
        self.check_collisions("horizontal")
        self.hitbox_rect.centery += self.direction_vec.y * self.speed * delta_time
        self.check_collisions("vertical")

        self.rect.center = self.hitbox_rect.center # -> Definir el rectangulo final

    def animate(self, delta_time): # -> Animación del tornado
        self.frame += self.animation_speed * delta_time
        self.image = self.tornado_frames[int(self.frame) % len(self.tornado_frames)]

    def check_collisions(self, direction):
        for sprite in self.all_solid_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):

                # ? Activamos evasión
                self.is_evading = True
                self.evade_timer = self.evade_duration
                
                # ? Colisión horizontal
                if direction == "horizontal":
                    if self.direction_vec.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction_vec.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                # ? Colisión vertical
                else:
                    if self.direction_vec.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction_vec.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def check_acorn_collisions(self):
        hit_acorn = pygame.sprite.spritecollide(self, self.acorn_group, True)

        if hit_acorn: # -> Si una bellota golpea
            for acorn in hit_acorn:
                self.sizzle_sound.play()
                self.health -= 1 # -> Bajamos vida

                if self.health <= 0:
                    self.swoosh_sound.play()
                    self.kill() # -> Matamos al sprite
                    return
                
    def check_player_collision(self, delta_time):

        # ? Actualizar el cooldown de daño
        if not self.can_damage:
            self.damage_timer -= delta_time * 1000
            if self.damage_timer <= 0:
                self.can_damage = True # -> Puede hacer daño
                self.damage_timer = 0

        if self.hitbox_rect.colliderect(self.player.hitbox_rect) and self.can_damage:
            self.player.health -= self.base_damage
            self.player.hit_sound.play()
            self.can_damage = False # -> No puede hacer daño y reiniciamos lógica de cooldown
            self.damage_timer = self.damage_cooldown

class Ghost(pygame.sprite.Sprite):
    def __init__(self, groups, position, player, difficulty = "normal"):
        super().__init__(groups) # -> Grupos
        self.wd = os.getcwd() # -> Directorio de trabajo
        
        self.frames = [pygame.image.load(os.path.join("assets", "images", "enemies", "ghost", f"{i}.png")).convert_alpha() for i in range(1, 4)]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        
        self.rect = self.image.get_frect(center = position)
        self.hitbox_rect = self.rect.inflate(-14, -10) # ? -> Rect de Hitbox (Colisiones)

        # ? Enemy Attributes
        self.speed = random.randint(55, 62)
        self.animation_speed = random.randint(8, 12)
        
        # * Lógica de daño
        self.can_damage = True
        self.damage_cooldown = 2000 # -> 2000 segundos
        self.damage_timer = 0
        self.base_damage = 5 if difficulty == "normal" else 10

        self.player = player # -> Get Game Player
    
    # * Actualizar enemigo
    def update(self, delta_time, events = None):
        self.check_player_collision(delta_time)
        self.animate(delta_time)
        self.move(delta_time)

    # ? Mover Personaje
    def move(self, delta_time):
        player_position = pygame.Vector2(self.player.rect.center)
        enemy_position = pygame.Vector2(self.rect.center)
        direction = (player_position - enemy_position) # -> Dirección a la que se moverá el Ghost
        
        self.direction = direction.normalize() if direction.length() > 0 else direction

        # ? Mover Hitbox del Ghost
        self.hitbox_rect.centerx += self.direction.x * self.speed * delta_time
        self.hitbox_rect.centery += self.direction.y * self.speed * delta_time
        self.rect.center = self.hitbox_rect.center # -> Definir rectangulo final

    # ? Ghost animation
    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        self.image = self.frames[int(self.current_frame) % len(self.frames)]

    # ? Colisión con el jugador
    def check_player_collision(self, delta_time):
        # ? Actualizar el cooldown de daño
        if not self.can_damage:
            self.damage_timer -= delta_time * 1000
            if self.damage_timer <= 0:
                self.can_damage = True # -> Puede hacer daño
                self.damage_timer = 0

        if self.hitbox_rect.colliderect(self.player.hitbox_rect) and self.can_damage and self.player.can_be_damaged:
            self.player.health -= self.base_damage
            self.player.last_time_damaged = pygame.time.get_ticks()
            self.player.can_be_damaged = False
            self.player.ouch_sound.play()

            self.can_damage = False # -> No puede hacer daño y reiniciamos lógica de cooldown
            self.damage_timer = self.damage_cooldown