import pygame
import os
from settings import *
from ui.utils import draw_text, get_text, draw_text_space


class GameOver:
    def __init__(self, game, screen: pygame.Surface, level_id):
        self.game_screen = screen
        self.level_id = str(
            level_id
        )  # Aseguramos que sea string para los nombres de archivo
        self.wd = os.getcwd()

        self.translations = game.translations
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        self.font_path = TITLE_FONT_PATH

        # --- CARGA DE FONDO ESPECÍFICO ---
        # Construimos el nombre del archivo: fondolose1.png, fondolose2.png, etc.
        image_filename = f"fondolose{self.level_id}.png"
        image_path = os.path.join(
            self.wd, "assets", "images", "screens", image_filename
        )

        self.background = pygame.image.load(image_path).convert()
        self.background = pygame.transform.scale(
        self.background, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # Capa oscura semitransparente para que el texto se lea mejor sobre el dibujo
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))  # Negro con transparencia (0-255)

    def wrap_text(self, text, font, max_width):
        """Divide el texto en líneas que caben en el ancho máximo"""
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            # Probar si la palabra cabe en la línea actual
            test_line = " ".join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:  # Si ya hay palabras en la línea actual
                    lines.append(" ".join(current_line))
                current_line = [word]  # Comenzar nueva línea con esta palabra

        # Añadir la última línea
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def draw_multiline_text(
        self, surface, text, font, color, x, y, max_width, line_spacing=1.2
    ):
        """Dibuja texto multilínea centrado horizontalmente"""
        lines = self.wrap_text(text, font, max_width)
        line_height = font.get_linesize() * line_spacing

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(x, y + i * line_height))
            surface.blit(text_surface, text_rect)

        return len(lines) * line_height

    def run(self, game, events):
        self.window_width, self.window_height = self.game_screen.get_size()

        # --- DIBUJAR FONDO ---
        if self.background:
            self.game_screen.blit(self.background, (0, 0))
            self.game_screen.blit(
                self.overlay, (0, 0)
            )  # Oscurecer un poco para leer texto
        else:
            self.game_screen.fill("black")  # Fallback

        # Tamaños de fuente responsive basados en el tamaño de pantalla
        base_size = min(self.window_width, self.window_height)

        # Ajustar tamaños de fuente según el nivel
        if self.level_id == "3":
            title_size = int(base_size * 0.06)
        else:
            title_size = int(base_size * 0.07)

        subtitle_size = int(base_size * 0.04)
        menu_restart_size = int(base_size * 0.03)

        # Crear fuentes
        title_font = pygame.font.Font(self.font_path, title_size)
        subtitle_font = pygame.font.Font(self.font_path, subtitle_size)
        menu_font = pygame.font.Font(self.font_path, menu_restart_size)

        # Obtener textos
        title_text = get_text(
            self.translations, game.current_lang, f"gameover-title-{self.level_id}"
        )
        subtitle_text = get_text(
            self.translations, game.current_lang, f"gameover-subtitle-{self.level_id}"
        )
        menu_text = get_text(self.translations, game.current_lang, "press-m-to-menu")
        restart_text = get_text(
            self.translations, game.current_lang, "press-r-to-restart"
        )

        # Anchos máximos
        max_title_width = self.window_width * 0.9
        max_subtitle_width = self.window_width * 0.85

        # Calcular alturas
        title_lines = self.wrap_text(title_text, title_font, max_title_width)
        subtitle_lines = self.wrap_text(
            subtitle_text, subtitle_font, max_subtitle_width
        )

        title_height = len(title_lines) * title_font.get_linesize() * 1.3
        subtitle_height = len(subtitle_lines) * subtitle_font.get_linesize() * 1.3
        actions_height = menu_font.get_linesize() * 3

        # Espaciado
        spacing = self.window_height * 0.04

        # Altura total
        total_height = title_height + subtitle_height + actions_height + (spacing * 3)

        # Posición vertical inicial
        start_y = (self.window_height - total_height) / 2
        current_y = start_y

        # DIBUJAR TÍTULO (Color rojo para resaltar derrota)
        title_height_used = self.draw_multiline_text(
            self.game_screen,
            title_text,
            title_font,
            "#ff4444",
            self.window_width / 2,
            current_y,
            max_title_width,
            1.3,
        )
        current_y += title_height_used + spacing

        # DIBUJAR SUBTÍTULO
        subtitle_height_used = self.draw_multiline_text(
            self.game_screen,
            subtitle_text,
            subtitle_font,
            "white",
            self.window_width / 2,
            current_y,
            max_subtitle_width,
            1.3,
        )
        current_y += subtitle_height_used + spacing

        # DIBUJAR OPCIONES
        menu_surface = menu_font.render(menu_text, True, "#cccccc")
        menu_rect = menu_surface.get_rect(center=(self.window_width / 2, current_y))
        self.game_screen.blit(menu_surface, menu_rect)

        current_y += menu_font.get_linesize() * 1.5

        restart_surface = menu_font.render(restart_text, True, "#cccccc")
        restart_rect = restart_surface.get_rect(
            center=(self.window_width / 2, current_y)
        )
        self.game_screen.blit(restart_surface, restart_rect)

        # EVENTOS
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "MENU"
                elif e.key == pygame.K_r:
                    return "RESTART_LEVEL"

        return "GAMEOVER"
