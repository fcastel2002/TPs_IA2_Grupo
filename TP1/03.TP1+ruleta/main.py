# main.py (versión corregida)

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
from crossover import pmx_crossover, cycle_crossover 

# ========== Parámetros del GA ==========
POPULATION_SIZE = 36      # Número de individuos en la población
NUM_GENERATIONS = 20      # Número de generaciones a ejecutar
MUTATION_RATE = 0.5       # Probabilidad de mutación (intercambio) en cada hijo
TOURNAMENT_SIZE = 3       # Tamaño del torneo para selección
SELECTION_TYPE = "tournament"  # Método de selección: "tournament" o "roulette"
PMX_LIMIT_GENERATION = 10
ELITISM = True            # Activar o desactivar elitismo

class GeneticOptimizer:
    """
    Clase que encapsula la lógica del algoritmo genético para optimización
    de distribución de productos en almacén.
    """
    
    def __init__(self, population_size, num_generations, mutation_rate, 
                 selection_type, tournament_size, elitism):
        """
        Inicializa el optimizador genético con los parámetros especificados.
        
        Args:
            population_size: Tamaño de la población
            num_generations: Número de generaciones a ejecutar
            mutation_rate: Probabilidad de mutación (0.0 a 1.0)
            selection_type: Método de selección ("tournament" o "roulette")
            tournament_size: Tamaño del torneo (solo para selection_type="tournament")
            elitism: Si True, el mejor individuo siempre pasa a la siguiente generación
        """
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.selection_type = selection_type
        self.tournament_size = tournament_size
        self.elitism = elitism
        
        self.config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
        
        # Obtener ruta al archivo de órdenes
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.orders_csv_path = os.path.join(script_dir, "ordenes.csv")
        
        # Inicializar componentes
        self.selector = Selector(selection_type=selection_type, 
                                tournament_size=tournament_size)
        self.evaluator = FitnessEvaluator(self.orders_csv_path, self.config_app)
        
        # Variables para seguimiento del progreso
        self.best_overall = None
        self.population = []
        
    def initialize_population(self):
        """Genera la población inicial de individuos aleatorios."""
        self.population = generar_poblacion(self.population_size)
        
    def evaluate_population(self, population):
        """
        Evalúa el fitness de cada individuo en la población.
        
        Args:
            population: Lista de individuos a evaluar
            
        Returns:
            Lista de individuos con fitness actualizado
        """
        evaluated_population, _, _ = self.evaluator.evaluate_population(population)
        return evaluated_population
    
    def apply_mutation(self, config):
        """
        Aplica mutación por intercambio (swap) a una configuración.
        
        Args:
            config: Lista que representa la configuración del individuo
            
        Returns:
            Nueva configuración después de la mutación
        """
        new_config = config.copy()
        if random.random() < self.mutation_rate:
            i = random.randint(0, len(new_config) - 1)
            j = random.randint(0, len(new_config) - 1)
            new_config[i], new_config[j] = new_config[j], new_config[i]
        return new_config
    
    def create_next_generation(self, generacion_actual):
        """
        Crea una nueva generación de individuos mediante selección, cruce y mutación,
        conservando los 10 mejores individuos de la generación actual (multi-elitismo).
        
        Args:
            generacion_actual: Número de la generación actual
            
        Returns:
            Nueva población (lista de individuos)
        """
        # Actualizar el mejor global si es necesario
        current_best = min(self.population, key=lambda ind: ind.fitness)
        if self.best_overall is None or current_best.fitness < self.best_overall.fitness:
            self.best_overall = current_best
        
        # Crear nueva población
        new_population = []
        
        # Aplicar multi-elitismo si está activado (conservar los 10 mejores)
        if self.elitism:
            # Ordenar la población por fitness (de menor a mayor, ya que menor es mejor)
            sorted_population = sorted(self.population, key=lambda ind: ind.fitness)
            # Determinar cuántos elites conservar (hasta 10, o menos si la población es pequeña)
            num_elites = min(10, len(sorted_population) // 4)  # No más del 25% de la población
            # Añadir los mejores individuos a la nueva población
            new_population.extend(sorted_population[:num_elites])
            print(f"Aplicando multi-elitismo: conservando los {num_elites} mejores individuos")
        
        # Generar descendientes hasta llenar la nueva población
        while len(new_population) < self.population_size:
            # Seleccionar padres
            parent1, parent2 = self.selector.select_parents(self.population)
            
            # Aplicar cruce según la generación actual
            if generacion_actual <= PMX_LIMIT_GENERATION:
                child1_config, child2_config = pmx_crossover(
                    parent1.configuracion, parent2.configuracion)
            else:
                child1_config, child2_config = cycle_crossover(
                    parent1.configuracion, parent2.configuracion)    
            
            # Aplicar mutación
            child1_config = self.apply_mutation(child1_config)
            child2_config = self.apply_mutation(child2_config)
            
            # Crear nuevos individuos
            new_population.append(Individuo(child1_config))
            if len(new_population) < self.population_size:
                new_population.append(Individuo(child2_config))
        
        return new_population
    
    def run(self):
        """
        Ejecuta el algoritmo genético completo.
        
        Returns:
            Tupla (mejor_individuo, ruta_csv, config_app)
        """
        # Registrar tiempo de inicio
        total_start = time.perf_counter()
        
        # Inicializar población
        self.initialize_population()
        
        # Evaluar población inicial
        self.population = self.evaluate_population(self.population)
        
        # Informar al usuario sobre el método de selección
        if self.selection_type == "tournament":
            print(f"Usando selección por torneo (tamaño={self.tournament_size})")
        else:
            print("Usando selección por ruleta")
        
        # Ejecutar ciclo principal de generaciones
        for gen in range(1, self.num_generations + 1):
            gen_start = time.perf_counter()
            print(f"\n=== Generación {gen} ===")
            
            # Crear nueva generación
            new_population = self.create_next_generation(gen)
            
            # Evaluar nueva generación
            self.population = self.evaluate_population(new_population)
            
            # Reportar progreso
            best_gen = min(self.population, key=lambda ind: ind.fitness)
            print(f"Mejor fitness en Gen {gen}: {best_gen.fitness}")
            
            # Actualizar mejor global si es necesario
            if best_gen.fitness < self.best_overall.fitness:
                self.best_overall = best_gen
                
            gen_end = time.perf_counter()
            print(f"Tiempo generación {gen}: {gen_end - gen_start:.3f} seg")
        
        # Calcular tiempo total
        total_end = time.perf_counter()
        total_elapsed = total_end - total_start
        
        # Mostrar resultados finales
        print("\n=== Resultados finales ===")
        print("Mejor individuo overall:")
        print(f"Configuración: {self.best_overall.configuracion}")
        print(f"Fitness: {self.best_overall.fitness}")
        print(f"Tiempo total de ejecución: {total_elapsed:.3f} seg")
        
        return self.best_overall, self.orders_csv_path, self.config_app


# ========== Funciones para visualización de resultados ==========
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

def mostrar_mejor_solucion(best_ind, orders_csv_path, config_app):
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
    tablero.dibujar(True)
    
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

def main():
    """Función principal que configura y ejecuta el algoritmo genético."""
    # Crear y configurar el optimizador genético
    optimizer = GeneticOptimizer(
        population_size=POPULATION_SIZE,
        num_generations=NUM_GENERATIONS,
        mutation_rate=MUTATION_RATE,
        selection_type=SELECTION_TYPE,
        tournament_size=TOURNAMENT_SIZE,
        elitism=ELITISM
    )
    
    # Ejecutar el algoritmo
    best_ind, orders_csv_path, config_app = optimizer.run()
    
    # Visualizar la mejor solución
    mostrar_mejor_solucion(best_ind, orders_csv_path, config_app)

if __name__ == "__main__":
    main()