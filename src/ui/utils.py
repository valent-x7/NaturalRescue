from settings import *
import json

# Dibuja texto
def draw_text(screen, font_path, font_size, text, color, x, y):

    # Cargamos fuente
    font = pygame.font.Font(font_path, font_size)

    # Creamos superficie del texto y su rectangulo
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_frect()
    
    # Ajustamos la posición
    text_rect.centerx = x
    text_rect.centery = y

    # Dibujamos en pantalla
    screen.blit(text_surface, text_rect)

# Cargar configuración
def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        settings = json.load(f)
        return settings["lenguaje"]
    
# Cargar dificultad
def load_difficulty(path):
    with open(path, "r", encoding="utf-8") as f:
        settings = json.load(f)
        return settings["difficulty"] # -> Normal o avanzado
    
def set_difficulty(path, new_difficulty):
    with open(path, "r", encoding="utf-8") as f: # -> Leer la dificultad
        settings = json.load(f)

    settings["difficulty"] = new_difficulty # -> Asignamos nueva dificultad

    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

# Cargar idioma
def load_language(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
# Obtener texto
def get_text(translation_dict, lang, key):
    return translation_dict.get(lang, {}).get(key, key)

# Cambiar el lenguaje
def set_language(config_path, lang):
    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    # Asignamos el lenguaje nuevo
    settings["lenguaje"] = lang

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def draw_text_space(screen, font_path, font_size, text, color, x, y, line_spacing = 1.5):
    # Cargamos fuente
    font = pygame.font.Font(font_path, font_size)
    lines = text.split('\n') # -> Dividimos texto
    
    # Calculamos la altura
    line_height = font.get_linesize() 
    total_height = (len(lines) - 1) * (line_height * line_spacing) + line_height
    current_y = y - (total_height / 2) + (line_height / 2) # -> Calculamos la posición Y inicial
    
    for line in lines:
        # Creamos superficie del texto y su rectángulo
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_frect()
        
        text_rect.centerx = x
        text_rect.centery = current_y
        
        # Dibujamos en pantalla
        screen.blit(text_surface, text_rect)
        current_y += line_height * line_spacing # -> Avanzamos la pos de y

def draw_text_optimized(screen: pygame.Surface, font: pygame.Font, text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_frect(center = (x, y))
    screen.blit(text_surface, text_rect)