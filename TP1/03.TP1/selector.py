# selector.py
import random

class Selector:
    def __init__(self, tournament_size=2):
        """
        Inicializa el selector con el tamaño de torneo.
        Por defecto, torneo binario (tournament_size = 2).
        """
        self.tournament_size = tournament_size

    def weighted_selection(self, population):
        """
        Selecciona un individuo de la población usando una selección ponderada.
        Calcula un peso para cada individuo basado en la diferencia entre
        el peor fitness y el fitness del individuo, de modo que los individuos
        con fitness más bajo tengan un mayor peso.
        """
        # Determinar el peor fitness (máximo) de la población
        max_fitness = max(ind.fitness for ind in population)
        # Se utiliza un pequeño epsilon para evitar que el peso sea 0.
        epsilon = 1e-6
        weights = [max_fitness - ind.fitness + epsilon for ind in population]
        # random.choices selecciona con probabilidad proporcional a los pesos.
        return random.choices(population, weights=weights, k=1)[0]

    def tournament_selection(self, population):
        """
        Selecciona un individuo de la población mediante torneo.
        En lugar de elegir competidores de forma uniforme, se utiliza la selección ponderada.
        """
        competitors = [self.weighted_selection(population) for _ in range(self.tournament_size)]
        # Se elige el individuo con menor fitness entre los competidores
        winner = min(competitors, key=lambda ind: ind.fitness)
        return winner

    def select_parents(self, population):
        """
        Selecciona dos padres usando torneo ponderado.
        Retorna una tupla (padre1, padre2).
        """
        parent1 = self.tournament_selection(population)
        parent2 = self.tournament_selection(population)
        return parent1, parent2
