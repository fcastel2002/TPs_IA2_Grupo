import numpy as np
import random

class NeuralNetwork:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # ======================== INITIALIZE NETWORK WEIGTHS AND BIASES =============================
        # Red neuronal: 6 entradas -> 6 neuronas ocultas -> 3 salidas
        # Pero con conexiones limitadas (25 conexiones + 9 biases = 34 genes)
        self.entradas = 6  # Entradas (sensores)
        self.ocultas = 6   # Neuronas ocultas
        self.salidas = 3   # Neuronas de salida (acciones)
        
        # Inicializar matrices de pesos con ceros (conexiones desactivadas)
        self.weights_input_hidden = np.zeros((self.entradas, self.ocultas))  # 6x6 = 36 conexiones posibles
        self.weights_hidden_output = np.zeros((self.ocultas, self.salidas))  # 6x3 = 18 conexiones posibles
        
        # Biases para todas las neuronas (siempre activos)
        self.bias_hidden = np.random.randn(self.ocultas) * 0.5    # 6 biases capa oculta
        self.bias_output = np.random.randn(self.salidas) * 0.5    # 3 biases capa salida
        
        # Crear 25 conexiones aleatorias
        self.create_random_connections(20)
        # ============================================================================================

    def create_random_connections(self, num_connections):
        """Crea un número específico de conexiones aleatorias"""
        connections_created = 0
        
        while connections_created < num_connections:
            # Decidir aleatoriamente si crear conexión input->hidden o hidden->output
            if random.choice([True, False]):
                # Conexión input -> hidden
                i = random.randint(0, self.entradas-1)  # entrada
                j = random.randint(0, self.ocultas-1)  # neurona oculta
                if self.weights_input_hidden[i, j] == 0:  # Si no existe conexión
                    self.weights_input_hidden[i, j] = np.random.randn() * 0.5
                    connections_created += 1
            else:
                # Conexión hidden -> output
                i = random.randint(0, self.ocultas-1)  # neurona oculta
                j = random.randint(0, self.salidas-1)  # neurona salida
                if self.weights_hidden_output[i, j] == 0:  # Si no existe conexión
                    self.weights_hidden_output[i, j] = np.random.randn() * 0.5
                    connections_created += 1

    def relu(self, x):
        """Función de activación ReLU"""
        return np.maximum(0, x)

    def softmax(self, x):
        """Función softmax para la capa de salida"""
        # Manejar el caso donde todas las entradas son 0
        if np.all(x == 0):
            return np.ones(len(x)) / len(x)  # Distribución uniforme
        exp_x = np.exp(x - np.max(x))  # Estabilidad numérica
        return exp_x / np.sum(exp_x)

    def think(self, inputs):
        # ======================== PROCESS INFORMATION SENSED TO ACT =============================
        # Convertir entradas a array numpy
        inputs = np.array(inputs, dtype=np.float32)
        
        # Forward pass: entrada -> capa oculta
        hidden_input = np.dot(inputs, self.weights_input_hidden) + self.bias_hidden
        hidden_output = self.relu(hidden_input)
        
        # Forward pass: capa oculta -> salida
        output_input = np.dot(hidden_output, self.weights_hidden_output) + self.bias_output
        
        # Aplicar softmax para obtener probabilidades
        output = self.softmax(output_input)
        
        # ========================================================================================
        return self.act(output)

    def act(self, output):
        # ======================== USE THE ACTIVATION FUNCTION TO ACT =============================
        # Seleccionar la acción con mayor probabilidad
        action = np.argmax(output)
        
        # =========================================================================================
        if (action == 0):
            return "JUMP"
        elif (action == 1):
            return "DUCK"
        elif (action == 2):
            return "RUN"
    
    def get_genome(self):
        """Retorna el genoma: conexiones activas + biases"""
        genome = []
        
        # Agregar conexiones input->hidden (con identificador de posición)
        for i in range(self.entradas):
            for j in range(self.ocultas):
                if self.weights_input_hidden[i, j] != 0:
                    gene = {
                        'type': 'input_hidden',
                        'from': i,
                        'to': j,
                        'weight': self.weights_input_hidden[i, j]
                    }
                    genome.append(gene)
        
        # Agregar conexiones hidden->output
        for i in range(self.ocultas):
            for j in range(self.salidas):
                if self.weights_hidden_output[i, j] != 0:
                    gene = {
                        'type': 'hidden_output', 
                        'from': i,
                        'to': j,
                        'weight': self.weights_hidden_output[i, j]
                    }
                    genome.append(gene)
        
        # Agregar biases de capa oculta
        for i in range(self.ocultas):
            gene = {
                'type': 'bias_hidden',
                'neuron': i,
                'weight': self.bias_hidden[i]
            }
            genome.append(gene)
            
        # Agregar biases de capa salida
        for i in range(self.salidas):
            gene = {
                'type': 'bias_output',
                'neuron': i,
                'weight': self.bias_output[i]
            }
            genome.append(gene)
            
        return genome
    
    def set_genome(self, genome):
        """Establece la red neuronal desde un genoma"""
        # Reinicializar matrices
        self.weights_input_hidden = np.zeros((self.entradas, self.ocultas))
        self.weights_hidden_output = np.zeros((self.ocultas, self.salidas))
        self.bias_hidden = np.zeros(self.ocultas)
        self.bias_output = np.zeros(self.salidas)
        
        # Aplicar genes del genoma
        for gene in genome:
            if gene['type'] == 'input_hidden':
                self.weights_input_hidden[gene['from'], gene['to']] = gene['weight']
            elif gene['type'] == 'hidden_output':
                self.weights_hidden_output[gene['from'], gene['to']] = gene['weight']
            elif gene['type'] == 'bias_hidden':
                self.bias_hidden[gene['neuron']] = gene['weight']
            elif gene['type'] == 'bias_output':
                self.bias_output[gene['neuron']] = gene['weight']
    
    def count_connections(self):
        """Cuenta el número de conexiones activas"""
        input_hidden_count = np.count_nonzero(self.weights_input_hidden)
        hidden_output_count = np.count_nonzero(self.weights_hidden_output)
        return input_hidden_count + hidden_output_count