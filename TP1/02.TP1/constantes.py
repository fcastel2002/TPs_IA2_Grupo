import pygame


CANT_FILAS = 11
CANT_COLUMNAS = 13

# Definir colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0) # Color objetivo principal 
GREEN = (0, 255, 0) # Color Montacargas Inicio
COLORES_OBJETIVOS = ['red','yellow','sandy brown','blue2','DarkGoldenrod4','bisque3','cyan3','MediumPurple2']
# Función para convertir colores hexadecimales a tuplas RGB
def hex_a_rgb(hex_color):
    # Eliminar el símbolo # si está presente
    hex_color = hex_color.lstrip('#')
    # Convertir el valor hexadecimal a decimales RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Paleta de colores original en formato hexadecimal
paleta_hex = [
    "#D4F1F9", "#B3E0F2", "#91CDEA", "#6BAFD6", 
    "#4682B4", "#3A75C4", "#4B6EAF", "#6A5ACD", 
    "#8B5F8A", "#A55D7B", "#C25B6C", "#D84A5F", 
    "#E63946", "#F13030", "#FA1E1E", "#FF0000"
]

# Convertir a formato RGB para Pygame
PALETA_FRECUENCIAS = [hex_a_rgb(color) for color in paleta_hex]
BLUE = pygame.Color('blue')
# Definir tamaño de la ventana y de los casilleros
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 600
CELL_SIZE = 50
