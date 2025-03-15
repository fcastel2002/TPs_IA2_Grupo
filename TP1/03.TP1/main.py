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
from crossover import pmx_crossover

# --- Operador de mutación por intercambio (swap) ---
def swap_mutation(config, mutation_rate=0.1):
    new_config = config.copy()
    if random.random() < mutation_rate:
        i = random.randint(0, len(new_config) - 1)
        j = random.randint(0, len(new_config) - 1)
        new_config[i], new_config[j] = new_config[j], new_config[i]
    return new_config


# --- Función para calcular la frecuencia de cada producto a partir de orders.csv ---
def compute_frequencies(orders):
    freq = {}
    for order in orders:
        for prod in order:
            try:
                p = int(prod)
                freq[p] = freq.get(p, 0) + 1
            except:
                continue
    return freq

# --- Función para mapear la frecuencia a un color (gradiente de azul a rojo) ---
def get_heat_color(freq_value, max_freq):
    if max_freq == 0:
        return (0, 0, 255)
    # r aumenta con la frecuencia; b disminuye
    r = int(255 * freq_value / max_freq)
    b = 255 - r
    return (r, 0, b)

# ========== Función para dibujar la leyenda de colores ==========
def draw_color_legend(screen, x, y, width, height, freq_min, freq_max, font):
    """
    Dibuja una leyenda vertical con un gradiente de azul (frecuencia baja) a rojo (frecuencia alta).
    - screen: superficie de Pygame donde se dibuja
    - x, y: posición (superior izquierda) de la leyenda
    - width, height: tamaño del recuadro para la leyenda
    - freq_min, freq_max: valores mínimo y máximo de frecuencia para etiquetar
    - font: fuente de texto para escribir las etiquetas
    """
    # Dibujamos un gradiente vertical de 0 a height
    for i in range(height):
        # ratio indica el nivel de la posición dentro de la altura total
        ratio = i / float(height)
        # ratio = 0 -> azul puro, ratio = 1 -> rojo puro
        r = int(255 * ratio)
        b = 255 - r
        color = (r, 0, b)
        pygame.draw.line(screen, color, (x, y + i), (x + width, y + i))
    
    # Etiquetar frecuencia mínima (abajo)
    freq_min_text = font.render(f"{freq_min} (bajo)", True, (0, 0, 0))
    screen.blit(freq_min_text, (x + width + 5, y + height - freq_min_text.get_height()))
    
    # Etiquetar frecuencia máxima (arriba)
    freq_max_text = font.render(f"{freq_max} (alto)", True, (0, 0, 0))
    screen.blit(freq_max_text, (x + width + 5, y))

