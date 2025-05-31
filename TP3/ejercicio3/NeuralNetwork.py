import numpy as np

class NeuralNetwork:
    def __init__(self, input_size, hidden_sizes, output_size):
        self.input_size = input_size      # 6
        self.hidden_size = hidden_sizes[0] # 8 (solo una capa oculta)
        self.output_size = output_size    # 3
        self.initialize()

    def initialize(self):
        # ======================== INITIALIZE NETWORK WEIGTHS AND BIASES =============================

        # Capa oculta: He initialization (fan_in = input_size)
        # W1 tendrá forma (hidden_size, input_size) → (8, 6)
        self.W1 = np.random.randn(self.hidden_size, self.input_size) * np.sqrt(2.0 / self.input_size)
        # b1 será un vector de ceros de longitud hidden_size → (8,)
        self.b1 = np.zeros(self.hidden_size)

        # Capa de salida: He initialization (fan_in = hidden_size)
        # W2 tendrá forma (output_size, hidden_size) → (3, 8)
        self.W2 = np.random.randn(self.output_size, self.hidden_size) * np.sqrt(2.0 / self.hidden_size)
        # b2 será un vector de ceros de longitud output_size → (3,)
        self.b2 = np.zeros(self.output_size)

    def think(self, features):
        """
        Recibe la lista de 6 features y devuelve los logits de la capa de salida.
        """
        x = np.array(features, dtype=float)

        # 1) Capa oculta
        z1 = self.W1.dot(x) + self.b1
        h  = np.maximum(0, z1)           # ReLU

        # 2) Capa de salida (logits)
        z2 = self.W2.dot(h) + self.b2
        return z2                       # <-- devolvemos LOS LOGITS, sin softmax

    def act(self, logits):
        """
        Recibe los logits (array de 3 valores) y:
         1) Aplica Softmax (la función de activación del output)
         2) Selecciona la acción de mayor probabilidad
         3) Mapea 0→JUMP, 1→DUCK, 2→RUN
        """
        # 1) Softmax para convertir logits en probabilidades
        exp_z = np.exp(logits - np.max(logits))
        probs = exp_z / exp_z.sum()

        # 2) Elegir índice de máxima probabilidad
        choice = np.argmax(probs)  # 0, 1 o 2

        # 3) Mapear a etiqueta según consigna
        if choice == 0:
            return "JUMP"
        elif choice == 1:
            return "DUCK"
        else:
            return "RUN"
