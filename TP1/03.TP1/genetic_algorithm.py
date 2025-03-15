# genetic_algorithm.py
import os
import time
from constantes import CANT_FILAS, CANT_COLUMNAS
from algoritmo_genetico import generar_poblacion
from fitness_evaluator import FitnessEvaluator
from selector import Selector

class GeneticAlgorithm:
    def __init__(self, population_size, orders_csv_path):
        self.population_size = population_size
        self.config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
        self.orders_csv_path = orders_csv_path
        self.population = generar_poblacion(self.population_size)
        self.evaluator = FitnessEvaluator(self.population_size, self.orders_csv_path, self.config_app)
        self.selector = Selector(tournament_size=2)
    
    def evaluate_population(self):
        """
        Evalúa el fitness de cada individuo en paralelo usando FitnessEvaluator.
        Luego asigna el fitness a cada individuo en la población.
        Retorna el diccionario de resultados y el tiempo total de evaluación.
        """
        fitness_results, total_time = self.evaluator.evaluate_population()
        for ind in self.population:
            key = str(ind.configuracion)
            if key in fitness_results:
                ind.fitness = fitness_results[key][0]
            else:
                ind.fitness = float('inf')
        return fitness_results, total_time

    def select_parents(self):
        parent1 = self.selector.tournament_selection(self.population)
        parent2 = self.selector.tournament_selection(self.population)
        return parent1, parent2

    def run(self):
        total_start = time.perf_counter()
        self.evaluate_population()
        total_end = time.perf_counter()
        total_elapsed = total_end - total_start
        
        print("Fitness de la población:")
        for ind in self.population:
            print(f"Configuración: {ind.configuracion} => Fitness: {ind.fitness}")
        print(f"Tiempo total de evaluación: {total_elapsed:.3f} seg")
        
        parent1, parent2 = self.select_parents()
        print("Padres seleccionados:")
        print(f"Padre 1: {parent1.configuracion} => Fitness: {parent1.fitness}")
        print(f"Padre 2: {parent2.configuracion} => Fitness: {parent2.fitness}")
