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
        self.projectiles = MONKEY_ACORNS
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
        elif self.seeds == 0:
            pass

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
    
    # Disparar platanos
    def shoot(self, groups, player, mouse_pos, camera_offset, zoom, banana_img, throw_sound, impact_sound):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.cooldown_shot and self.projectiles > 0:
            # ? Creamos bellota
            Acorn.launch(groups, player, mouse_pos, camera_offset, zoom, self.collision_sprites, banana_img, throw_sound, impact_sound)
            self.last_shot = current_time
            self.projectiles -= 1

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
        self.wd = os.getcwd()
        self.spritesheet = spritesheet
        self.w = TILE
        self.h = TILE
        self.lives = 3
        self.eggs = 0
        self.current_lives = 3
        
        # --- Atributos de Estado y Animación ---
        self.moving = False
        self.direction = 'down'
        self.frame = 1
        self.animation_speed = 8
        self.alive = True
        self.is_dying = False
        self.is_damaged = False
        self.damage_timer = 0
        self.dead_timer = 0
        self.angle = 0  # Para la rotación de muerte
        self.invulnerable = False
        self.can_win = False

        # --- Atributos de Física y Movimiento ---
        self.speed = 3.2 
        self.x_vel = 0
        self.y_vel = 0
        self.on_ground = False
        
        # --- Carga de Animaciones ---
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
        
        # --- Configuración de Imagen y Rectángulo ---
        self.original_image = self.down_animation[1] 
        self.image = self.original_image
        self.rect = self.image.get_frect(topleft=(x - self.w // 2, y - self.h // 2))
        self.hitbox_rect = self.rect.inflate(-14, -10)
        self.mask = pygame.mask.from_surface(self.image)
        self.jump_sfx = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "penguin_jump.mp3"))
        self.damage_sfx = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "waterdrop.mp3"))
        self.damage_sfx.set_volume(1)
        self.jump_sfx.set_volume(1)

    def animate(self, moving, delta_time):
        if self.is_dying:
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            return

        if moving: 
            self.frame += self.animation_speed * delta_time
            if self.direction == "down":
                self.image = self.down_animation[int(self.frame) % len(self.down_animation)]
            elif self.direction == "left":
                self.image = self.left_animation[int(self.frame) % len(self.left_animation)]
            elif self.direction == "right":
                self.image = self.right_animation[int(self.frame) % len(self.right_animation)]
        else:
            if self.direction == "down":
                self.image = self.down_animation[1]
            elif self.direction == "right":
                self.image = self.right_animation[1]
            elif self.direction == "left":
                self.image = self.left_animation[1]
        
        
        self.catch = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "pick.mp3"))
        self.catch.set_volume(1)

    def collect(self):
        self.catch.play()

    def damage(self):
        
        if not self.alive or self.is_dying or self.invulnerable:
            return
        
        self.damage_sfx.play()
        self.current_lives -= 1
        
        if self.current_lives <= 0:
            self.alive = False
            self.is_dying = True
            self.dead_timer = 1.0 
            self.y_vel = -12.0 # Salto de muerte
            self.x_vel = 0
            self.original_image = self.image
            return

        self.is_dying = True
        self.dead_timer = 1.0 
        self.y_vel = -12.0 # Salto de muerte
        self.x_vel = 0
        self.original_image = self.image
        self.is_damaged = True
        self.invulnerable = True
        self.damage_timer = 2.0
        self.y_vel = -8.0

        self.original_image = self.image

    def apply_gravity(self):
        self.y_vel += 0.53
        self.rect.y += self.y_vel

    def handle_horizontal_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.x_vel > 0: # Moviéndose a la derecha
                    self.rect.right = platform.rect.left
                    self.x_vel = 0
                elif self.x_vel < 0: # Moviéndose a la izquierda
                    self.rect.left = platform.rect.right
                    self.x_vel = 0

    def handle_vertical_collisions(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_vel > 0: # Cayendo
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0
                    self.on_ground = True
                elif self.y_vel < 0: # Saltando
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.moving = False
        self.x_vel = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_vel = -self.speed
            self.direction = 'left'
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_vel = self.speed
            self.direction = 'right'
            self.moving = True
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = 'up'
            self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = 'down'
            self.moving = True
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.jump_sfx.play()
            self.y_vel = -12
            self.on_ground = False

    def update(self, delta_time, platforms):
        if self.is_damaged and self.invulnerable:
            self.damage_timer -= delta_time
            
            # Efecto de parpadeo durante la invulnerabilidad
            if int(self.damage_timer * 10) % 2 == 0:  # Parpadeo cada 0.1 segundos
                self.image.set_alpha(128)  # Semi-transparente
            else:
                self.image.set_alpha(255)  # Normal
            
            # Fin de la invulnerabilidad
            if self.damage_timer <= 0:
                self.is_damaged = False
                self.invulnerable = False
                self.image.set_alpha(255)  # Restaurar opacidad normal
        
        # 2. LÓGICA DE MUERTE DEFINITIVA
        if self.is_dying:
            self.dead_timer -= delta_time
            self.y_vel += 0.55
            self.rect.y += self.y_vel
            self.rect.x += self.x_vel
            self.angle += 360 * delta_time
            self.animate(False, delta_time)
            self.mask = pygame.mask.from_surface(self.image)
            if self.dead_timer <= 0:
                self.is_dying = False
                self.kill()
            return

        if not self.alive:
            return

        # 3. LÓGICA DE JUEGO NORMAL
        self.handle_input()
        
        # Movimiento y colisión horizontal
        self.rect.x += self.x_vel
        self.handle_horizontal_collisions(platforms)
        
        # Movimiento y colisión vertical
        self.apply_gravity()
        self.handle_vertical_collisions(platforms)
        
        # Actualizaciones finales
        self.animate(self.moving, delta_time)
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox_rect.center = self.rect.center

    def reset(self, x, y):
        self.rect.topleft = (x - self.w // 2, y - self.h // 2)
        self.hitbox_rect.center = self.rect.center
        self.alive = True
        self.is_dying = False
        self.is_damaged = False
        self.invulnerable = False
        self.damage_timer = 0
        self.dead_timer = 0
        self.angle = 0
        self.x_vel = 0
        self.y_vel = 0
        self.on_ground = False
        self.image.set_alpha(255)  # Asegurar opacidad normal
        self.direction = 'down'
        self.image = self.down_animation[1]

class Scientist(pygame.sprite.Sprite):
    def __init__(self, spritesheet: Spritesheet, groups, position, collision_sprites, acid_sprites):
        super().__init__(groups)
        self.wd = os.getcwd()

        self.collision_sprites = collision_sprites
        self.acid_sprites = acid_sprites

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
        self.grunt_sound = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "grunt.mp3"))

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
        self.projectiles = 100
        self.animation_speed = 14
        self.ghosts = 0

        # -> Lógica de disparo
        self.last_shot = 0
        self.cooldown_shot = 500

    # ? Actualizar jugador
    def update(self, delta_time, events):
        self.moving = False
        self.check_damage()
        self.input(events)
        self.move(delta_time)
        self.check_acid_collision()
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

    def check_acid_collision(self):
        def hitbox_collide(sprite1, sprite2):
            return sprite1.hitbox_rect.colliderect(sprite2.hitbox_rect)

        hit_acid = pygame.sprite.spritecollide(self, self.acid_sprites, False, collided=hitbox_collide)
        if hit_acid and self.can_be_damaged:
            self.health -= 5
            self.can_be_damaged = False
            self.last_time_damaged = pygame.time.get_ticks()
            self.grunt_sound.play()
            hit_acid[0].acid_burn.play()

    # Disparar capsulas
    def shoot(self, groups, player, mouse_pos, camera_offset, zoom, capsule_img, dissolve_frames, throw_sound, impact_sound):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.cooldown_shot and self.projectiles > 0:
            # ? Creamos capsula
            PuriCapsule.launch(groups, player, mouse_pos, camera_offset, zoom, self.collision_sprites, capsule_img, dissolve_frames, throw_sound, impact_sound)
            self.last_shot = current_time
            self.projectiles -= 1

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

