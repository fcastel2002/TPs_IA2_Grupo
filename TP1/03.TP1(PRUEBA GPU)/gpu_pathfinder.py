# archivo: gpu_pathfinder.py

import numpy as np
import math
import random
from numba import cuda, jit, float32, int32, boolean
import heapq
import numba.cuda.random as cuda_random
# Constantes
MAX_GRID_SIZE = 143  # Tamaño máximo de tablero
MAX_OPEN_NODES = 143 # Máximo número de nodos abiertos
MAX_ORDER_SIZE = 50  # Tamaño máximo de orden
INFINITY = float('inf')

@cuda.jit(device=True)
def heuristica_distancia_device(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos (optimizado para GPU)"""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

@cuda.jit(device=True)
def manhattan_distance_device(x1, y1, x2, y2):
    """Calcula la distancia Manhattan entre dos puntos (optimizado para GPU)"""
    return abs(x1 - x2) + abs(y1 - y2)

@cuda.jit(device=True)
def calcular_costo_total_device(orden, orders, order_count, order_size):
    """
    Calcula el costo total de recorrer los objetivos en el orden dado
    (versión para dispositivo GPU)
    
    Args:
        orden: Array local con índices en el orden a evaluar
        orders: Array 2D con los índices de casillas para cada orden
        order_count: Número de órdenes
        order_size: Tamaño máximo de cada orden
        
    Returns:
        Costo total (suma de distancias Manhattan)
    """
    costo_total = 0.0
    
    # Punto de inicio (celda C, asumimos que está en 5,0)
    x_actual, y_actual = 0, 5
    
    # Para cada objetivo en el orden
    for i in range(order_size):
        if orden[i] >= order_size:
            continue  # Ignorar índices inválidos
            
        # Obtener coordenadas del objetivo
        idx_objetivo = orden[i]
        
        # Convertir índice lineal a coordenadas
        # Asumiendo un tablero de 13 columnas (como en el problema original)
        x_objetivo = orders[0, idx_objetivo] % 13
        y_objetivo = orders[0, idx_objetivo] // 13
        
        # Calcular distancia Manhattan
        distancia = manhattan_distance_device(x_actual, y_actual, x_objetivo, y_objetivo)
        costo_total += distancia
        
        # Actualizar posición actual
        x_actual, y_actual = x_objetivo, y_objetivo
    
    # Regresar a la celda C (5,0)
    costo_total += manhattan_distance_device(x_actual, y_actual, 0, 5)
    
    return costo_total

@cuda.jit
def a_star_kernel(grid, start_x, start_y, goal_x, goal_y, width, height, 
                  path_x, path_y, path_length, success):
    """
    Implementación CUDA del algoritmo A* para encontrar caminos
    
    Parámetros:
    -----------
    grid: Array 2D de booleanos (True=libre, False=obstáculo)
    start_x, start_y: Coordenadas de inicio
    goal_x, goal_y: Coordenadas objetivo
    width, height: Dimensiones del grid
    path_x, path_y: Arrays para guardar el camino resultante
    path_length: Variable para guardar la longitud del camino
    success: Variable para indicar si se encontró un camino
    """
    # Inicialización
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    bx = cuda.blockIdx.x
    by = cuda.blockIdx.y
    
    # Solo ejecutar en un hilo
    if tx == 0 and ty == 0 and bx == 0 and by == 0:
        # Inicializar estructuras
        open_list = []
        heapq.heappush(open_list, (0, start_x, start_y))  # (f_score, x, y)
        
        # Diccionarios para controlar el proceso de búsqueda
        came_from = {}
        g_score = {}
        f_score = {}
        closed_set = set()
        
        # Valores iniciales
        g_score[(start_x, start_y)] = 0
        f_score[(start_x, start_y)] = heuristica_distancia_device(start_x, start_y, goal_x, goal_y)
        
        # Direcciones posibles (4-conectividad)
        dx = [0, 1, 0, -1]
        dy = [-1, 0, 1, 0]
        
        found_path = False
        
        # Bucle principal de A*
        while open_list:
            # Obtener nodo con menor f_score
            current = heapq.heappop(open_list)
            current_f, current_x, current_y = current
            
            # Si hemos llegado al objetivo
            if current_x == goal_x and current_y == goal_y:
                found_path = True
                break
            
            # Añadir a cerrados
            closed_set.add((current_x, current_y))
            
            # Explorar vecinos
            for i in range(4):
                neighbor_x = current_x + dx[i]
                neighbor_y = current_y + dy[i]
                
                # Comprobar límites y obstáculos
                if (neighbor_x < 0 or neighbor_x >= width or 
                    neighbor_y < 0 or neighbor_y >= height or
                    not grid[neighbor_y, neighbor_x] or
                    (neighbor_x, neighbor_y) in closed_set):
                    continue
                
                # Calcular g_score tentativo
                tentative_g = g_score.get((current_x, current_y), INFINITY) + 1
                
                # Si ya está en abiertos con mejor g_score, ignorar
                if ((neighbor_x, neighbor_y) in g_score and 
                    tentative_g >= g_score.get((neighbor_x, neighbor_y), INFINITY)):
                    continue
                
                # Este camino es mejor, guardar
                came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                g_score[(neighbor_x, neighbor_y)] = tentative_g
                f = tentative_g + heuristica_distancia_device(neighbor_x, neighbor_y, goal_x, goal_y)
                f_score[(neighbor_x, neighbor_y)] = f
                
                # Añadir a abiertos
                heapq.heappush(open_list, (f, neighbor_x, neighbor_y))
        
        # Reconstruir camino si se encontró
        if found_path:
            # Reconstruir camino
            current = (goal_x, goal_y)
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append((start_x, start_y))
            path.reverse()
            
            # Guardar camino en los arrays de salida
            for i in range(min(len(path), len(path_x))):
                path_x[i] = path[i][0]
                path_y[i] = path[i][1]
            
            path_length[0] = len(path)
            success[0] = 1
        else:
            success[0] = 0

@cuda.jit
def simulated_annealing_kernel(rng_states, orders, order_count, order_size, 
                              best_order, best_cost, 
                              temp_inicial, factor_enfriamiento, max_iteraciones):
    """
    Implementación CUDA de Temple Simulado para optimizar el orden de visita
    
    Parámetros:
    -----------
    rng_states: Estados para generación de números aleatorios
    orders: Array 2D con los órdenes (indices de casillas)
    order_count: Número de órdenes
    order_size: Tamaño máximo de cada orden
    best_order: Array para guardar el mejor orden encontrado
    best_cost: Variable para guardar el mejor costo
    temp_inicial, factor_enfriamiento, max_iteraciones: Parámetros del algoritmo
    """
    # Obtener ID de hilo para generación de números aleatorios
    thread_id = cuda.grid(1)
    
    # Solo ejecutar en un hilo por bloque
    if cuda.threadIdx.x == 0 and cuda.blockIdx.x == 0:
        # Inicializar orden aleatorio
        orden_actual = cuda.local.array(MAX_ORDER_SIZE, dtype=int32)
        for i in range(order_size):
            orden_actual[i] = i
        
        # Mezclar orden aleatoriamente (Fisher-Yates shuffle)
        for i in range(order_size - 1, 0, -1):
            j = int(cuda_random.xoroshiro128p_uniform_float32(rng_states, thread_id) * (i + 1))
            # Intercambiar i y j
            temp = orden_actual[i]
            orden_actual[i] = orden_actual[j]
            orden_actual[j] = temp
        
        # Calcular costo inicial
        mejor_costo = calcular_costo_total_device(orden_actual, orders, order_count, order_size)
        
        # Guardar mejor orden
        mejor_orden = cuda.local.array(MAX_ORDER_SIZE, dtype=int32)
        for i in range(order_size):
            mejor_orden[i] = orden_actual[i]
        
        # Temple simulado
        temp = temp_inicial
        
        for iter in range(max_iteraciones):
            # Generar vecino (intercambio aleatorio)
            orden_vecino = cuda.local.array(MAX_ORDER_SIZE, dtype=int32)
            for i in range(order_size):
                orden_vecino[i] = orden_actual[i]
            
            # Seleccionar dos posiciones aleatorias
            idx1 = int(cuda_random.xoroshiro128p_uniform_float32(rng_states, thread_id) * order_size)
            idx2 = int(cuda_random.xoroshiro128p_uniform_float32(rng_states, thread_id) * order_size)
            
            # Intercambiar
            temp_val = orden_vecino[idx1]
            orden_vecino[idx1] = orden_vecino[idx2]
            orden_vecino[idx2] = temp_val
            
            # Calcular costo del vecino
            costo_vecino = calcular_costo_total_device(orden_vecino, orders, order_count, order_size)
            
            # Determinar si aceptamos el vecino
            delta_e = costo_vecino - mejor_costo
            
            if delta_e < 0:  # Si es mejor, aceptar
                for i in range(order_size):
                    orden_actual[i] = orden_vecino[i]
                mejor_costo = costo_vecino
                
                # Actualizar mejor global si corresponde
                if costo_vecino < mejor_costo:
                    mejor_costo = costo_vecino
                    for i in range(order_size):
                        mejor_orden[i] = orden_vecino[i]
            else:  # Si es peor, aceptar con probabilidad
                prob = math.exp(-delta_e / temp)
                if cuda_random.xoroshiro128p_uniform_float32(rng_states, thread_id) < prob:
                    for i in range(order_size):
                        orden_actual[i] = orden_vecino[i]
            
            # Enfriamiento
            temp *= factor_enfriamiento
            if temp < 0.01:
                break
        
        # Guardar mejor orden y costo
        for i in range(order_size):
            best_order[i] = mejor_orden[i]
        best_cost[0] = mejor_costo

def a_star_gpu(grid, start, goal):
    """
    Función Python para preparar y lanzar el kernel A* en GPU
    
    Parámetros:
    -----------
    grid: Array 2D numpy (True=libre, False=obstáculo)
    start: Tuple (x, y) con posición inicial
    goal: Tuple (x, y) con posición objetivo
    
    Retorna:
    --------
    path: Lista de tuplas (x, y) representando el camino, o None si no hay camino
    """
    # Preparar datos para GPU
    d_grid = cuda.to_device(grid)
    height, width = grid.shape
    start_x, start_y = start
    goal_x, goal_y = goal
    
    # Arrays para el resultado
    path_x = np.zeros(MAX_GRID_SIZE, dtype=np.int32)
    path_y = np.zeros(MAX_GRID_SIZE, dtype=np.int32)
    path_length = np.zeros(1, dtype=np.int32)
    success = np.zeros(1, dtype=np.int32)
    
    d_path_x = cuda.to_device(path_x)
    d_path_y = cuda.to_device(path_y)
    d_path_length = cuda.to_device(path_length)
    d_success = cuda.to_device(success)
    
    # Configurar y lanzar kernel
    threads_per_block = (16, 16)
    blocks_per_grid = (1, 1)
    
    a_star_kernel[blocks_per_grid, threads_per_block](
        d_grid, start_x, start_y, goal_x, goal_y, width, height,
        d_path_x, d_path_y, d_path_length, d_success
    )
    
    # Recuperar resultados
    path_x = d_path_x.copy_to_host()
    path_y = d_path_y.copy_to_host()
    path_length = d_path_length.copy_to_host()[0]
    success = d_success.copy_to_host()[0]
    
    if success:
        # Crear lista de tuplas con el camino
        path = [(path_x[i], path_y[i]) for i in range(path_length)]
        return path
    else:
        return None

def temple_simulado_gpu(orders, temp_inicial=100, factor_enfriamiento=0.95, max_iteraciones=100):
    """
    Función Python para preparar y lanzar el kernel de Temple Simulado en GPU
    
    Parámetros:
    -----------
    orders: Lista de índices de órdenes
    temp_inicial, factor_enfriamiento, max_iteraciones: Parámetros del algoritmo
    
    Retorna:
    --------
    best_order: El mejor orden de visita encontrado
    best_cost: El costo asociado
    """
    # Preparar datos para GPU
    order_count = 1  # Una sola orden en este caso
    order_size = len(orders)
    
    # Crear array 2D para órdenes
    d_orders = np.zeros((order_count, MAX_ORDER_SIZE), dtype=np.int32)
    for i, item in enumerate(orders):
        if i < MAX_ORDER_SIZE:
            d_orders[0, i] = item
    
    # Arrays para resultados
    best_order = np.zeros(MAX_ORDER_SIZE, dtype=np.int32)
    best_cost = np.zeros(1, dtype=np.float32)
    
    d_orders = cuda.to_device(d_orders)
    d_best_order = cuda.to_device(best_order)
    d_best_cost = cuda.to_device(best_cost)
    
    # Configurar y lanzar kernel
    threads_per_block = 256
    blocks_per_grid = 1
    
    # Inicializar estados para generación de números aleatorios
    rng_states = cuda_random.create_xoroshiro128p_states(threads_per_block * blocks_per_grid, seed=1234)
    
    simulated_annealing_kernel[blocks_per_grid, threads_per_block](
        rng_states, d_orders, order_count, order_size,
        d_best_order, d_best_cost,
        temp_inicial, factor_enfriamiento, max_iteraciones
    )
    
    # Recuperar resultados
    best_order = d_best_order.copy_to_host()
    best_cost = d_best_cost.copy_to_host()[0]
    
    # Filtrar solo los índices válidos (menores que order_size)
    valid_indices = [best_order[i] for i in range(MAX_ORDER_SIZE) if best_order[i] < order_size]
    
    return valid_indices, best_cost