# --- Función para visualizar el tablero con el mapa de calor ---
def mostrar_mejor_solucion(best_ind, config_app, orders_csv_path):
    # Re-inicializamos Pygame en modo visible
    pygame.display.quit()
    os.environ.pop("SDL_VIDEODRIVER", None)  # Remover dummy
    pygame.display.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mejor Solución con Mapa de Calor")
    
    # Crear la aplicación y el tablero
    from aplicacion import Aplicacion  # Se importa aquí para que se use el driver visible
    app = Aplicacion(config_app)
    app.llenar_tablero()            # construye estructura interna del tablero (define que indices son estanterias y cual corresponde a casilla carga "C")
    tablero = app.tablero           # se asigna a variable local tablero, el atributo tablero (que es la creacion de objeto tablero) del objeto app (revisar Aplicacion para entender)
    # Asignar la configuración del mejor individuo
    tablero.asignar_configuracion(best_ind.configuracion)  # se pasa configuracion de mejor individuo. 
    
    # Calcular frecuencias a partir del archivo de órdenes
    orders = []
    with open(orders_csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            orders.append(row)
    freq = compute_frequencies(orders)
    max_freq = max(freq.values()) if freq else 1
    min_freq = min(freq.values()) if freq else 0
    
    # Actualizar el color de cada casillero de estantería según la frecuencia del producto
    for cas in tablero.casilleros:
        if not cas.libre and cas.caracter != "C" and cas.caracter != "":
            try:
                prod = int(cas.caracter)
                cas.color = get_heat_color(freq.get(prod, 0), max_freq)
            except:
                pass
    
    # Dibujar el tablero con la nueva configuración y el mapa de calor
    tablero.dibujar(screen)
    # ========== Dibujar la leyenda ==========
    font = pygame.font.SysFont("arial", 16)
    legend_x = WINDOW_WIDTH - 70  # posición X (por ejemplo, a la derecha)
    legend_y = 50                 # posición Y
    legend_width = 20
    legend_height = 100
    
    draw_color_legend(screen, legend_x, legend_y, legend_width, legend_height, min_freq, max_freq, font)

    pygame.display.flip()
    
    print("Mostrando la mejor solución con mapa de calor. Cierre la ventana para finalizar.")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

# --- Ciclo principal del GA ---
def genetic_algorithm():
    population_size = 40
    num_generations = 80
    config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv = os.path.join(script_dir, "ordenes.csv")
    
    # Inicializar población
    population = generar_poblacion(population_size)
    selector = Selector(tournament_size=2)
    
    # Para medir tiempo total de GA
    total_start = time.perf_counter()
    best_overall = None
    
    # Evaluar la población inicial
    evaluator = FitnessEvaluator(orders_csv, config_app)
    population, fitness_results, elapsed = evaluator.evaluate_population(population)
    best_overall = min(population, key=lambda ind: ind.fitness)
    # Asignar fitness a cada individuo ya se hizo en evaluate_population

    for gen in range(1, num_generations + 1):
        gen_start = time.perf_counter()
        print(f"\n=== Generación {gen} ===")
        
        # Selección, crossover y mutación para formar la nueva población:
        new_population = []
        # Elitismo: conservar el mejor individuo
        best = min(population, key=lambda ind: ind.fitness)
        if best.fitness < best_overall.fitness:
            best_overall = best
        new_population.append(best)
        
        while len(new_population) < population_size:
            parent1, parent2 = selector.select_parents(population)
            child1_config, child2_config = pmx_crossover(parent1.configuracion, parent2.configuracion)
            child1_config = swap_mutation(child1_config, mutation_rate=0.1)
            child2_config = swap_mutation(child2_config, mutation_rate=0.1)
            new_population.append(Individuo(child1_config))
            if len(new_population) < population_size:
                new_population.append(Individuo(child2_config))
        
        # Evaluar la nueva población en paralelo
        new_population, fit_results, elapsed_gen = evaluator.evaluate_population(new_population)
        population = new_population
        
        best = min(population, key=lambda ind: ind.fitness)
        print(f"Mejor fitness en Gen {gen}: {best.fitness}")
        gen_end = time.perf_counter()
        print(f"Tiempo generación {gen}: {gen_end - gen_start:.3f} seg")
    
    total_end = time.perf_counter()
    total_elapsed = total_end - total_start
    print("\n=== Resultados finales ===")
    print("Mejor individuo overall:")
    print(f"Configuración: {best_overall.configuracion}")
    print(f"Fitness: {best_overall.fitness}")
    print(f"Tiempo total de ejecución: {total_elapsed:.3f} seg")
    return best_overall, orders_csv, config_app

def evaluate_population_list(population, orders_csv, config_app):
    # Leer órdenes desde el CSV
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv_path = os.path.join(script_dir, "ordenes.csv")
    orders = []
    with open(orders_csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            orders.append(row)
    # Evaluar la población (FitnessEvaluator devuelve 3 valores)
    fitness_results, total_elapsed, pop = FitnessEvaluator(population_size=len(population),
                                                           orders_csv_path=orders_csv_path,
                                                           config_app=config_app).evaluate_population()
    return pop, fitness_results


def main():
    best_overall, orders_csv, config_app = genetic_algorithm()
    # Visualizar la mejor solución con mapa de calor:
    mostrar_mejor_solucion(best_overall, config_app, orders_csv)

if __name__ == "__main__":
    main()