class DamageSprite_2(pygame.sprite.Sprite):
    def __init__(self, groups, pos, image):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)

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
                        if player.health <= 110:
                            player.health += 10
                        else:
                            player.health = 120
                        self.is_complete = True # -> Completado
                
                else: # -> Si no hay agua para regar
                    self.error_sound.play()

            # ? Cambiamos imagen si o si
            self.image = self.get_image_by_water()

# ? Valvula
class Valve(pygame.sprite.Sprite):
    def __init__(self, groups, position, frames, close_sound):
        super().__init__(groups)
        self.wd = os.getcwd() # -> Get working direction

        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_frect(topleft = (position))
        self.hitbox_rect = self.rect.inflate(-5, -20)

        # ? Sonido
        self.close_sound = close_sound

        # ? Atributes
        self.animation_speed = 10
        self.is_leaking = True # -> Tiene fuga activada

    def update(self, player, delta_time):
        keystate = pygame.key.get_pressed()

        if self.check_player_collision(player) and keystate[pygame.K_h] and self.is_leaking:
            player.valves += 1
            self.is_leaking = False
            self.close_sound.play()

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
    def __init__(self, groups, pos, direction, collision_sprites, image, throw_sound, impact_sound):
        super().__init__(groups)

        # ? Imagen y gráficos
        self.original_image = image
        self.image = self.original_image

        # ? Audio del platano
        self.throw_sound = throw_sound
        self.impact_sound = impact_sound

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
    def launch(cls, groups, player, mouse_pos, camera_offset, zoom, collision_sprites, image, throw_sound, impact_sound):
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
        return cls(groups, player_pos, direction, collision_sprites, image, throw_sound, impact_sound)
    
