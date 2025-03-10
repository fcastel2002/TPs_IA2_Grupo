import pygame
import sys
from typing import List, Tuple, Dict, Set, Optional

# Inicialización de Pygame
pygame.init()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)  # Color marrón para los bordes de estanterías


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


class Grid:
    """Gestiona la cuadrícula completa del mapa."""
    
    def __init__(self, rows: int, cols: int, cell_size: int):
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_size
        self.grid: List[List[Cell]] = []
        self.create_grid()
        self.setup_map()
        
        # Calcular dimensiones exactas de la ventana
        self.width = cols * cell_size
        self.height = rows * cell_size
    
    def create_grid(self) -> None:
        """Crea la estructura de la cuadrícula."""
        self.grid = []
        for i in range(self.rows):
            self.grid.append([])
            for j in range(self.cols):
                cell = Cell(i, j, self.cell_width)
                self.grid[i].append(cell)
    
    def setup_map(self) -> None:
        """Configura el mapa según la disposición proporcionada."""
        # Configurar los bloques numerados (estanterías)
        shelf_blocks = [
            # Bloque 1-8
            [(1, 2), (1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (4, 3)],
            # Bloque 9-16
            [(1, 6), (1, 7), (2, 6), (2, 7), (3, 6), (3, 7), (4, 6), (4, 7)],
            # Bloque 17-24
            [(1, 10), (1, 11), (2, 10), (2, 11), (3, 10), (3, 11), (4, 10), (4, 11)],
            # Bloque 25-32
            [(6, 2), (6, 3), (7, 2), (7, 3), (8, 2), (8, 3), (9, 2), (9, 3)],
            # Bloque 33-40
            [(6, 6), (6, 7), (7, 6), (7, 7), (8, 6), (8, 7), (9, 6), (9, 7)],
            # Bloque 41-48
            [(6, 10), (6, 11), (7, 10), (7, 11), (8, 10), (8, 11), (9, 10), (9, 11)]
        ]
        
        cell_id = 1
        for block in shelf_blocks:
            for i, (row, col) in enumerate(block):
                self.grid[row][col].cell_id = cell_id
                self.grid[row][col].make_shelf()  # Marcar como estantería
                cell_id += 1
        
        # Configurar la celda especial C
        self.grid[5][0].make_special()
    
    def draw(self, win: pygame.Surface) -> None:
        """Dibuja la cuadrícula completa."""
        win.fill(WHITE)
        
        for row in self.grid:
            for cell in row:
                cell.draw(win)
        
        # Dibujar líneas de cuadrícula
        for i in range(self.rows + 1):
            pygame.draw.line(win, GRAY, (0, i * self.cell_width), 
                            (self.cols * self.cell_width, i * self.cell_width), 1)
        for j in range(self.cols + 1):
            pygame.draw.line(win, GRAY, (j * self.cell_width, 0), 
                            (j * self.cell_width, self.rows * self.cell_width), 1)


class Game:
    """Controla el flujo del juego y la visualización."""
    
    def __init__(self, cell_size: int = 50):
        # Definir dimensiones de la cuadrícula
        self.rows = 11
        self.cols = 13
        self.cell_size = cell_size
        
        # Crear la cuadrícula
        self.grid = Grid(self.rows, self.cols, self.cell_size)
        
        # Crear la ventana con el tamaño exacto de la cuadrícula
        self.width = self.grid.width
        self.height = self.grid.height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulador de Montacargas - Algoritmo A*")
        
        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()
        self.fps = 60
    
    def run(self) -> None:
        """Ejecuta el bucle principal del juego."""
        run = True
        
        while run:
            self.clock.tick(self.fps)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
            
            self.draw()
            
        pygame.quit()
        sys.exit()
    
    def draw(self) -> None:
        """Actualiza la pantalla."""
        self.grid.draw(self.window)
        pygame.display.update()


# Ejecutar el juego
if __name__ == "__main__":
    # Puedes ajustar el tamaño de las celdas según necesites
    CELL_SIZE = 50
    game = Game(cell_size=CELL_SIZE)
    game.run()