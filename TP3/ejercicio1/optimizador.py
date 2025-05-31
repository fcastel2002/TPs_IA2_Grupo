from parser import cargar_datos
import numpy as np
from red_neuronal import RedNeuronal, linear, linear_derivative, leaky_relu, leaky_relu_derivative
import matplotlib.pyplot as plt

puntos = cargar_datos()
X = puntos[:, 0].reshape(-1, 1)
Y = puntos[:, 1].reshape(-1, 1)
grado = 1
X_poly = np.hstack([X ** i for i in range(1, grado + 1)])

mejor_loss = float('inf')
mejor_lr = None
mejor_neuronas = None

# Random search
n_iter = 60  # Número de combinaciones aleatorias a probar
np.random.seed(42)
for _ in range(n_iter):
    lr = 10 ** np.random.uniform(-4, -1)  # learning rate entre 0.0001 y 0.1
    neuronas = np.random.randint(1, 10)   # entre 1 y 10 neuronas ocultas
    modelo = RedNeuronal(
        neuronas_entrada=grado,
        neuronas_ocultas=neuronas,
        neuronas_salida=1,
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

# Crear y entrenar la mejor red neuronal encontrada
mejor_modelo = RedNeuronal(
    neuronas_entrada=grado,
    neuronas_ocultas=mejor_neuronas,
    neuronas_salida=1,
    learning_rate=mejor_lr,
    activacion_oculta=leaky_relu,
    derivada_oculta=leaky_relu_derivative,
    activacion_salida=linear,
    derivada_salida=linear_derivative,
    alpha=0.02
)
mejor_modelo.train(X_poly, Y, epochs=1500, verbose=False)
y_pred = mejor_modelo.predict(X_poly)

# Mostrar el gráfico
plt.scatter(X, Y, s=10, label='Datos Originales', color='blue')
plt.scatter(X, y_pred, s=10, label='Predicciones', color='red')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Mejor red neuronal encontrada en 60 iteraciones')
plt.legend("lr = {:.4f}, neuronas = {}".format(mejor_lr, mejor_neuronas))
plt.show()
