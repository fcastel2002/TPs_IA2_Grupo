import pygame
from typing import Tuple, Optional

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
class Cell:
    """Representa una casilla individual en la cuadrícula."""
    
    def __init__(self, row: int, col: int, width: int, cell_id: Optional[int] = None):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.width = width
        self.cell_id = cell_id
        self.color = WHITE
        self.is_barrier = False
        self.is_start = False
        self.is_end = False
        self.is_special = False  # Para la casilla 'C'
        self.is_shelf = False    # Para identificar si es parte de una estantería
        
        # Para el algoritmo A*
        self.g_cost = float('inf')  # Costo desde el inicio
        self.h_cost = float('inf')  # Heurística (estimación hasta el final)
        self.f_cost = float('inf')  # Costo total (g + h)
        self.parent = None          # Celda padre en el camino
        self.visited = False        # Si la celda ha sido visitada
        self.in_open_set = False    # Si la celda está en el conjunto abierto
    
    def get_position(self) -> Tuple[int, int]:
        """Devuelve la posición (fila, columna) de la celda."""
        return self.row, self.col
    
    def make_barrier(self) -> None:
        """Marca la celda como barrera."""
        self.is_barrier = True
    
    def make_start(self) -> None:
        """Marca la celda como inicio."""
        self.is_start = True
        self.color = GREEN
    
    def make_end(self) -> None:
        """Marca la celda como destino."""
        self.is_end = True
        self.color = RED
    
    def make_special(self) -> None:
        """Marca la celda como especial (C)."""
        self.is_special = True
        self.color = YELLOW
    
    def make_shelf(self) -> None:
        """Marca la celda como parte de una estantería."""
        self.is_shelf = True
    
    def make_path(self) -> None:
        """Marca la celda como parte del camino encontrado."""
        if not self.is_start and not self.is_end and not self.is_special:
            self.color = BLUE
    
    def make_visited(self) -> None:
        """Marca la celda como visitada por el algoritmo."""
        if not self.is_start and not self.is_end and not self.is_special:
            self.color = (160, 160, 255)  # Azul claro
            self.visited = True
    
    def make_open(self) -> None:
        """Marca la celda como parte del conjunto abierto."""
        if not self.is_start and not self.is_end and not self.is_special:
            self.color = (200, 200, 255)  # Azul más claro
            self.in_open_set = True
    
    def reset(self) -> None:
        """Resetea los atributos de la celda para algoritmos de búsqueda."""
        if not self.is_start and not self.is_end and not self.is_special and not self.is_barrier:
            self.color = WHITE
        self.g_cost = float('inf')
        self.h_cost = float('inf')
        self.f_cost = float('inf')
        self.parent = None
        self.visited = False
        self.in_open_set = False
    
    def get_f_cost(self) -> float:
        """Retorna el costo total (f = g + h)."""
        return self.g_cost + self.h_cost
    
    def draw(self, win: pygame.Surface) -> None:
        """Dibuja la celda en la ventana."""
        # Dibujar el fondo de la celda
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
        # Dibujar el borde según el tipo de celda
        border_color = BROWN if self.is_shelf else BLACK
        border_width = 3 if self.is_shelf else 1
        pygame.draw.rect(win, border_color, (self.x, self.y, self.width, self.width), border_width)
        
        # Si tiene ID, mostrarla
        if self.cell_id is not None:
            font = pygame.font.SysFont('calibri', 20)
            text = font.render(str(self.cell_id), True, BLACK)
            win.blit(text, (self.x + self.width // 2 - text.get_width() // 2, 
                            self.y + self.width // 2 - text.get_height() // 2))
        
        # Si es la celda especial C
        if self.is_special:
            font = pygame.font.SysFont('arial', 30, bold=True)
            text = font.render('C', True, BLACK)
            win.blit(text, (self.x + self.width // 2 - text.get_width() // 2, 
                            self.y + self.width // 2 - text.get_height() // 2))