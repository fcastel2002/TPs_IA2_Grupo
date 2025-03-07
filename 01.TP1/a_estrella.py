# a_star.py
import pygame
import heapq
import time
from typing import List, Tuple, Set, Dict, Optional, Callable

class AStar:
    """
    Implementación optimizada del algoritmo A* para encontrar el camino más corto
    hacia estanterías en un sistema de almacén con montacargas.
    """
    
    def __init__(self, grid):
        """
        Inicializa el algoritmo A* con la cuadrícula proporcionada.
        
        Args:
            grid: La cuadrícula que contiene las celdas y la información del mapa.
        """
        self.grid = grid
        self.open_set = []  # Cola de prioridad para el conjunto abierto
        self.open_set_hash = set()  # Conjunto para verificación O(1)
        self.closed_set = set()  # Conjunto de nodos ya evaluados
        
        # Métricas de rendimiento
        self.nodes_visited = 0
        self.max_open_set_size = 0
        self.execution_time = 0
        
        # Para destino a estantería
        self.target_shelf = None  # Celda de estantería objetivo
        self.target_adjacent_cells = []  # Celdas adyacentes válidas a la estantería
        self.target_is_shelf = False  # Indica si el objetivo es una estantería
    
    def heuristic(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float: ##Podemos usar heuristica mixta? (Manhattan + Euclidea)
        """
        Calcula la heurística (distancia Manhattan) entre dos puntos. 
        
        Args:
            p1: Coordenadas (fila, columna) del primer punto.
            p2: Coordenadas (fila, columna) del segundo punto.
            
        Returns:
            float: La distancia Manhattan entre los dos puntos.
        """
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)
    
    def is_valid_neighbor(self, cell, neighbor) -> bool:
        """
        Verifica si un vecino es válido para el movimiento del montacargas.
        
        Args:
            cell: La celda actual desde donde se mueve el montacargas.
            neighbor: La celda vecina a la que se quiere mover.
            
        Returns:
            bool: True si el movimiento es válido, False en caso contrario.
        """
        # No permitir movimiento a celdas con barrera
        if neighbor.is_barrier:
            return False
            
        # No permitir movimiento a través de estanterías (a menos que sea el destino)
        if neighbor.is_shelf and (not self.target_is_shelf or neighbor != self.grid.end_cell):
            return False
            
        return True
    
    def get_valid_neighbors(self, cell) -> List:
        """
        Obtiene todos los vecinos válidos para una celda dada.
        
        Args:
            cell: La celda para la cual se buscan vecinos válidos.
            
        Returns:
            List: Lista de celdas vecinas válidas.
        """
        neighbors = self.grid.get_neighbors(cell)
        return [n for n in neighbors if self.is_valid_neighbor(cell, n)]
    
    def find_adjacent_cells(self, shelf_cell) -> List:
        """
        Encuentra celdas adyacentes horizontalmente a una estantería.
        
        Args:
            shelf_cell: La celda de estantería objetivo.
            
        Returns:
            List: Lista de celdas adyacentes válidas.
        """
        row, col = shelf_cell.get_position()
        adjacent_cells = []
        
        # Comprobar posiciones izquierda y derecha (horizontalmente adyacentes)
        for adj_col in [col - 1, col + 1]:
            if 0 <= adj_col < self.grid.cols:
                adj_cell = self.grid.get_cell(row, adj_col)
                if adj_cell and not adj_cell.is_barrier and not adj_cell.is_shelf:
                    adjacent_cells.append(adj_cell)
        
        return adjacent_cells
    
    def prepare_search(self) -> bool:
        """
        Prepara la búsqueda analizando el destino y configurando el objetivo adecuadamente.
        
        Returns:
            bool: True si la preparación fue exitosa, False en caso contrario.
        """
        # Resetear estado
        self.reset_state()
        
        # Verificar si tenemos un punto de inicio
        if not self.grid.start_cell:
            print("Error: No se ha definido el punto de inicio.")
            return False
        
        # Verificar si tenemos un destino
        if not self.grid.end_cell:
            print("Error: No se ha definido el punto de destino.")
            return False
        
        # Analizar el tipo de destino
        end_cell = self.grid.end_cell
        
        # Si el destino es una estantería, necesitamos encontrar celdas adyacentes
        if end_cell.is_shelf:
            self.target_is_shelf = True
            self.target_shelf = end_cell
            self.target_adjacent_cells = self.find_adjacent_cells(end_cell)
            
            # Verificar que haya al menos una celda adyacente accesible
            if not self.target_adjacent_cells:
                print(f"Error: No hay celdas adyacentes accesibles a la estantería {end_cell.cell_id}.")
                return False
                
            print(f"Buscando camino hacia la estantería {end_cell.cell_id}...")
            print(f"Celdas adyacentes encontradas: {len(self.target_adjacent_cells)}")
        else:
            self.target_is_shelf = False
            self.target_shelf = None
            self.target_adjacent_cells = []
            print("Buscando camino hacia un destino normal...") ##Acá se podria hacer que pida devuelta una celda objetivo?
        
        return True
    
    def is_destination_reached(self, current) -> bool:
        """
        Verifica si se ha alcanzado el destino según el tipo de búsqueda.
        
        Args:
            current: La celda actual que se está evaluando.
            
        Returns:
            bool: True si se ha llegado al destino, False en caso contrario.
        """
        if self.target_is_shelf:
            # Si el destino es una estantería, verificar si estamos en una celda adyacente
            return current in self.target_adjacent_cells
        else:
            # Si es un destino normal, verificar si estamos en la celda de destino
            return current == self.grid.end_cell
    
    def calculate_heuristic(self, cell, is_for_open_set: bool = False) -> float:
        """
        Calcula la heurística según el tipo de destino.
        
        Args:
            cell: La celda para la cual calcular la heurística.
            is_for_open_set: Indica si el cálculo es para añadir al conjunto abierto.
            
        Returns:
            float: Valor de la heurística.
        """
        if self.target_is_shelf:
            # Si el destino es una estantería, usar la celda adyacente más cercana
            min_h = float('inf')
            for adj_cell in self.target_adjacent_cells:
                h = self.heuristic(cell.get_position(), adj_cell.get_position())
                min_h = min(min_h, h)
            return min_h
        else:
            # Si es un destino normal, usar la celda de destino directamente
            return self.heuristic(cell.get_position(), self.grid.end_cell.get_position())
    
    def reconstruct_path(self, current, draw_function: Callable) -> List[Tuple[int, int]]:
        """
        Reconstruye el camino desde el destino hasta el inicio y lo visualiza.
        
        Args:
            current: La celda actual (normalmente la celda adyacente a la estantería).
            draw_function: Función para actualizar la visualización.
            
        Returns:
            List[Tuple[int, int]]: Lista de coordenadas (fila, columna) que forman el camino.
        """
        path = []
        
        # Añadir la celda actual (posición final del montacargas)
        path.append(current.get_position())
        current.make_path()  # Añade esta línea
        draw_function()      # Añade esta línea para actualizar inmediatamente
        # Reconstruir el camino hacia atrás
        while current.parent:
            current = current.parent
            if not current.is_start:  # No cambiar el color de la celda de inicio
                current.make_path()
            path.append(current.get_position())
            draw_function()
            pygame.time.delay(20)  # Pequeña pausa para visualizar mejor el camino
        
        # Invertir para que el camino vaya del inicio al destino
        path.reverse()
        
        # Si el destino es una estantería, destacarla visualmente
        if self.target_is_shelf and self.target_shelf:
            # Añadir algún efecto visual para destacar la estantería objetivo
            # (esto dependerá de tu implementación visual)
            pass
        
        return path
    
    def reset_state(self) -> None:
        """Resetea el estado del algoritmo para una nueva ejecución."""
        self.open_set = []
        self.open_set_hash = set()
        self.closed_set = set()
        self.nodes_visited = 0
        self.max_open_set_size = 0
        self.execution_time = 0
        self.target_is_shelf = False
        self.target_shelf = None
        self.target_adjacent_cells = []
    
    def run(self, draw_function: Callable, delay: int = 20) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Ejecuta el algoritmo A* para encontrar el camino más corto.
        
        Args:
            draw_function: Función para actualizar la visualización.
            delay: Retraso en milisegundos entre pasos para visualización.
            
        Returns:
            Tuple[bool, List[Tuple[int, int]]]: (éxito, camino)
        """
        # Preparar la búsqueda según el tipo de destino
        if not self.prepare_search():
            return False, []
        
        start_time = time.time()
        
        # Obtener celda de inicio
        start = self.grid.start_cell
        
        # Inicializar la celda de inicio
        start.g_cost = 0
        start.h_cost = self.calculate_heuristic(start)
        start.f_cost = start.h_cost
        
        # Añadir la celda de inicio al conjunto abierto
        count = 0  # Para desempatar cuando dos nodos tienen el mismo f_cost
        heapq.heappush(self.open_set, (start.f_cost, count, start))
        self.open_set_hash.add(start)
        start.in_open_set = True
        
        # Bucle principal del algoritmo
        while self.open_set:
            # Verificar eventos de Pygame (para salir, etc.)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False, []
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False, []
            
            # Actualizar métricas
            self.max_open_set_size = max(self.max_open_set_size, len(self.open_set))
            
            # Obtener el nodo con menor f_cost
            current = heapq.heappop(self.open_set)[2]
            self.open_set_hash.remove(current)
            current.in_open_set = False
            self.closed_set.add(current)
            self.nodes_visited += 1
            
            # Verificar si hemos llegado al destino
            if self.is_destination_reached(current):
                self.execution_time = time.time() - start_time
                path = self.reconstruct_path(current, draw_function)
                
                # Asegurar que inicio y destino mantengan sus colores
                start.make_start()
                
                if self.target_is_shelf:
                    self.target_shelf.make_end()  # Asegurar que la estantería destino mantenga su color
                    print(f"Camino encontrado a la estantería {self.target_shelf.cell_id}")
                else:
                    self.grid.end_cell.make_end()
                
                # Mostrar métricas de rendimiento
                print(f"A* completado en {self.execution_time:.4f} segundos")
                print(f"Nodos visitados: {self.nodes_visited}")
                print(f"Tamaño máximo del conjunto abierto: {self.max_open_set_size}")
                print(f"Longitud del camino: {len(path)}")
                
                return True, path
            
            # Explorar vecinos válidos
            for neighbor in self.get_valid_neighbors(current):
                # Saltar vecinos ya evaluados
                if neighbor in self.closed_set:
                    continue
                
                # Calcular nuevo costo g tentativo
                tentative_g_cost = current.g_cost + 1
                
                # Si encontramos un camino mejor a este vecino
                if tentative_g_cost < neighbor.g_cost:
                    # Actualizar camino y costos
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.calculate_heuristic(neighbor, True)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    
                    # Si el vecino no está en el conjunto abierto, añadirlo
                    if neighbor not in self.open_set_hash:
                        count += 1
                        heapq.heappush(self.open_set, (neighbor.f_cost, count, neighbor))
                        self.open_set_hash.add(neighbor)
                        neighbor.make_open()
            
            # Visualizar el proceso
            draw_function()
            if delay > 0:
                pygame.time.delay(delay)
            
            # Marcar como visitada (excepto el inicio y el destino)
            if current != start and current != self.grid.end_cell:
                current.make_visited()
        
        # Si llegamos aquí, no se encontró camino
        self.execution_time = time.time() - start_time
        print("No se encontró un camino al destino.")
        print(f"A* terminado en {self.execution_time:.4f} segundos")
        print(f"Nodos visitados: {self.nodes_visited}")
        print(f"Tamaño máximo del conjunto abierto: {self.max_open_set_size}")
        
        return False, []