# crossover.py
import random

def pmx_crossover(parent1, parent2):
    """
    Implementa PMX (Partially Mapped Crossover) para permutaciones.
    parent1, parent2: listas de enteros (por ejemplo, [1,2,...,48])
    Retorna dos hijos (offspring1, offspring2).
    """
    size = len(parent1)
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

def cycle_crossover(parent1, parent2):
    """
    Implementa Cycle Crossover para permutaciones.
    Se construyen dos hijos alternando los ciclos encontrados.
    """
    size = len(parent1)
    child1 = [None] * size
    child2 = [None] * size
    cycle_number = 1

    for i in range(size):
        # Si ya se asignó este índice, continuar
        if child1[i] is not None:
            continue
        # Iniciar un ciclo a partir del índice i
        start = i
        current = i
        cycle_indices = []
        while True:
            cycle_indices.append(current)
            current = parent1.index(parent2[current])
            if current == start:
                break
        # Alternar: en ciclos impares, child1 toma de parent1; en pares, child1 toma de parent2.
        if cycle_number % 2 == 1:
            for index in cycle_indices:
                child1[index] = parent1[index]
                child2[index] = parent2[index]
        else:
            for index in cycle_indices:
                child1[index] = parent2[index]
                child2[index] = parent1[index]
        cycle_number += 1

    return child1, child2

def crossover_operator(parent1, parent2, gen, num_generations):
    """
    Selecciona el operador de cruce en función de la generación.
    Hasta el 60% de las generaciones usa PMX; a partir de ese punto usa Cycle Crossover.
    """
    threshold = 0.85 * num_generations
    if gen < threshold:
        return pmx_crossover(parent1, parent2)
    else:
        return cycle_crossover(parent1, parent2)
