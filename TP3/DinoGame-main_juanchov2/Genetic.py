import random
import numpy as np
import copy
from GenomeManager import GenomeManager

# Instancia global del manejador de genomas
genome_manager = GenomeManager()

def updateNetwork(population, generation=1):
    """
    Algoritmo genético reestructurado con distribución de porcentajes:
    - 5% elitismo puro
    - 5% redes nuevas (aleatorias) 
    - 30% clones mutados del mejor
    - 40% clones mutados de padres del top élite
    - 20% crossover entre pares de élites
    """
    
    # Verificar que tenemos una población válida
    if not population or len(population) == 0:
        print("ERROR: Población vacía en updateNetwork")
        return
    
    # Ordenar población por score (mayor a menor)
    population.sort(key=lambda dino: dino.score, reverse=True)
    
    population_size = len(population)
    
    # Calcular tamaños de cada grupo
    elite_size = max(2, int(population_size * 0.1))  # 5% élite
    random_size = max(2, int(population_size * 0.05))  # 5% aleatorios
    best_mutated_size = int(population_size * 0.30)  # 30% clones mutados del mejor
    elite_mutated_size = int(population_size * 0.40)  # 40% clones mutados de élites
    crossover_size = population_size - elite_size - random_size - best_mutated_size - elite_mutated_size  # Resto para crossover
    
    print(f"\n=== GENERACIÓN {generation} ===")
    print(f"Población total: {population_size}")
    print(f"Distribución:")
    print(f"  - Élite: {elite_size} ({elite_size/population_size*100:.1f}%)")
    print(f"  - Aleatorios: {random_size} ({random_size/population_size*100:.1f}%)")
    print(f"  - Clones mutados del mejor: {best_mutated_size} ({best_mutated_size/population_size*100:.1f}%)")
    print(f"  - Clones mutados de élites: {elite_mutated_size} ({elite_mutated_size/population_size*100:.1f}%)")
    print(f"  - Crossover entre élites: {crossover_size} ({crossover_size/population_size*100:.1f}%)")
    
    # Mostrar los mejores scores
    print("Top 5 scores:")
    for i in range(min(5, len(population))):
        print(f"  {i+1}. ID {population[i].id}: {population[i].score} puntos")
    
    best_score = population[0].score
    
    # Guardar la población entera
    genome_manager.save_elite_genomes(population, generation, best_score)
    
    # Seleccionar élite extendida para operaciones genéticas
    elite_extended_size = max(elite_size, int(population_size * 0.15))  # Al menos 15% para selección
    elite_extended = population[:elite_extended_size]
    
    current_index = 0
    
    # 1. ELITISMO PURO (5%)
    print(f"\n1. Preservando élite: {elite_size} individuos")
    for i in range(elite_size):
        elite_genome = population[i].get_genome()
        population[current_index].set_genome(elite_genome)
        population[current_index].resetStatus(genetico=True)
        current_index += 1
    
    # 2. REDES NUEVAS ALEATORIAS (5%)
    print(f"2. Generando redes aleatorias: {random_size} individuos")
    for i in range(random_size):
        random_genome = generate_random_genome()
        population[current_index].set_genome(random_genome)
        population[current_index].resetStatus(genetico=True)
        current_index += 1
    
    # 3. CLONES MUTADOS DEL MEJOR (30%)
    print(f"3. Generando clones mutados del mejor: {best_mutated_size} individuos")
    best_genome = population[0].get_genome()
    for i in range(best_mutated_size):
        mutated_genome = create_mutated_clone(best_genome, mutation_strength="suave")
        population[current_index].set_genome(mutated_genome)
        population[current_index].resetStatus(genetico=True)
        current_index += 1
    
    # 4. CLONES MUTADOS DE ÉLITES ALEATORIOS (40%)
    print(f"4. Generando clones mutados de élites: {elite_mutated_size} individuos")
    for i in range(elite_mutated_size):
        # Seleccionar un padre aleatoriamente del top élite
        parent = random.choice(elite_extended)
        mutated_genome = create_mutated_clone(parent.get_genome(), mutation_strength="suave")
        population[current_index].set_genome(mutated_genome)
        population[current_index].resetStatus(genetico=True)
        current_index += 1
    
    # 5. CROSSOVER ENTRE PARES DE ÉLITES (20%)
    print(f"5. Generando crossover entre élites: {crossover_size} individuos")
    for i in range(crossover_size):
        # Seleccionar dos padres diferentes del élite extendido
        parent1 = random.choice(elite_extended)
        parent2 = random.choice(elite_extended)
        while parent2 == parent1 and len(elite_extended) > 1:
            parent2 = random.choice(elite_extended)
        
        child_genome = create_crossover_genome(parent1, parent2)
        population[current_index].set_genome(child_genome)
        population[current_index].resetStatus(genetico=True)
        current_index += 1
    
    print(f"\nPoblación regenerada completamente: {current_index} individuos")
    print(f"Mejor score: {best_score}")
    print("=" * 60)

