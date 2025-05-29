from parser import cargar_datos
import numpy as np
from red_neuronal import RedNeuronal, linear, linear_derivative, leaky_relu, leaky_relu_derivative

puntos = cargar_datos()
X = puntos[:, 0].reshape(-1, 1)
Y = puntos[:, 1].reshape(-1, 1)
grado = 2
X_poly = np.hstack([X ** i for i in range(1, grado + 1)])

mejor_loss = float('inf')
mejor_lr = None
mejor_neuronas = None

# Random search
n_iter = 20  # Número de combinaciones aleatorias a probar
np.random.seed(42)
for _ in range(n_iter):
    lr = 10 ** np.random.uniform(-4, -1)  # learning rate entre 0.0001 y 0.1
    neuronas = np.random.randint(1, 10)   # entre 1 y 10 neuronas ocultas
    modelo = RedNeuronal(
        capas_entrada=grado,
        capas_ocultas=neuronas,
        capas_salida=1,
        learning_rate=lr,
        activacion_oculta=leaky_relu,
        derivada_oculta=leaky_relu_derivative,
        activacion_salida=linear,
        derivada_salida=linear_derivative,
        alpha=0.02
    )
    losses = modelo.train(X_poly, Y, epochs=1500, verbose=False)
    final_loss = losses[-1]
    if final_loss < mejor_loss:
        mejor_loss = final_loss
        mejor_lr = lr
        mejor_neuronas = neuronas

print(f"Mejor loss: {mejor_loss:.4f}")
print(f"Mejor learning rate: {mejor_lr}")
print(f"Mejor número de neuronas ocultas: {mejor_neuronas}")