class PuriCapsule(pygame.sprite.Sprite):
    def __init__(self, groups, pos, direction, collision_sprites, original_img, dissolve_frames, throw_sound, impact_sound):
        super().__init__(groups)

        # ? Imagen y gráficos
        self.original_image = original_img
        self.image = self.original_image

        self.dissolve_frames = dissolve_frames
        self.current_disolve_frame = 0

        # ? Audio
        self.throw_sound = throw_sound
        self.impact_sound = impact_sound

        # Rectangulo y HitBox
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-15, -5)

        # ? Dirección de la capsula
        if direction.length_squared() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2(0, 0)

        # ? Attributes
        self.is_dissolving = False
        self.animation_speed = 12
        self.time_to_live = 1000 # -> Tiempo de vida
        self.collision_sprites = collision_sprites
        self.angle = 0 
        self.rotation_speed = 360 # -> Velocidad de rotación

        self.throw_sound.play()

    def update(self, dt, events = None):
        if self.is_dissolving:
            self.dissolve(dt)
            return

        # Descontamos tiempo de vida
        self.time_to_live -= (dt * 1000)
        self.rotate_image(dt) # -> Rotamos imagen

        # Eliminamos sprite si su tiempo de vida pasó o colisiona
        if self.time_to_live <= 0 or self.check_collisions():
            self.impact_sound.play()
            self.is_dissolving = True
            self.current_disolve_frame = 0
            return
        
        # Movemos sprite
        self.rect.center += self.direction * ACORN_SPEED * dt
        self.hitbox_rect.center = self.rect.center

    def rotate_image(self, delta_time): # -> Rotar imagen del projectil
        self.angle += self.rotation_speed * delta_time
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_frect(center = self.rect.center)
        self.hitbox_rect.center = self.rect.center

    # ? Si choca con un sprite de collision
    def check_collisions(self):
        return pygame.sprite.spritecollideany(self, self.collision_sprites)
    
    def dissolve(self, delta_time):
        self.current_disolve_frame += self.animation_speed * delta_time

        if int(self.current_disolve_frame) < len(self.dissolve_frames):
            self.image = self.dissolve_frames[int(self.current_disolve_frame) % len(self.dissolve_frames)]
        else:
            self.kill() # -> Matar sprite después de animar

    @classmethod # * Crear PuriCapsule
    def launch(cls, groups, player, mouse_pos, camera_offset, zoom, collision_sprites, capsule_img, dissolve_frames, throw_sound, impact_sound):
        player_pos = pygame.Vector2(player.rect.center) # -> Posición del jugador

        # ? La posición real del mouse cuidando el zoom!!
        mouse_x = (mouse_pos[0] / zoom) + camera_offset.x
        mouse_y = (mouse_pos[1] / zoom) + camera_offset.y

        target_pos = pygame.Vector2(mouse_x, mouse_y) # -> Dirección objetivo
        direction = target_pos - player_pos # -> Dirección

        # ? Creamos puricapsula (Grupo, posicion jugador, dirección, sprites de colisión)
        return cls(groups, player_pos, direction, collision_sprites, capsule_img, dissolve_frames, throw_sound, impact_sound)

# ? Sprite de enemigos (tornados)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos, player, collision_sprites, water_sprites, plant_spots, acorn_group, tornado_frames, smog_frames, sizzle, swoosh, difficulty = "normal"):
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
        num = random.randint(1, 2)
        self.frames = tornado_frames if num == 1 else smog_frames

        # ? Sonidos de enemigo (smog / tornado)
        self.sizzle_sound = sizzle
        self.swoosh_sound = swoosh

        # Vida
        self.health = 3

        # ? Imagen y frame
        self.frame = 1
        self.image = self.frames[self.frame]

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
        self.image = self.frames[int(self.frame) % len(self.frames)]

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

