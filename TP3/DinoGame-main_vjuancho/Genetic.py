import random
import numpy as np
import copy
from GenomeManager import GenomeManager

# Instancia global del manejador de genomas
genome_manager = GenomeManager()

def updateNetwork(population, generation=1):
    # ===================== ESTA FUNCIÓN RECIBE UNA POBLACIÓN A LA QUE SE DEBEN APLICAR MECANISMOS DE SELECCIÓN, =================
    # ===================== CRUCE Y MUTACIÓN. LA ACTUALIZACIÓN DE LA POBLACIÓN SE APLICA EN LA MISMA VARIABLE ====================
    
    # Verificar que tenemos una población válida
    if not population or len(population) == 0:
        print("ERROR: Población vacía en updateNetwork")
        return
    
    # Ordenar población por score (mayor a menor)
    population.sort(key=lambda dino: dino.score, reverse=True)
    
    # Calcular número de individuos de élite (5% mínimo 2, máximo 20)
    elite_size = max(2, min(20, int(len(population) * 0.15)))
    
    print(f"\n=== GENERACIÓN {generation} ===")
    print(f"Población total: {len(population)}")
    print(f"Élite seleccionada: {elite_size} individuos")
    
    # Mostrar los mejores scores
    print("Top 5 scores:")
    for i in range(min(5, len(population))):
        print(f"  {i+1}. ID {population[i].id}: {population[i].score} puntos")
    
    # Extraer élite
    elite_dinosaurs = population[:elite_size]
    best_score = elite_dinosaurs[0].score
    
    # Guardar genomas de élite
    genome_manager.save_elite_genomes(elite_dinosaurs, generation, best_score)
    
    # Seleccionar padres de toda la población (no solo élite)
    parents = select_fittest(population)
    
    print(f"Padres seleccionados: {len(parents)} individuos")
    
    # Preservar genomas de élite (elitismo múltiple)
    for i in range(elite_size):
        elite_genome = elite_dinosaurs[i].get_genome()
        population[i].set_genome(elite_genome)
        population[i].resetStatus(genetico=True)
    
    # Generar el resto de la población mediante cruce y mutación
    for i in range(elite_size, len(population)):
        # Seleccionar dos padres (pueden ser de la élite o no)
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        
        # Crear descendiente mediante cruce
        child_genome = create_child_genome(parent1, parent2)
        population[i].set_genome(child_genome)
        population[i].resetStatus(genetico=True)
    
    print(f"Élite preservada: {elite_size}, Nuevos individuos: {len(population) - elite_size}")
    print(f"Mejor score: {best_score}")
    print("=" * 50)
    # =============================================================================================================================

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
        return metadata.get('total_generations', 0)# + 1
    else:
        print("🆕 INICIANDO NUEVA EVOLUCIÓN 🆕")
        return 1

def select_fittest(population):
    # ===================== FUNCIÓN DE SELECCIÓN MEJORADA =====================
    # Selección por probabilidades ponderadas basada en el score
    # Pero incluyendo más diversidad genética
    
    # Calcular scores positivos
    scores = [max(1, dino.score) for dino in population]  # Mínimo 1 para evitar división por 0
    total_score = sum(scores)
    
    # Calcular probabilidades con diversidad
    probabilities = []
    for i, score in enumerate(scores):
        # Probabilidad base por score
        base_prob = score / total_score
        
        # Bonus por diversidad (dinosaurios con menos conexiones)
        connections = population[i].count_connections()
        diversity_bonus = 1.0 / max(1, connections / 20)  # Favor a redes más simples
        
        # Probabilidad final
        final_prob = base_prob * (1 + 0.1 * diversity_bonus)
        probabilities.append(final_prob)
    
    # Normalizar probabilidades
    total_prob = sum(probabilities)
    probabilities = [p / total_prob for p in probabilities]
    
    # Seleccionar padres
    num_parents = max(3, len(population) // 4)  # Al menos 3 padres, máximo 1/4 de la población
    parents = []
    
    for _ in range(num_parents):
        # Ruleta de selección
        rand = random.random()
        cumulative_prob = 0
        
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if rand <= cumulative_prob:
                parents.append(population[i])
                break
    
    # Asegurar diversidad mínima
    if len(set(parents)) < 2:
        parents = population[:max(2, num_parents)]
    
    return parents
    # ================================================================

def create_child_genome(parent1, parent2):
    """Crea un genoma hijo a partir de dos padres"""
    # Obtener genomas de los padres
    genome1 = parent1.get_genome()
    genome2 = parent2.get_genome()
    
    # === CRUCE MEJORADO ===
    all_connections = {}
    
    # Recopilar todas las conexiones únicas
    for gene in genome1:
        key = get_gene_key(gene)
        all_connections[key] = copy.deepcopy(gene)
    
    for gene in genome2:
        key = get_gene_key(gene)
        if key in all_connections:
            # Conexión existe en ambos padres: combinar de forma inteligente
            existing_gene = all_connections[key]
            
            if gene['type'] in ['input_hidden', 'hidden_output']:
                # Para conexiones: promediar pesos con variación
                avg_weight = (existing_gene['weight'] + gene['weight']) / 2
                variation = random.gauss(0, 0.05)  # Pequeña variación
                existing_gene['weight'] = avg_weight + variation
            else:
                # Para biases: seleccionar el mejor padre
                if random.random() < 0.7:  # 70% probabilidad de mantener el del mejor padre
                    existing_gene['weight'] = gene['weight']
        else:
            # Conexión solo existe en parent2: heredar con mayor probabilidad
            if random.random() < 0.6:  # 60% probabilidad de heredar
                all_connections[key] = copy.deepcopy(gene)
    
    # Convertir dict a lista
    child_genome = list(all_connections.values())
    
    # === MUTACIÓN ADAPTATIVA ===
    connection_count = len([g for g in child_genome if g['type'] in ['input_hidden', 'hidden_output']])
    
    # Tasa de mutación adaptativa (más mutación si hay pocas conexiones)
    base_mutation_rate = 0.08
    adaptive_rate = base_mutation_rate * (25 / max(5, connection_count))
    
    # Mutar pesos existentes
    for gene in child_genome:
        if random.random() < adaptive_rate:
            if gene['type'] in ['input_hidden', 'hidden_output']:
                # Mutación de conexión
                mutation_strength = random.gauss(0, 0.15)
                gene['weight'] += mutation_strength
                # Limitar pesos extremos
                gene['weight'] = max(-5.0, min(5.0, gene['weight']))
            elif gene['type'] in ['bias_hidden', 'bias_output']:
                # Mutación de bias
                gene['weight'] += random.gauss(0, 0.08)
                gene['weight'] = max(-2.0, min(2.0, gene['weight']))
    
    # Mutación estructural: agregar nueva conexión
    if connection_count < 30 and random.random() < 0.06:  # 6% probabilidad si hay pocas conexiones
        add_random_connection(child_genome)
    
    # Mutación estructural: eliminar conexión aleatoria
    if connection_count > 10 and random.random() < 0.03:  # 3% probabilidad si hay muchas conexiones
        remove_random_connection(child_genome)
    
    return child_genome

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
    attempts = 0
    while attempts < 20:
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
        attempts += 1
    
    # Si no se pudo agregar input->hidden, intentar hidden->output
    attempts = 0
    while attempts < 20:
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
        attempts += 1

def remove_random_connection(genome):
    """Elimina una conexión aleatoria del genoma"""
    connections = [gene for gene in genome if gene['type'] in ['input_hidden', 'hidden_output']]
    if connections:
        gene_to_remove = random.choice(connections)
        genome.remove(gene_to_remove)