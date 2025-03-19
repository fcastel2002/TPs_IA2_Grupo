# crossover.py
import random
from typing import List, Tuple, TypeVar, Generic

T = TypeVar('T')  # Tipo genérico para elementos de permutación
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
def cycle_crossover(parent1: List[T], parent2: List[T]) -> Tuple[List[T], List[T]]:
    """
    Implementa CX (Cycle Crossover) para permutaciones.
    
    CX preserva la posición absoluta de los elementos en la permutación.
    Es ideal para problemas donde la posición específica de cada elemento es importante,
    como problemas de asignación o ubicación.
    
    Args:
        parent1: Primera permutación parental.
        parent2: Segunda permutación parental.
        
    Returns:
        Tupla conteniendo dos hijos (offspring1, offspring2).
    """
    size = len(parent1)
    
    # Validar entrada
    if size != len(parent2):
        raise ValueError("Ambos padres deben tener la misma longitud")
    
    # Inicializar hijos
    offspring1 = [None] * size
    offspring2 = [None] * size
    
    # Mapa para acceso rápido a índices
    p2_indices = {val: idx for idx, val in enumerate(parent2)}
    
    # Encontrar ciclos
    cycles = []
    visited = [False] * size
    
    for i in range(size):
        if not visited[i]:
            # Comenzar un nuevo ciclo
            cycle = []
            start_pos = i
            pos = i
            
            while True:
                visited[pos] = True
                cycle.append(pos)
                # Encontrar posición en parent2 del elemento en esta posición de parent1
                value = parent1[pos]
                pos = p2_indices[value]
                
                if pos == start_pos:
                    break
            
            cycles.append(cycle)
    
    # Asignar elementos a los hijos alternando ciclos
    for cycle_idx, cycle in enumerate(cycles):
        for position in cycle:
            if cycle_idx % 2 == 0:  # Ciclo par
                offspring1[position] = parent1[position]
                offspring2[position] = parent2[position]
            else:  # Ciclo impar
                offspring1[position] = parent2[position]
                offspring2[position] = parent1[position]
    
    return offspring1, offspring2