class WaterEnemy(pygame.sprite.Sprite):
    def __init__(self, position, player, difficulty="normal"):
        super().__init__()
        self.wd = os.getcwd()

        self.frames = [pygame.image.load(os.path.join("assets", "images", "water", f"{i}.png")).convert_alpha() for i in range(1, 4)]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        self.rect = self.image.get_rect(topleft=position)

        self.y_float = float(self.rect.y)

        # Guardar posición inicial para el reset
        self.initial_position = position

        if difficulty == "normal":
            self.speed = 20.0
        else:
            self.speed = 35.0
            
        self.animation_speed = 4
        self.player = player

        self.mask = pygame.mask.from_surface(self.image)
        
        self.last_debug_time = 0
        self.water_vol = 0.5
        self.water_sfx = pygame.mixer.Sound(os.path.join(self.wd, "assets", "sound", "waterloop.wav"))
        self.water_sfx.set_volume(self.water_vol)
        self.water_sfx.play(loops=1)

    def update(self, delta_time, events=None):
        movement = self.speed * delta_time
        self.y_float -= movement
        self.rect.y = int(self.y_float)

        self.animate(delta_time)
        self.mask = pygame.mask.from_surface(self.image)

    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        
        new_frame_index = int(self.current_frame) % len(self.frames)
        new_image = self.frames[new_frame_index]
        
        if new_image is not self.image:
            self.image = new_image
        
    def reset(self):
        self.rect.topleft = self.initial_position
        self.y_float = float(self.rect.y)

class Helicopter(pygame.sprite.Sprite):
    def __init__(self, position, player):
        super().__init__()
        self.wd = os.getcwd()
        self.frames = [pygame.image.load(os.path.join("assets", "images", "helicopter", f"{i}.png")).convert_alpha() for i in range(0, 4)]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        self.rect = self.image.get_rect(topleft=position)
        self.animation_speed = 10
        self.player = player

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time, events=None):
        self.animate(delta_time)
        self.mask = pygame.mask.from_surface(self.image)

    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        
        new_frame_index = int(self.current_frame) % len(self.frames)
        new_image = self.frames[new_frame_index]
        
        if new_image is not self.image:
            self.image = new_image

class Ghost(pygame.sprite.Sprite):
    def __init__(self, groups, position, player, capsules_group, frames, dissolve_frames, impact_sound, difficulty = "normal"):
        super().__init__(groups) # -> Grupos
        
        self.frames = frames
        self.current_frame = 0
        self.dissolve_frames = dissolve_frames
        self.current_dissolve_frame = 0

        self.image = self.frames[self.current_frame]
        
        self.rect = self.image.get_frect(center = position)
        self.hitbox_rect = self.rect.inflate(-14, -10) # ? -> Rect de Hitbox (Colisiones)

        self.capsules_group = capsules_group

        # ? Sonido
        self.impact_sound = impact_sound

        # ? Enemy Attributes
        self.speed = random.randint(55, 62) if difficulty == "normal" else random.randint(62, 76)
        self.animation_speed = random.randint(8, 12)
        self.health = 3
        self.is_dissolving = False
        
        # * Lógica de daño
        self.can_be_damaged = True
        self.capsule_damage_cooldown = 300
        self.last_time_damage = 0
        self.can_damage = True
        self.damage_cooldown = 2000 # -> 2000 segundos
        self.damage_timer = 0
        self.base_damage = 5 if difficulty == "normal" else 10

        self.player = player # -> Get Game Player
    
    # * Actualizar enemigo
    def update(self, delta_time, events = None):
        now = pygame.time.get_ticks()
        if now - self.last_time_damage >= self.capsule_damage_cooldown:
            self.can_be_damaged = True

        if self.is_dissolving:
            self.dissolve_ghost(delta_time)
        else:
            self.check_capsule_collision()
            self.check_player_collision(delta_time)
            self.animate(delta_time)
            self.move(delta_time)
    
    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        self.image = self.frames[int(self.current_frame) % len(self.frames)]

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

    def check_capsule_collision(self):
        now = pygame.time.get_ticks()
        hit_capsules = pygame.sprite.spritecollide(self, self.capsules_group, False)

        if not hit_capsules:
            return # No hay colisiones

        a_new_hit_occured = False

        for capsule in hit_capsules:
            if not capsule.is_dissolving:
                capsule.is_dissolving = True # -> Disolver capsula
                a_new_hit_occured = True
                
                if self.can_be_damaged:
                    self.impact_sound.play()
                    self.health -= 1

                    if self.health <= 0 and not self.is_dissolving:
                        self.is_dissolving = True
                        self.current_dissolve_frame = 0
                        return 
                    
        if a_new_hit_occured and self.can_be_damaged:
            self.last_time_damage = now
            self.can_be_damaged = False
                
    def dissolve_ghost(self, delta_time):
        self.current_dissolve_frame += self.animation_speed * delta_time

        if int(self.current_dissolve_frame) < len(self.dissolve_frames):
            self.image = self.dissolve_frames[int(self.current_dissolve_frame)]
        else:
            self.kill() # -> Matar sprite
            self.player.health = min(self.player.health + 1, SCIENTIST_HEALTH)
            self.player.ghosts += 1
            return
        
