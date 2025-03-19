# selector.py
import random

class Selector:
    """
    Clase que proporciona diferentes estrategias de selección para algoritmos genéticos.
    """
    def __init__(self, selection_type="tournament", tournament_size=2):
        """
        Inicializa el selector con el método especificado.
        
        Args:
            selection_type: Método de selección ("tournament" o "roulette")
            tournament_size: Tamaño del torneo (solo relevante para torneo)
        """
        self.selection_type = selection_type
        self.tournament_size = tournament_size
    
    def tournament_selection(self, population):
        """
        Selecciona un individuo de la población mediante torneo.
        
        Args:
            population: Lista de individuos (cada uno con atributo 'fitness')
            
        Returns:
            El individuo ganador.
        """
        competitors = random.sample(population, self.tournament_size)
        winner = min(competitors, key=lambda ind: ind.fitness)
        return winner
    
    def roulette_selection(self, population):
        """
        Selecciona un individuo mediante ruleta (probabilidad proporcional al fitness inverso).
        
        Args:
            population: Lista de individuos (cada uno con atributo 'fitness')
            
        Returns:
            El individuo seleccionado.
        """
        # Para problemas de minimización, transformamos los fitness
        # (menor fitness = mejor individuo = mayor probabilidad)
        total_inverse_fitness = sum(1.0/(ind.fitness + 1e-10) for ind in population)
        
        # Generar punto de selección aleatorio
        selection_point = random.uniform(0, total_inverse_fitness)
        
        # Encontrar el individuo correspondiente
        current = 0
        for ind in population:
            current += 1.0/(ind.fitness + 1e-10)
            if current >= selection_point:
                return ind
        
        # Por seguridad, si hay algún error numérico
        return population[-1]
    
    def select(self, population):
        """
        Selecciona un individuo usando el método configurado.
        
        Args:
            population: Lista de individuos
            
        Returns:
            Un individuo seleccionado
        """
        if self.selection_type == "tournament":
            return self.tournament_selection(population)
        elif self.selection_type == "roulette":
            return self.roulette_selection(population)
        else:
            raise ValueError(f"Método de selección no soportado: {self.selection_type}")
    
    def select_parents(self, population):
        """
        Selecciona dos padres usando el método configurado.
        
        Args:
            population: Lista de individuos
            
        Returns:
            Tupla (parent1, parent2)
        """
        parent1 = self.select(population)
        parent2 = self.select(population)
        return parent1, parent2