import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin

import pygame
from settings import *
from ui.utils import draw_text, get_text
from math import sin


def _draw_blinking_hint(screen, translations, current_lang):
    # Dibuja el mensaje parpadeante de 'Presiona Enter'
    hint = get_text(translations, current_lang, "press-enter")
    t = pygame.time.get_ticks() / 500
    alpha = sin(t) * 0.5 + 0.5
    color_blink = [int(150 + alpha * 100)] * 3
    draw_text(
        screen,
        TITLE_FONT_PATH,
        30,
        hint,
        color_blink,
        WINDOW_WIDTH / 2,
        WINDOW_HEIGHT - 60,
    )


# Maneja los eventos de teclado para continuar o salir.
def _handle_tutorial_events(game, events, next_scene_on_enter, scene_on_m):
    for e in events:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                # Marcar el tutorial específico como completado
                if next_scene_on_enter == "LEVEL_1":
                    game.tutorial_1_done = True
                elif next_scene_on_enter == "LEVEL_2":
                    game.tutorial_2_done = True
                elif next_scene_on_enter == "LEVEL_3":
                    game.tutorial_3_done = True

                return next_scene_on_enter
            elif e.key == pygame.K_m:
                return scene_on_m
    return None


class Tutorial_levelone:
    # Tutorial Nivel 1: Movimiento y Acción Principal (Chango, Plantar).

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.scene_name = "TUTORIAL_1"
        self.next_scene_on_enter = "LEVEL_1"
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):
        # Fondo y Título
        bg = pygame.image.load("assets/images/tutorial/background_forest.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))
        title = get_text(self.translations, current_lang, "tutorial-title")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # TAMAÑOS REDUCIDOS
        IMG_SIZE = (100, 100)
        ARROW_SIZE = (100, 100) 

        # Movimiento Básico (WASD con Chango y Flechas)
        actions = ["W", "A", "S", "D"]
        start_y_move = 200 
        gap_x = 200
        base_x = WINDOW_WIDTH // 2 - (len(actions) - 1) * gap_x // 2

        for i, key in enumerate(actions):
            x = base_x + i * gap_x

            # Tecla (W, A, S, D)
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, start_y_move)))

            # Chango
            monkey_img = pygame.transform.scale(
                self.tutorial_assets["monkey"][key], IMG_SIZE
            )
            screen.blit(
                monkey_img, monkey_img.get_rect(center=(x, start_y_move + 120))
            )  

            # Flecha
            arrow_img = pygame.transform.scale(
                self.tutorial_assets["arrows"][key], ARROW_SIZE
            )
            screen.blit(
                arrow_img, arrow_img.get_rect(center=(x, start_y_move + 240))
            )  

        #  Acción Principal: Plantar

        # Subtítulo
        action_title_y = start_y_move + 350  #
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            get_text(self.translations, current_lang, "tutorial-extra-actions"),
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            action_title_y,
        )

        plant_y = action_title_y + 100

        # Cargar y escalar imágenes para la "fórmula"
        img_key_h = pygame.transform.scale(self.tutorial_assets["keys"]["H"], IMG_SIZE)
        img_brote = pygame.transform.scale(
            self.tutorial_assets["extras"]["H_brote"], (150, 100)
        )  # <--- CAMBIO: Tamaño reducido
        img_hoyo = pygame.transform.scale(
            self.tutorial_assets["extras"]["T1_hoyo"], IMG_SIZE
        )

        x_h = WINDOW_WIDTH // 2 - 250
        x_brote = WINDOW_WIDTH // 2
        x_hoyo = WINDOW_WIDTH // 2 + 250

        screen.blit(img_key_h, img_key_h.get_rect(center=(x_h, plant_y)))
        screen.blit(img_brote, img_brote.get_rect(center=(x_brote, plant_y)))
        screen.blit(img_hoyo, img_hoyo.get_rect(center=(x_hoyo, plant_y)))

        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "+",
            "#FFFFFF",
            WINDOW_WIDTH // 2 - 125,
            plant_y,
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2 + 125,
            plant_y,
        )

        # Texto descriptivo
        instruction_text = get_text(
            self.translations, current_lang, "tutorial-plant-instruction"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            instruction_text,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            plant_y + 90,
        ) 

        # Acción: Ataque

        attack_y = plant_y + 150  # 

        # Subtítulo de Ataque
        attack_title = get_text(self.translations, current_lang, "tutorial-attack")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            attack_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            attack_y,
        )

        attack_img_y = attack_y + 100  

        # Cargar y escalar imágenes
        img_click = pygame.transform.scale(
            self.tutorial_assets["keys"]["CLICK_LEFT"], IMG_SIZE
        )
        img_banana = pygame.transform.scale(
            self.tutorial_assets["extras"]["T1_banana"], IMG_SIZE
        )

        x_click = WINDOW_WIDTH // 2 - 100
        x_banana = WINDOW_WIDTH // 2 + 100

        screen.blit(img_click, img_click.get_rect(center=(x_click, attack_img_y)))
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            attack_img_y,
        )
        screen.blit(img_banana, img_banana.get_rect(center=(x_banana, attack_img_y)))

        # Texto descriptivo
        attack_instr_text = get_text(
            self.translations, current_lang, "tutorial-attack-instr"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            attack_instr_text,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            attack_img_y + 80,
        )  

        # Mensaje parpadeante
        #
        _draw_blinking_hint(screen, self.translations, current_lang)

        # Manejo de Eventos
        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )
        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass


class Tutorial_leveltwo:
    # Tutorial Nivel 2: Plataformero (Pingüino).

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.scene_name = "TUTORIAL_2"
        self.next_scene_on_enter = "LEVEL_2"
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):

        # Fondo y Título
        bg = pygame.image.load("assets/images/tutorial/background_ice.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))
        title = get_text(self.translations, current_lang, "tutorial-title-2")

        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)
        # TAMAÑOS
        IMG_SIZE = (90, 90)  
        ARROW_SIZE = (90, 90) 

        # Movimiento (A/D)
        move_y = 170 
        move_title = get_text(self.translations, current_lang, "tutorial-move-2")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            move_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            move_y,
        )

        # Imágenes
        key_a = pygame.transform.scale(self.tutorial_assets["keys"]["A"], IMG_SIZE)
        penguin_a = pygame.transform.scale(
            self.tutorial_assets["penguin"]["A"], IMG_SIZE
        )
        arrow_left_img = pygame.transform.scale(
            self.tutorial_assets["arrows"]["A"], ARROW_SIZE
        )
        key_d = pygame.transform.scale(self.tutorial_assets["keys"]["D"], IMG_SIZE)
        penguin_d = pygame.transform.scale(
            self.tutorial_assets["penguin"]["D"], IMG_SIZE
        )
        arrow_right_img = pygame.transform.scale(
            self.tutorial_assets["arrows"]["D"], ARROW_SIZE
        )

        # Posiciones
        gap_x = 200
        x_a = WINDOW_WIDTH // 2 - gap_x // 2
        x_d = WINDOW_WIDTH // 2 + gap_x // 2
        img_y_row1 = move_y + 80  

        # Dibujar 'A' (Tecla + Flecha + Pingüino)
        screen.blit(key_a, key_a.get_rect(center=(x_a, img_y_row1)))
        screen.blit(
            arrow_left_img, arrow_left_img.get_rect(center=(x_a, img_y_row1 + 60))
        )
        screen.blit(penguin_a, penguin_a.get_rect(center=(x_a, img_y_row1 + 120)))

        # Dibujar 'D' (Tecla + Flecha + Pingüino)
        screen.blit(key_d, key_d.get_rect(center=(x_d, img_y_row1)))
        screen.blit(
            arrow_right_img, arrow_right_img.get_rect(center=(x_d, img_y_row1 + 60))
        )
        screen.blit(penguin_d, penguin_d.get_rect(center=(x_d, img_y_row1 + 120)))

        # Texto de instrucción
        move_instr = get_text(self.translations, current_lang, "tutorial-move-instr-2")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            move_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            img_y_row1 + 200,
        )

        # Salto (W/Space)
        jump_y = 520 
        jump_title = get_text(self.translations, current_lang, "tutorial-jump")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            jump_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            jump_y,
        )

        # Imágenes
        key_w = pygame.transform.scale(self.tutorial_assets["keys"]["W"], IMG_SIZE)
        key_space = pygame.transform.scale(
            self.tutorial_assets["keys"]["SPACE"], (250, 250)
        )  

        penguin_jump = pygame.transform.scale(
            self.tutorial_assets["penguin"]["JUMP"], IMG_SIZE
        )

        # Posiciones
        x_w = WINDOW_WIDTH // 2 - 400
        x_space = WINDOW_WIDTH // 2 - 70
        x_jump = WINDOW_WIDTH // 2 + 250
        img_y_jump = jump_y + 110

        # Dibujar
        screen.blit(key_w, key_w.get_rect(center=(x_w, img_y_jump)))
        screen.blit(key_space, key_space.get_rect(center=(x_space, img_y_jump)))
        screen.blit(penguin_jump, penguin_jump.get_rect(center=(x_jump, img_y_jump)))
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "O",
            "#FFFFFF",
            WINDOW_WIDTH // 2 - 250,
            img_y_jump,
        )

        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2 + 125,
            img_y_jump,
        )

        # Texto de instrucción
        jump_instr = get_text(self.translations, current_lang, "tutorial-jump-instr")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            jump_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            jump_y + 200,
        )

        # Objetivo (Recolectar)
        collect_y = 780  
        collect_title = get_text(self.translations, current_lang, "tutorial-objective")

        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            collect_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            collect_y,
        )

        # Imágenes
        penguin_walk = pygame.transform.scale(
            self.tutorial_assets["penguin"]["D"], IMG_SIZE
        )  

        egg_img = pygame.transform.scale(
            self.tutorial_assets["extras"]["T2_huevo"], IMG_SIZE
        )

        # Posiciones
        x_penguin = WINDOW_WIDTH // 2 - 100
        x_egg = WINDOW_WIDTH // 2 + 100
        img_y_collect = collect_y + 100

        # Dibujar
        screen.blit(
            penguin_walk, penguin_walk.get_rect(center=(x_penguin, img_y_collect))
        )
        screen.blit(egg_img, egg_img.get_rect(center=(x_egg, img_y_collect)))
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            img_y_collect,
        )

        # Texto de instrucción
        collect_instr = get_text(
            self.translations, current_lang, "tutorial-collect-instr-2"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            collect_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            collect_y + 200,
        )

        # Mensaje parpadeante y Manejo de Eventos

        _draw_blinking_hint(screen, self.translations, current_lang)

        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )

        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass


class Tutorial_levelthree:
    """Tutorial Nivel 3: Top-Down (Científico)."""

    def __init__(self, translations, lang, tutorial_assets):
        self.translations = translations
        self.lang = lang
        self.tutorial_assets = tutorial_assets
        self.scene_name = "TUTORIAL_3"
        self.next_scene_on_enter = "LEVEL_3"
        self.scene_on_m = "LEVEL_SELECT"

    def draw(self, game, screen, events, current_lang):
        # --- 1. Fondo y Título ---
        bg = pygame.image.load("assets/images/tutorial/background_lab.png").convert()
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(bg, (0, 0))
        title = get_text(self.translations, current_lang, "tutorial-title-3")
        draw_text(screen, TITLE_FONT_PATH, 52, title, "#FFFFFF", WINDOW_WIDTH // 2, 80)

        # --- TAMAÑOS ---
        IMG_SIZE = (90, 90)  # Tamaño reducido para que quepa todo

        # --- 2. Movimiento (WASD + Científico + Flechas) ---
        move_y = 170  # Posición Y fija
        move_title = get_text(
            self.translations, current_lang, "tutorial-move-2"
        )  # Reusa "MOVIMIENTO"
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            move_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            move_y,
        )

        actions = ["W", "A", "S", "D"]
        gap_x = 200
        base_x = WINDOW_WIDTH // 2 - (len(actions) - 1) * gap_x // 2

        # Posiciones de las filas
        y_keys = move_y + 80
        y_scientist = move_y + 170
        y_arrows = move_y + 260

        for i, key in enumerate(actions):
            x = base_x + i * gap_x
            # Fila 1: Teclas
            key_img = pygame.transform.scale(
                self.tutorial_assets["keys"][key], IMG_SIZE
            )
            screen.blit(key_img, key_img.get_rect(center=(x, y_keys)))
            # Fila 2: Científico
            scientist_img = pygame.transform.scale(
                self.tutorial_assets["scientist"][key], IMG_SIZE
            )
            screen.blit(scientist_img, scientist_img.get_rect(center=(x, y_scientist)))
            # Fila 3: Flechas
            arrow_img = pygame.transform.scale(
                self.tutorial_assets["arrows"][key], IMG_SIZE
            )
            screen.blit(arrow_img, arrow_img.get_rect(center=(x, y_arrows)))

        # Texto de instrucción
        move_instr = get_text(self.translations, current_lang, "tutorial-move-instr-3")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            move_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            y_arrows + 80,
        )  # Debajo de las flechas

        # --- 3. Acción: Purificar ---
        action_y = 550  # Posición Y fija
        action_title = get_text(self.translations, current_lang, "tutorial-action-3")
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            action_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            action_y,
        )

        # Imágenes
        img_click = pygame.transform.scale(
            self.tutorial_assets["keys"]["CLICK_LEFT"], IMG_SIZE
        )
        img_pill = pygame.transform.scale(
            self.tutorial_assets["extras"]["T3_pill"], IMG_SIZE
        )
        img_ghost = pygame.transform.scale(
            self.tutorial_assets["extras"]["T3_ghost"], (110, 110)
        )  # Fantasma un poco más grande

        # Posiciones
        x_click = WINDOW_WIDTH // 2 - 200
        x_pill = WINDOW_WIDTH // 2
        x_ghost = WINDOW_WIDTH // 2 + 200
        img_y_action = action_y + 90

        # Dibujar
        screen.blit(img_click, img_click.get_rect(center=(x_click, img_y_action)))
        screen.blit(img_pill, img_pill.get_rect(center=(x_pill, img_y_action)))
        screen.blit(img_ghost, img_ghost.get_rect(center=(x_ghost, img_y_action)))

        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2 - 100,
            img_y_action,
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2 + 100,
            img_y_action,
        )

        # Texto de instrucción
        action_instr = get_text(
            self.translations, current_lang, "tutorial-action-instr-3"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            action_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            action_y + 180,
        )

        # --- 4. Objetivo: Válvulas ---
        objective_y = 780  # Posición Y fija
        objective_title = get_text(
            self.translations, current_lang, "tutorial-objective"
        )  # Reusa "OBJETIVO"
        draw_text(
            screen,
            TITLE_FONT_PATH,
            36,
            objective_title,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            objective_y,
        )

        # Imágenes
        # Reusamos el científico "hacia abajo" y la tecla H
        img_scientist = pygame.transform.scale(
            self.tutorial_assets["scientist"]["S"], IMG_SIZE
        )
        img_key_h = pygame.transform.scale(self.tutorial_assets["keys"]["H"], IMG_SIZE)
        img_valve = pygame.transform.scale(
            self.tutorial_assets["extras"]["T3_valve"], (110, 110)
        )

        # Posiciones
        x_scientist = WINDOW_WIDTH // 2 - 200
        x_key_h = WINDOW_WIDTH // 2
        x_valve = WINDOW_WIDTH // 2 + 200
        img_y_objective = objective_y + 90

        # Dibujar
        screen.blit(
            img_scientist, img_scientist.get_rect(center=(x_scientist, img_y_objective))
        )
        screen.blit(img_key_h, img_key_h.get_rect(center=(x_key_h, img_y_objective)))
        screen.blit(img_valve, img_valve.get_rect(center=(x_valve, img_y_objective)))

        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "+",
            "#FFFFFF",
            WINDOW_WIDTH // 2 - 100,
            img_y_objective,
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            40,
            "->",
            "#FFFFFF",
            WINDOW_WIDTH // 2 + 100,
            img_y_objective,
        )

        # Texto de instrucción
        objective_instr = get_text(
            self.translations, current_lang, "tutorial-objective-instr-3"
        )
        draw_text(
            screen,
            TITLE_FONT_PATH,
            24,
            objective_instr,
            "#FFFFFF",
            WINDOW_WIDTH // 2,
            objective_y + 180,
        )

        # --- 5. Pie de Página y Eventos ---
        _draw_blinking_hint(screen, self.translations, current_lang)
        next_scene = _handle_tutorial_events(
            game, events, self.next_scene_on_enter, self.scene_on_m
        )
        return next_scene if next_scene else self.scene_name

    def setup_assets(self):
        pass
