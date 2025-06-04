# Genetic.py

import random
import numpy as np
from NeuralNetwork import NeuralNetwork

def select_fittest(population, k=3):
    """
    Selecciona los mejores individuos mediante torneo.
    Devuelve la lista de índices de los padres seleccionados.
    """
    num_parents = len(population) // 2
    selected = []

    # Torneo: cada vez, escoger k aspirantes al azar y quedarse con el de mayor score
    while len(selected) < num_parents:
        aspirants = random.sample(range(len(population)), k)
        winner = max(aspirants, key=lambda i: population[i].score)
        if winner not in selected:
            selected.append(winner)

    return selected


def evolve(parent1, parent2=None, mutation_type='mild'):
    """
    Genera un nuevo juego de pesos/biases a partir de parent1 (y opcionalmente de parent2).
    Si solo se pasa parent1, se aplica únicamente mutación (clon con mutación).
    Si se pasan parent1 y parent2, se hace cruce (crossover) seguido de mutación.

    Parámetros de mutación según mutation_type:
      - 'mild' : prob_mutación = 0.1, fuerza_mu = 0.03
      - 'hard' : prob_mutación = 0.2, fuerza_mu = 0.07
      - 'none' : no hay mutación (solo cruce/al promediar)
    """

    # Definir parámetros según tipo
    if mutation_type == 'mild':
        prob_mut = 0.10
        mag_mut = 0.03
    elif mutation_type == 'hard':
        prob_mut = 0.20
        mag_mut = 0.07
    else:
        prob_mut = 0.0
        mag_mut = 0.0

    # Extraer pesos/biases del primer padre
    W1_p1 = parent1.W1.copy()
    b1_p1 = parent1.b1.copy()
    W2_p1 = parent1.W2.copy()
    b2_p1 = parent1.b2.copy()

    if parent2 is None:
        # Mutación directa de parent1
        W1_child = W1_p1.copy()
        b1_child = b1_p1.copy()
        W2_child = W2_p1.copy()
        b2_child = b2_p1.copy()
    else:
        # Cruce: obtener pesos de ambos padres
        W1_p2 = parent2.W1
        b1_p2 = parent2.b1
        W2_p2 = parent2.W2
        b2_p2 = parent2.b2

        # Podemos combinar por máscara aleatoria
        mask_W1 = np.random.rand(*W1_p1.shape) < 0.5
        mask_b1 = np.random.rand(*b1_p1.shape) < 0.5
        mask_W2 = np.random.rand(*W2_p1.shape) < 0.5
        mask_b2 = np.random.rand(*b2_p1.shape) < 0.5

        W1_child = np.where(mask_W1, W1_p1, W1_p2)
        b1_child = np.where(mask_b1, b1_p1, b1_p2)
        W2_child = np.where(mask_W2, W2_p1, W2_p2)
        b2_child = np.where(mask_b2, b2_p1, b2_p2)

    # Aplicar mutación (ruido gaussiano) a cada matriz/vector por separado
    if prob_mut > 0:
        # Para W1
        mutation_mask_W1 = np.random.rand(*W1_child.shape) < prob_mut
        noise_W1 = np.random.randn(*W1_child.shape) * mag_mut
        W1_child = W1_child + (mutation_mask_W1 * noise_W1)

        # Para b1
        mutation_mask_b1 = np.random.rand(*b1_child.shape) < prob_mut
        noise_b1 = np.random.randn(*b1_child.shape) * mag_mut
        b1_child = b1_child + (mutation_mask_b1 * noise_b1)

        # Para W2
        mutation_mask_W2 = np.random.rand(*W2_child.shape) < prob_mut
        noise_W2 = np.random.randn(*W2_child.shape) * mag_mut
        W2_child = W2_child + (mutation_mask_W2 * noise_W2)

        # Para b2
        mutation_mask_b2 = np.random.rand(*b2_child.shape) < prob_mut
        noise_b2 = np.random.randn(*b2_child.shape) * mag_mut
        b2_child = b2_child + (mutation_mask_b2 * noise_b2)

    return W1_child, b1_child, W2_child, b2_child


