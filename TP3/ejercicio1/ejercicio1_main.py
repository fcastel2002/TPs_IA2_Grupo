
# Importa la función para cargar los datos
from parser import cargar_datos
import numpy as np
import matplotlib.pyplot as plt

# Cargar los datos del archivo
puntos = cargar_datos()

X = puntos[:, 0].reshape(-1, 1)  # Reshape para asegurar que es un vector columna
Y = puntos[:, 1].reshape(-1, 1)  # Reshape para asegurar que es un vector columna

def linear(z):
    """Función de activación Lineal."""
    return z

def leaky_relu(z, alpha=0.01):
    """Función de activación Leaky ReLU."""
    return np.where(z > 0, z, alpha * z)

capas_entrada = 1
capas_ocultas = 2
capas_salida = 1


W1 = np.random.randn(capas_entrada, capas_ocultas) * 0.1
b1 = np.zeros((1, capas_ocultas))
W2 = np.random.randn(capas_ocultas, capas_salida) * 0.1
b2 = np.zeros((1, capas_salida))

loss_rate = 0.01
epochs = 1000

for epoch in range(epochs):
    
    Z1 = X @ W1 + b1
    A1 = linear(Z1)  # Aplicar la función de activación lineal