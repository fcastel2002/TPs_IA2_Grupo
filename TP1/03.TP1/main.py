# main.py

import os
import time
import csv
import random
import pygame
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

# Importar nuestras clases y funciones ya definidas
from constantes import WINDOW_WIDTH, WINDOW_HEIGHT, CANT_FILAS, CANT_COLUMNAS, CELL_SIZE
from algoritmo_genetico import generar_poblacion, Individuo
from fitness_evaluator import FitnessEvaluator
from selector import Selector
from utils import get_initial_config
from crossover import pmx_crossover, crossover_operator

# ========== Parámetros del GA ==========
POPULATION_SIZE = 50      # Número de individuos en la población
NUM_GENERATIONS = 150     # Número de generaciones a ejecutar
MUTATION_RATE = 0.2      # Probabilidad de mutación (intercambio) en cada hijo
TOURNAMENT_SIZE = 2       # Tamaño del torneo para selección
ELITISM = True            # Activar o desactivar elitismo

# ========== Operador de mutación por intercambio (swap) ==========
def swap_mutation(config, mutation_rate=MUTATION_RATE):
    """
    Mutación por intercambio (swap).
    Con probabilidad 'mutation_rate', elige 2 posiciones al azar y las intercambia.
    """
    new_config = config.copy()
    if random.random() < mutation_rate:
        i = random.randint(0, len(new_config) - 1)
        j = random.randint(0, len(new_config) - 1)
        new_config[i], new_config[j] = new_config[j], new_config[i]
    return new_config

# ========== Funciones para representar frecuencia con escala de colores discretos ==========
def compute_frequencies(orders):
    """
    Calcula la frecuencia de cada producto (entero) en la lista de órdenes.
    """
    freq = {}
    for order in orders:
        for prod in order:
            try:
                p = int(prod)
                freq[p] = freq.get(p, 0) + 1
            except:
                pass
    return freq

def generate_discrete_palette(max_freq):
    """
    Genera una lista de 'max_freq' colores discretos,
    desde azul (para freq=1) hasta rojo (para freq=max_freq).
    """
    palette = []
    for f in range(1, max_freq + 1):
        ratio = f / float(max_freq)  # va de 1/max_freq hasta 1
        r = int(255 * ratio)
        b = 255 - r
        palette.append((r, 0, b))
    return palette

def get_discrete_color(freq_value, max_freq, palette):
    """
    Dado un valor de frecuencia 'freq_value' en [1..max_freq],
    retorna palette[freq_value - 1].
    Si freq_value es 0 (no aparece en órdenes), retorna un color gris.
    Si freq_value > max_freq, se usa el color del final (palette[-1]).
    """
    if freq_value == 0:
        return (128, 128, 128)  # gris para freq=0
    if freq_value <= max_freq:
        return palette[freq_value - 1]
    # saturar si freq_value > max_freq
    return palette[-1]

def draw_discrete_legend(screen, x, y, box_size, freq_min, freq_max, palette, font):
    """
    Dibuja una leyenda vertical con recuadros de colores discretos
    desde freq_min hasta freq_max.
    """
    current_y = y
    for freq in range(freq_min, freq_max + 1):
        color = palette[freq - 1]  # freq=1 -> palette[0]
        pygame.draw.rect(screen, color, (x, current_y, box_size, box_size))
        label = font.render(str(freq), True, (0,0,0))
        screen.blit(label, (x + box_size + 5, current_y))
        current_y += box_size + 5

