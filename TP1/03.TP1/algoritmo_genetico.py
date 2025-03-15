# algoritmo_genetico.py
import random

class Individuo:
    def __init__(self, configuracion):
        self.configuracion = configuracion  # Lista de 48 enteros (por ejemplo, [1, 2, 3, ..., 48] en orden aleatorio)
        self.fitness = None  # Se asignará luego tras la evaluación

    @classmethod
    def generar_individuo(cls):
        config = list(range(1, 49))
        random.shuffle(config)
        return cls(config)

def generar_poblacion(tam_poblacion=10):
    """Genera una lista de 'tam_poblacion' individuos aleatorios."""
    return [Individuo.generar_individuo() for _ in range(tam_poblacion)]
