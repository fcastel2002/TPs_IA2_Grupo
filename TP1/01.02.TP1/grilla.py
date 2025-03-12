import pygame
from typing import List, Tuple, Optional
from celda import Cell

GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
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
        
        # Para el algoritmo A*
        self.start_cell: Optional[Cell] = None
        self.end_cell: Optional[Cell] = None
    
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
    
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Retorna la celda en la posición especificada."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None
    
    def get_neighbors(self, cell: Cell) -> List[Cell]:
        """Retorna los vecinos válidos de una celda."""
        neighbors = []
        row, col = cell.get_position()
        
        # Movimientos posibles: arriba, derecha, abajo, izquierda
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            neighbor = self.get_cell(new_row, new_col)
            if neighbor and not neighbor.is_barrier:
                neighbors.append(neighbor)
        
        return neighbors
    
    def set_start(self, row: int, col: int) -> bool:
        """Establece la celda de inicio."""
        cell = self.get_cell(row, col)
        if cell and not cell.is_barrier and not cell.is_end:
            # Resetear la celda de inicio anterior si existe
            if self.start_cell:
                self.start_cell.reset()
                self.start_cell.color = WHITE
                self.start_cell.is_start = False
            
            cell.make_start()
            self.start_cell = cell
            return True
        return False
    
    def set_end(self, row: int, col: int) -> bool:
        """Establece la celda de destino."""
        cell = self.get_cell(row, col)
        if cell and not cell.is_barrier and not cell.is_start:
            # Resetear la celda de destino anterior si existe
            if self.end_cell:
                self.end_cell.reset()
                self.end_cell.color = WHITE
                self.end_cell.is_end = False
            
            cell.make_end()
            self.end_cell = cell
            return True
        return False
    
    def reset_path(self) -> None:
        """Resetea todas las celdas excepto inicio, fin, barreras y especiales."""
        for row in self.grid:
            for cell in row:
                if not cell.is_start and not cell.is_end and not cell.is_barrier and not cell.is_special:
                    cell.reset()
    
    def draw(self, win: pygame.Surface) -> None:
        """Dibuja la cuadrícula completa."""
        win.fill((255, 255, 255))
        
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
    def get_occupied_positions(self):
        """Devuelve las posiciones ocupadas en la cuadrícula."""
        occupied = set()
        for row in self.grid:
            for cell in row:
                if cell.is_barrier or cell.is_shelf:
                    occupied.add(cell.get_position())
        return occupied