# ========== Función para mostrar el tablero final con escala de colores discretos ==========
def mostrar_mejor_solucion(best_ind, config_app, orders_csv_path):
    """
    Muestra la mejor solución (best_ind) con un mapa de calor discreto.
    """
    # Re-inicializamos Pygame en modo visible
    pygame.display.quit()
    os.environ.pop("SDL_VIDEODRIVER", None)  # Remover 'dummy'
    pygame.display.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mejor Solución con Mapa de Calor (Discreto)")
    
    # Crear la aplicación y el tablero
    from aplicacion import Aplicacion
    app = Aplicacion(config_app)
    app.llenar_tablero()
    tablero = app.tablero
    tablero.asignar_configuracion(best_ind.configuracion)
    
    # Leer órdenes y calcular frecuencias
    orders = []
    with open(orders_csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            orders.append(row)
    freq = compute_frequencies(orders)
    if freq:
        max_freq = max(freq.values())
        min_freq = min(freq.values())
    else:
        max_freq = 1
        min_freq = 0
    
    # Generar la paleta discreta
    palette = generate_discrete_palette(max_freq)
    
    # Asignar color a cada casilla de estantería
    for cas in tablero.casilleros:
        if not cas.libre and cas.caracter != "C" and cas.caracter != "":
            try:
                prod = int(cas.caracter)
                freq_value = freq.get(prod, 0)
                cas.color = get_discrete_color(freq_value, max_freq, palette)
            except:
                pass
    
    # Dibujar el tablero
    tablero.dibujar(screen)
    
    # Dibujar la leyenda
    font = pygame.font.SysFont("arial", 16)
    legend_x = WINDOW_WIDTH - 80
    legend_y = 50
    box_size = 20
    draw_discrete_legend(screen, legend_x, legend_y, box_size,
                         1 if min_freq < 1 else min_freq,  # para no romper si min_freq=0
                         max_freq, palette, font)

    pygame.display.flip()
    print("Mostrando la mejor solución con escala de colores discreta. Cierre la ventana para finalizar.")

    # Esperar a que se cierre la ventana
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

# ========== Ciclo principal del GA ==========
def genetic_algorithm():
    population_size = POPULATION_SIZE
    num_generations = NUM_GENERATIONS
    config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv = os.path.join(script_dir, "ordenes.csv")
    
    # Inicializar población
    population = generar_poblacion(population_size)
    selector = Selector(tournament_size=TOURNAMENT_SIZE)
    
    total_start = time.perf_counter()
    best_overall = None
    evaluator = FitnessEvaluator(orders_csv, config_app)
    
    # Evaluar la población inicial
    population, fitness_results, elapsed = evaluator.evaluate_population(population)
    best_overall = min(population, key=lambda ind: ind.fitness)
    
    for gen in range(1, num_generations + 1):
        gen_start = time.perf_counter()
        print(f"\n=== Generación {gen} ===")
        best = min(population, key=lambda ind: ind.fitness)
        if best_overall is None or best.fitness < best_overall.fitness:
            best_overall = best
        new_population = []
        if ELITISM:
            new_population.append(best)
        
        # Generar descendientes hasta llenar la población
        while len(new_population) < population_size:
            parent1, parent2 = selector.select_parents(population)
            # Usar el operador de cruce dinámico:
            child1_config, child2_config = crossover_operator(
                parent1.configuracion, parent2.configuracion, gen, num_generations
            )
            child1_config = swap_mutation(child1_config, mutation_rate=MUTATION_RATE)
            child2_config = swap_mutation(child2_config, mutation_rate=MUTATION_RATE)
            new_population.append(Individuo(child1_config))
            if len(new_population) < population_size:
                new_population.append(Individuo(child2_config))
        
        # Evaluar la nueva población
        new_population, fit_results, elapsed_gen = evaluator.evaluate_population(new_population)
        population = new_population
        
        best_gen = min(population, key=lambda ind: ind.fitness)
        print(f"Mejor fitness en Gen {gen}: {best_gen.fitness}")
        gen_end = time.perf_counter()
        print(f"Tiempo generación {gen}: {gen_end - gen_start:.3f} seg")
        if best_gen.fitness < best_overall.fitness:
            best_overall = best_gen
    
    total_end = time.perf_counter()
    total_elapsed = total_end - total_start
    print("\n=== Resultados finales ===")
    print("Mejor individuo overall:")
    print(f"Configuración: {best_overall.configuracion}")
    print(f"Fitness: {best_overall.fitness}")
    print(f"Tiempo total de ejecución: {total_elapsed:.3f} seg")
    
    return best_overall, orders_csv, config_app

def main():
     # --- Evaluar la configuración inicial ---
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv = os.path.join(script_dir, "ordenes.csv")
    config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
    # Obtenemos la configuración inicial (definida en utils.py)
    initial_config = get_initial_config()
    # Creamos un individuo con esa configuración
    from algoritmo_genetico import Individuo
    init_ind = Individuo(initial_config)
    
    # Creamos un evaluador para evaluar la configuración inicial
    evaluator = FitnessEvaluator(orders_csv, config_app)
    pop_eval, fit_results, elapsed = evaluator.evaluate_population([init_ind])
    fitness_inicial = init_ind.fitness
    print(f"\nFitness de la configuración inicial: {fitness_inicial}")
    
    # Mostrar mapa de calor de la configuración inicial (opcional)
    mostrar_mejor_solucion(init_ind, config_app, orders_csv)

    best_ind, orders_csv, config_app = genetic_algorithm()
    fitness_best = best_ind.fitness
    mostrar_mejor_solucion(best_ind, config_app, orders_csv)

    if fitness_inicial != 0:
        improvement = 100 * (fitness_inicial - fitness_best) / fitness_inicial
        print(f"La eficiencia de picking ha mejorado un {improvement:.2f}% respecto a la configuración inicial.")
    else:
        print("Fitness inicial es 0, no se puede calcular la mejora.")

if __name__ == "__main__":
    main()