def updateNetwork(population):
    """
    Aplica un paso de evolución genética sobre la lista 'population', que contiene objetos Dinosaur.
    Se basa en:
      - 5% elitismo directo (copiar mejores)
      - 5% nuevos aleatorios
      - 30% mutaciones a partir del mejor
      - 40% mutaciones a partir de padres al azar entre el top 5%
      - 20% cruces entre pares del top 5%
    """
    N = len(population)
    if N == 0:
        return

    # 1) Ordenar la población por score descendente
    sorted_pop = sorted(population, key=lambda d: d.score, reverse=True)

    # 2) Calcular cantidades
    elitism_count = max(1, int(0.05 * N))
    new_random_count = max(1, int(0.05 * N))
    mutate_best_count = int(0.30 * N)
    mutate_rand_count = int(0.40 * N)

    # El resto será crossover para completar N individuos
    assigned = elitism_count + new_random_count + mutate_best_count + mutate_rand_count
    crossover_count = N - assigned
    if crossover_count < 0:
        # Ajustar para que no se pase
        crossover_count = max(0, N - (elitism_count + new_random_count + mutate_best_count + mutate_rand_count))

    new_population = []

    # 3) 5% Elitismo: copiamos directamente los mejores cerebros
    for i in range(elitism_count):
        parent = sorted_pop[i]
        # Crear nuevo individuo con mismo color/autoplay (y luego reasignar id)
        child = type(parent)(parent.id, parent.color, parent.autoPlay)
        # Copiar pesos y bias exactamente
        child.W1 = parent.W1.copy()
        child.b1 = parent.b1.copy()
        child.W2 = parent.W2.copy()
        child.b2 = parent.b2.copy()
        new_population.append(child)

    # 4) 5% Nuevos aleatorios: redes completamente nuevas
    for _ in range(new_random_count):
        ref = sorted_pop[0]
        child = type(ref)(ref.id, ref.color, ref.autoPlay)
        # Su constructor inicializa la red con valores aleatorios
        new_population.append(child)

    # 5) 30% Mutaciones del mejor individuo (mejor = índice 0 en sorted_pop)
    best_parent = sorted_pop[0]
    for _ in range(mutate_best_count):
        child = type(best_parent)(best_parent.id, best_parent.color, best_parent.autoPlay)
        W1_new, b1_new, W2_new, b2_new = evolve(best_parent, mutation_type='mild')
        child.W1, child.b1, child.W2, child.b2 = W1_new, b1_new, W2_new, b2_new
        new_population.append(child)

    # 6) 40% Mutaciones a partir de un padre aleatorio entre los top elitism_count
    top_parents = sorted_pop[:elitism_count]
    for _ in range(mutate_rand_count):
        parent = random.choice(top_parents)
        child = type(parent)(parent.id, parent.color, parent.autoPlay)
        W1_new, b1_new, W2_new, b2_new = evolve(parent, mutation_type='mild')
        child.W1, child.b1, child.W2, child.b2 = W1_new, b1_new, W2_new, b2_new
        new_population.append(child)

    # 7) 20% Crossover entre pares de padres tomados del top elitism_count
    for _ in range(crossover_count):
        p1, p2 = random.sample(top_parents, 2)
        child = type(p1)(p1.id, p1.color, p1.autoPlay)
        W1_new, b1_new, W2_new, b2_new = evolve(p1, p2, mutation_type='mild')
        child.W1, child.b1, child.W2, child.b2 = W1_new, b1_new, W2_new, b2_new
        new_population.append(child)

    # 8) Asegurar que tenemos exactamente N individuos
    # Si por redondeo nos faltan, completamos con clones mutados del mejor
    while len(new_population) < N:
        child = type(best_parent)(best_parent.id, best_parent.color, best_parent.autoPlay)
        W1_new, b1_new, W2_new, b2_new = evolve(best_parent, mutation_type='mild')
        child.W1, child.b1, child.W2, child.b2 = W1_new, b1_new, W2_new, b2_new
        new_population.append(child)

    # Si nos sobraron, cortamos el excedente
    new_population = new_population[:N]

    # 9) Reasignar IDs secuenciales y reemplazar población original
    for idx, child in enumerate(new_population):
        child.id = idx
        population[idx] = child
