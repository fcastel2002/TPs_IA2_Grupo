# crossover.py
import random

def pmx_crossover(parent1, parent2):
    """
    Implementa PMX (Partially Mapped Crossover) para permutaciones.
    
    parent1, parent2: listas de enteros (por ejemplo, [1,2,...,48])
    
    Retorna dos hijos (offspring1, offspring2).
    """
    size = len(parent1)
    # Elegir dos puntos de cruce aleatorios (asegurando que cxpoint1 < cxpoint2)
    cxpoint1 = random.randint(0, size - 2)
    cxpoint2 = random.randint(cxpoint1 + 1, size - 1)
    
    def pmx(parent_a, parent_b):
        child = [None] * size
        # Copiar segmento de parent_a a child
        child[cxpoint1:cxpoint2+1] = parent_a[cxpoint1:cxpoint2+1]
        
        # Para cada posición en el segmento de parent_b:
        for i in range(cxpoint1, cxpoint2+1):
            element = parent_b[i]
            if element not in child:
                pos = i
                # Buscar la posición en parent_b donde el elemento correspondiente de parent_a
                # se encuentre y que no se haya copiado aún.
                while True:
                    element_in_a = parent_a[pos]
                    pos = parent_b.index(element_in_a)
                    if child[pos] is None:
                        child[pos] = element
                        break
        # Rellenar las posiciones restantes con los valores de parent_b
        for i in range(size):
            if child[i] is None:
                child[i] = parent_b[i]
        return child

    offspring1 = pmx(parent1, parent2)
    offspring2 = pmx(parent2, parent1)
    return offspring1, offspring2
