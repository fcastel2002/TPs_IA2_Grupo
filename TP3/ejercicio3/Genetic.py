import random
import numpy as np
from NeuralNetwork import NeuralNetwork

def select_fittest(population, k=2):
    """
    Tournament selection: elige num_parents = len(population)//2
    usando torneos de tamaño k y devuelve sus índices.
    """
    scores = [d.score for d in population]
    print("» Scores:", scores)
    num_parents = len(population) // 2
    selected = []
    while len(selected) < num_parents:
        # elijo k candidatos al azar
        aspirants = random.sample(range(len(population)), k)
        # gano el de mayor score
        winner = max(aspirants, key=lambda i: population[i].score)
        if winner not in selected:
            selected.append(winner)
    print("» Selected parents indices:", selected)
    return selected

def evolve(parent1, parent2, mutation_rate=0.2, mutation_strength=0.3):
    """
    Cruza de un punto + mutación gaussiana de dos redes, devolviendo
    una NUEVA instancia de NeuralNetwork.
    """
    print(f"» Evolving P{parent1.id} (score={parent1.score}) + "
          f"P{parent2.id} (score={parent2.score})")
    # hijo con misma arquitectura
    child = NeuralNetwork(
        input_size=parent1.input_size,
        hidden_sizes=[parent1.hidden_size],
        output_size=parent1.output_size
    )

    def crossover_and_mutate(a, b):
        fa = a.flatten()
        fb = b.flatten()
        child_flat = np.empty_like(fa)
        # cruce de un punto
        cp = random.randrange(len(fa))
        child_flat[:cp] = fa[:cp]
        child_flat[cp:] = fb[cp:]
        # mutación elemento a elemento
        for i in range(len(child_flat)):
            if random.random() < mutation_rate:
                child_flat[i] += np.random.randn() * mutation_strength
        return child_flat.reshape(a.shape)

    # cruzar y mutar cada parámetro
    child.W1 = crossover_and_mutate(parent1.W1, parent2.W1)
    child.b1 = crossover_and_mutate(parent1.b1, parent2.b1)
    child.W2 = crossover_and_mutate(parent1.W2, parent2.W2)
    child.b2 = crossover_and_mutate(parent1.b2, parent2.b2)

    return child

def updateNetwork(population, elitism=3):
    """
    1) Selección por torneo (select_fittest)
    2) Elitismo: copiar intactos 'elitism' mejores padres
    3) Cruce/mutación para completar la población
    4) Reemplazo in-place de los pesos/biases de cada Dinosaur
    """
    print("\n=== New Generation ===")
    print("Previous scores:", [d.score for d in population])
    pop_size = len(population)

    # 1) Selección
    parent_indices = select_fittest(population)
    parents = [population[i] for i in parent_indices]

    new_networks = []
    # 2) Elitismo: copiamos los mejores intactos
    for idx in parent_indices[:elitism]:
        p = population[idx]
        # clonamos sus parámetros en una nueva red
        elite = NeuralNetwork(
            input_size=p.input_size,
            hidden_sizes=[p.hidden_size],
            output_size=p.output_size
        )
        elite.W1, elite.b1 = np.copy(p.W1), np.copy(p.b1)
        elite.W2, elite.b2 = np.copy(p.W2), np.copy(p.b2)
        new_networks.append(elite)

    # 3) Resto de la población: cruce + mutación
    while len(new_networks) < pop_size:
        p1, p2 = random.sample(parents, 2)
        child = evolve(p1, p2)
        new_networks.append(child)

    # 4) Sustitución in-place
    for dino, net in zip(population, new_networks):
        dino.W1, dino.b1 = net.W1, net.b1
        dino.W2, dino.b2 = net.W2, net.b2

    print("Assigned new networks to dinos:")
    for dino in population:
        print(f"  Dino {dino.id} W1[0,0]={dino.W1.flat[0]:.4f}")
