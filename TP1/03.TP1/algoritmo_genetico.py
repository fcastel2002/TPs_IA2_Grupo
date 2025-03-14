import random

class Individuo:
    def __init__(self, configuracion):
        """
        configuracion: lista de 48 enteros (una permutación de 1 a 48)
        """
        self.configuracion = configuracion  
        self.fitness = None  # Se calculará posteriormente

    @classmethod
    def generar_individuo(cls):
        # Genera una permutación aleatoria de los números del 1 al 48.
        config = list(range(1, 49))
        random.shuffle(config)
        return cls(config)

def generar_poblacion(tam_poblacion=10):
    """Genera una lista de 'tam_poblacion' individuos aleatorios."""
    return [Individuo.generar_individuo() for _ in range(tam_poblacion)]

# Ejemplo de uso:
if __name__ == "__main__":
    poblacion = generar_poblacion()
    for i, ind in enumerate(poblacion, start=1):
        print(f"Individuo {i}: {ind.configuracion}")