def generate_random_genome():
    """Genera un genoma completamente aleatorio"""
    genome = []
    
    # Conexiones input -> hidden (aleatorias, no todas)
    for input_node in range(6):  # 6 entradas
        for hidden_node in range(6):  # 6 neuronas ocultas
            if random.random() < 0.3:  # 30% probabilidad de conexión
                genome.append({
                    'type': 'input_hidden',
                    'from': input_node,
                    'to': hidden_node,
                    'weight': random.gauss(0, 0.5)
                })
    
    # Conexiones hidden -> output (aleatorias, no todas)
    for hidden_node in range(6):
        for output_node in range(3):  # 3 salidas
            if random.random() < 0.4:  # 40% probabilidad de conexión
                genome.append({
                    'type': 'hidden_output',
                    'from': hidden_node,
                    'to': output_node,
                    'weight': random.gauss(0, 0.5)
                })
    
    # Biases para neuronas ocultas
    for hidden_node in range(6):
        if random.random() < 0.5:  # 50% probabilidad de bias
            genome.append({
                'type': 'bias_hidden',
                'neuron': hidden_node,
                'weight': random.gauss(0, 0.3)
            })
    
    # Biases para neuronas de salida
    for output_node in range(3):
        if random.random() < 0.5:  # 50% probabilidad de bias
            genome.append({
                'type': 'bias_output',
                'neuron': output_node,
                'weight': random.gauss(0, 0.3)
            })
    
    return genome

def create_mutated_clone(parent_genome, mutation_strength="suave"):
    """
    Crea un clon mutado de un genoma padre
    mutation_strength: "suave" o "fuerte"
    """
    clone_genome = copy.deepcopy(parent_genome)
    
    # Definir parámetros de mutación según la intensidad
    if mutation_strength == "suave":
        mutation_rate = 0.1  # 10% de genes se mutan
        weight_mutation_std = 0.05  # Desviación estándar pequeña
        bias_mutation_std = 0.03
        add_connection_prob = 0.02  # 2% probabilidad de agregar conexión
        remove_connection_prob = 0.01  # 1% probabilidad de quitar conexión
    else:  # "fuerte"
        mutation_rate = 0.3  # 30% de genes se mutan
        weight_mutation_std = 0.15  # Desviación estándar mayor
        bias_mutation_std = 0.08
        add_connection_prob = 0.05  # 5% probabilidad de agregar conexión
        remove_connection_prob = 0.03  # 3% probabilidad de quitar conexión
    
    # Mutar pesos existentes
    for gene in clone_genome:
        if random.random() < mutation_rate:
            if gene['type'] in ['input_hidden', 'hidden_output']:
                # Mutación de conexión
                mutation = random.gauss(0, weight_mutation_std)
                gene['weight'] += mutation
            elif gene['type'] in ['bias_hidden', 'bias_output']:
                # Mutación de bias
                mutation = random.gauss(0, bias_mutation_std)
                gene['weight'] += mutation
    
    # Mutación estructural: agregar nueva conexión
    if random.random() < add_connection_prob:
        add_random_connection(clone_genome)
    
    # Mutación estructural: eliminar conexión aleatoria
    connections = [gene for gene in clone_genome if gene['type'] in ['input_hidden', 'hidden_output']]
    if len(connections) > 5 and random.random() < remove_connection_prob:
        remove_random_connection(clone_genome)
    
    return clone_genome

