import numpy as np
from NeuralNetwork import NeuralNetwork

# --------------------------------------------------
# Constantes para normalizar las features
# --------------------------------------------------
SCREEN_WIDTH        = 1100    # igual que en main.py
SCREEN_HEIGHT       = 600     # igual que en main.py
MAX_OBSTACLE_WIDTH  = 105     # ancho máximo entre Small y Large Cactus
MAX_OBSTACLE_HEIGHT = 95      # alto máximo entre Cactus y Bird
MAX_GAME_SPEED      = 100     # velocidad tope que consideramos

# --------------------------------------------------
# 1) Creamos la red
# --------------------------------------------------
nn = NeuralNetwork(input_size=6, hidden_sizes=[8], output_size=3)

# --------------------------------------------------
# 2) Definimos un ejemplo de features (no normalizadas)
#    [distancia, tipo, ancho, alto, y_dino, velocidad]
# --------------------------------------------------
sample = [150, 0, 34, 50, 310, 20]

# --------------------------------------------------
# 3) Normalizamos cada feature al rango [0,1]
# --------------------------------------------------
sample_norm = [
    sample[0] / SCREEN_WIDTH,         # distancia relativa
    sample[1],                        # tipo (0 o 1)
    sample[2] / MAX_OBSTACLE_WIDTH,   # ancho relativo
    sample[3] / MAX_OBSTACLE_HEIGHT,  # alto relativo
    sample[4] / SCREEN_HEIGHT,        # posición vertical relativa
    sample[5] / MAX_GAME_SPEED        # velocidad relativa
]

print("Normalized sample:", sample_norm)

# --------------------------------------------------
# 4) Forward-pass + decisión
# --------------------------------------------------
logits = nn.think(sample_norm)   # devuelve los logits
action = nn.act(logits)          # aplica softmax y argmax

# --------------------------------------------------
# 5) Resultados
# --------------------------------------------------
print("Logits:", logits)
print("Chosen action:", action)
