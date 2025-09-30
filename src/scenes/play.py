# -> Aquí se dibujará el juego
from settings import *

def draw_game(screen, events, game_instance=None, delta_time = 0):
    
    screen.fill("#32FF23")
    
    if game_instance:

        # ? Jugador
        player = game_instance.player
        # ? Actualizamos los sprites
        player.input(events)
        game_instance.all_sprites.update(delta_time, events)

        # player_rect = player.rect

        # # ? Camara
        # screen_rect = screen.get_rect()
        # offset_x = player_rect.centerx - screen_rect.width // 2
        # offset_y = player_rect.centery - screen_rect.height // 2

        # map_rect = bg.get_rect()
        # offset_x = max(0, min(offset_x, map_rect.width - screen_rect.width))
        # offset_y = max(0, min(offset_y, map_rect.height - screen_rect.height))

        # screen.blit(bg, (-offset_x, -offset_y))

        # for sprite in game_instance.all_sprites:
        #     screen.blit(sprite.image, sprite.rect.move(-offset_x, -offset_y))
    
        game_instance.all_sprites.draw(screen)

    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "LEVEL_SELECT"   
            
    return "PLAYING"

class HealthBar():
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))

health_bar = HealthBar(64, 64, 64*6, 32, 100)
health_bar.hp=50
