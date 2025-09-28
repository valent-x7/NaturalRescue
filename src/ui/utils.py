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