class Acid(pygame.sprite.Sprite):
    def __init__(self, groups, position, frames, burn_sound):
        super().__init__(groups)

        self.acid_frames = frames
        self.current_frame = 0
        self.image = self.acid_frames[self.current_frame]

        # ? Sonido
        self.acid_burn = burn_sound
        
        self.rect = self.image.get_frect(topleft = (position))
        self.hitbox_rect = self.rect.inflate(-20, -45)

        # ? Attributes
        self.animation_speed = random.randint(6, 8)

    def update(self, delta_time, events = None):
        self.animate(delta_time)

    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        self.image = self.acid_frames[int(self.current_frame) % len(self.acid_frames)]

class LabDoor(pygame.sprite.Sprite):
    def __init__(self, groups, position, frames, metalic_door_sound):
        super().__init__(groups)

        self.door_frames = frames
        self.current_frame = 0

        self.image = self.door_frames[self.current_frame]

        self.rect = self.image.get_frect(topleft = (position))

        # ? Sonido
        self.metalic_door = metalic_door_sound

        # ? Attributes
        self.required_ghosts = 0
        self.is_open = False
        self.animation_speed = 4

    def update(self, delta_time, events = None):
        pass

    def open(self, delta_time):
        if not self.is_open:
            self.is_open = True
            self.metalic_door.play()

        self.current_frame += self.animation_speed * delta_time
        if int(self.current_frame) < len(self.door_frames):
            self.image = self.door_frames[int(self.current_frame) % len(self.door_frames)]
        else:
            self.kill()

class Egg(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        self.wd = os.getcwd() 
        self.egg_frames = [pygame.image.load(os.path.join(self.wd, "assets", "images", "egg", f"{i}.png")).convert_alpha() for i in range(1, 6)]
        self.current_frame = 0
        self.image = self.egg_frames[self.current_frame]
        
        self.rect = self.image.get_frect(topleft = position)
        self.hitbox_rect = self.rect.inflate(-20, -45)

        self.animation_speed = random.randint(6, 8)

    def update(self, delta_time, *args):
        self.animate(delta_time)

    def animate(self, delta_time):
        self.current_frame += self.animation_speed * delta_time
        self.image = self.egg_frames[int(self.current_frame) % len(self.egg_frames)]

class Pickup(pygame.sprite.Sprite):
    def __init__(self, groups, player, type, frames, pos, coords, sound):
        super().__init__(groups)
        if pos in coords:
            coords.remove(pos) # -> Quitar posición

        self.coords = coords # -> Coords
        self.pos = pos # -> Posición
        self.player = player # -> Jugador
        self.type = type # -> Tipo de PickUp

        self.frames = frames
        self.frame = 0
        self.image = self.frames[self.frame]
        self.rect = self.image.get_frect(topleft = (self.pos))
        self.hitbox_rect = self.rect.inflate(-20, -45)

        self.speed_animation = 4
        self.creation_time = pygame.time.get_ticks() # -> Tiempo de creación
        self.lifetime = 20000 # -> 20 segundos
        self.sound = sound

    def update(self, delta_time, *args):
        self.animate(delta_time)
        self.check_player_collision()
        self.check_time()

    def animate(self, delta_time):
        self.frame += self.speed_animation * delta_time
        self.image = self.frames[int(self.frame) % len(self.frames)]

    def check_player_collision(self):
        if self.hitbox_rect.colliderect(self.player.hitbox_rect):
            if self.type == "Life":
                self.player.health = min(self.player.health + 10, SCIENTIST_HEALTH)
            else:
                self.player.projectiles += 12
            self.sound.play()
            self.despawn()
            return
        
    def check_time(self):
        now = pygame.time.get_ticks()

        if now - self.creation_time >= self.lifetime:
            self.despawn()
            return
        
    def despawn(self):
        if self.pos not in self.coords:
            self.coords.append(self.pos)
        self.kill()