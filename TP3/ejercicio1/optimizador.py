from parser import cargar_datos
import numpy as np
from red_neuronal import RedNeuronal, linear, linear_derivative, leaky_relu, leaky_relu_derivative
import datetime
import matplotlib.pyplot as plt

puntos = cargar_datos()
X = puntos[:, 0].reshape(-1, 1)
Y = puntos[:, 1].reshape(-1, 1)
grado = 2
X_poly = np.hstack([X ** i for i in range(1, grado + 1)])

mejor_loss = float('inf')
mejor_lr = None
mejor_neuronas = None

# Random search
n_iter = 1000  # Número de combinaciones aleatorias a probar
learnling_rates = np.logspace(-3, -1, num = 80)

np.random.seed(42)
for _ in range(n_iter):
    #lr = 10 ** np.random.uniform(-4, -1)  # learning rate entre 0.0001 y 0.1, limitado a 4 cifras decimales
    lr = float(np.random.choice(learnling_rates))
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
        alpha=0.02,
        epochs=1000
        
    )
    losses = modelo.train(X_poly, Y, verbose=False)
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
    alpha=0.02,
    epochs=1500
)
mejor_modelo.train(X_poly, Y, verbose=False)
x_min, x_max = X.min(), X.max()
x_range = x_max - x_min
x_extended = np.linspace(x_min - 0.3 * x_range, x_max + 0.3 * x_range, 300).reshape(-1, 1)

# Crear características polinómicas para el rango extendido
X_poly_extended = np.hstack([x_extended ** i for i in range(1, grado + 1)])

# Hacer predicciones sobre el rango extendido
y_tendencia = mejor_modelo.predict(X_poly_extended)

# Predicciones solo para los datos de entrenamiento
y_final = mejor_modelo.predict(X_poly)

# Mostrar solo los datos originales
plt.scatter(X, Y, s=10, label='Datos Originales', color='blue')
plt.title('Dataset propuesto')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

# Mostrar datos originales y la tendencia predicha
plt.figure(figsize=(10, 6))
plt.scatter(X, Y, s=30, label='Datos Originales', color='blue', alpha=0.7)
plt.plot(x_extended, y_tendencia, label='Tendencia Predicha', color='red', linewidth=2)
plt.scatter(X, y_final, s=20, label='Predicciones en datos de entrenamiento', color='orange', alpha=0.8)
plt.xlabel('X')
plt.ylabel('Y')
plt.title(f'Tendencia de la Red Neuronal en {modelo.epochs} epochs')
plt.figtext(0.5,0,f"{modelo.W1.shape[0]} entradas, {mejor_neuronas} neuronas ocultas, {modelo.W2.shape[1]} salidas, LR :{mejor_lr:.4f}, Loss:{mejor_loss:.4f} ", ha='center', fontsize=13)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()