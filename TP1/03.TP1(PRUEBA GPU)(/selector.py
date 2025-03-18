# selector.py
import random

class Selector:
    def __init__(self, tournament_size=2):
        """
        Inicializa el selector con el tamaño de torneo.
        Por defecto, torneo binario (tournament_size = 2).
        """
        self.tournament_size = tournament_size

    def tournament_selection(self, population):
        """
        Selecciona un individuo de la población mediante torneo.
        population: lista de individuos (cada uno con un atributo 'fitness').
        Retorna el individuo ganador.
        """
        competitors = random.sample(population, self.tournament_size)
        winner = min(competitors, key=lambda ind: ind.fitness)
        return winner

    def select_parents(self, population):
        """
        Selecciona dos padres usando torneo binario.
        Retorna una tupla (padre1, padre2).
        """
        parent1 = self.tournament_selection(population)
        parent2 = self.tournament_selection(population)
        return parent1, parent2