def create_crossover_genome(parent1, parent2):
    """
    Crea un genoma hijo mediante crossover de dos padres
    Usa crossover uniforme con mutación ligera
    """
    genome1 = parent1.get_genome()
    genome2 = parent2.get_genome()
    
    # Diccionarios para organizar genes por clave
    genes1 = {get_gene_key(gene): gene for gene in genome1}
    genes2 = {get_gene_key(gene): gene for gene in genome2}
    
    # Obtener todas las claves únicas
    all_keys = set(genes1.keys()) | set(genes2.keys())
    
    child_genome = []
    
    for key in all_keys:
        gene1 = genes1.get(key)
        gene2 = genes2.get(key)
        
        if gene1 and gene2:
            # Ambos padres tienen este gen: crossover uniforme
            if random.random() < 0.5:
                child_gene = copy.deepcopy(gene1)
            else:
                child_gene = copy.deepcopy(gene2)
                
            # Pequeña mutación en el peso
            if random.random() < 0.05:  # 5% probabilidad
                if child_gene['type'] in ['input_hidden', 'hidden_output']:
                    child_gene['weight'] += random.gauss(0, 0.02)
                elif child_gene['type'] in ['bias_hidden', 'bias_output']:
                    child_gene['weight'] += random.gauss(0, 0.01)
                    
        elif gene1:
            # Solo padre1 tiene este gen: heredar con probabilidad
            if random.random() < 0.7:  # 70% probabilidad
                child_gene = copy.deepcopy(gene1)
            else:
                continue
                
        elif gene2:
            # Solo padre2 tiene este gen: heredar con probabilidad
            if random.random() < 0.7:  # 70% probabilidad
                child_gene = copy.deepcopy(gene2)
            else:
                continue
        
        child_genome.append(child_gene)
    
    return child_genome

def initialize_population_with_saved_genomes(population, archivo=None):
    """Inicializa la población con genomas guardados si existen"""
    if archivo:
        genome_manager.filename = archivo
    elite_genomes, metadata = genome_manager.load_elite_genomes()
    
    if elite_genomes:
        applied_count = genome_manager.apply_elite_genomes_to_population(population, elite_genomes)
        print(f"\n🧬 CONTINUANDO EVOLUCIÓN 🧬")
        print(f"Genomas aplicados: {applied_count}")
        print(f"Generación inicial: {metadata.get('total_generations', 0) + 1}")
        print(f"Mejor score histórico: {metadata.get('best_score_ever', 0)}")
        return metadata.get('total_generations', 0)
    else:
        print("🆕 INICIANDO NUEVA EVOLUCIÓN 🆕")
        return 1

def get_gene_key(gene):
    """Crea una clave única para identificar un gen"""
    if gene['type'] == 'input_hidden':
        return f"ih_{gene['from']}_{gene['to']}"
    elif gene['type'] == 'hidden_output':
        return f"ho_{gene['from']}_{gene['to']}"
    elif gene['type'] == 'bias_hidden':
        return f"bh_{gene['neuron']}"
    elif gene['type'] == 'bias_output':
        return f"bo_{gene['neuron']}"

def add_random_connection(genome):
    """Agrega una nueva conexión aleatoria al genoma"""
    existing_keys = {get_gene_key(gene) for gene in genome}
    
    # Intentar agregar conexión input->hidden
    for _ in range(20):
        from_node = random.randint(0, 5)
        to_node = random.randint(0, 5)
        key = f"ih_{from_node}_{to_node}"
        
        if key not in existing_keys:
            new_gene = {
                'type': 'input_hidden',
                'from': from_node,
                'to': to_node,
                'weight': random.gauss(0, 0.3)
            }
            genome.append(new_gene)
            return
    
    # Si no se pudo agregar input->hidden, intentar hidden->output
    for _ in range(20):
        from_node = random.randint(0, 5)
        to_node = random.randint(0, 2)
        key = f"ho_{from_node}_{to_node}"
        
        if key not in existing_keys:
            new_gene = {
                'type': 'hidden_output',
                'from': from_node,
                'to': to_node,
                'weight': random.gauss(0, 0.3)
            }
            genome.append(new_gene)
            return

def remove_random_connection(genome):
    """Elimina una conexión aleatoria del genoma"""
    connections = [gene for gene in genome if gene['type'] in ['input_hidden', 'hidden_output']]
    if connections:
        gene_to_remove = random.choice(connections)
        genome.remove(gene_to_remove)