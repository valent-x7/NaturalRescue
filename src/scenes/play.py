# -> Aquí se dibujará el juego
from settings import *

bg = pygame.image.load("./img/bosque.png")

def draw_game(screen, events, game_instance=None, delta_time = 0):
    keys = pygame.key.get_pressed()
    if game_instance:
        game_instance.all_sprites.update(keys, delta_time)

        player = game_instance.player
        player_rect = player.rect
        screen_rect = screen.get_rect()
        offset_x = player_rect.centerx - screen_rect.width // 2
        offset_y = player_rect.centery - screen_rect.height // 2

        map_rect = bg.get_rect()
        offset_x = max(0, min(offset_x, map_rect.width - screen_rect.width))
        offset_y = max(0, min(offset_y, map_rect.height - screen_rect.height))

        screen.blit(bg, (-offset_x, -offset_y))

        for sprite in game_instance.all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-offset_x, -offset_y))
    
    # ? Recorremos los eventos
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return "LEVEL_SELECT"   
            
    return "PLAYING"