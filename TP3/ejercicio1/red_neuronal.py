# Importa la función para cargar los datos
from parser import cargar_datos
import numpy as np
import matplotlib.pyplot as plt

def linear(z):
    return z
def linear_derivative(z):
    return np.ones_like(z)
def quadratic(z):
    return z ** 2
def quadratic_derivative(z):
    return 2 * z
def leaky_relu(z, alpha=0.02):
    return np.where(z > 0, z, alpha * z)
def leaky_relu_derivative(z, alpha=0.02):
    return np.where(z > 0, 1, alpha)

class RedNeuronal:
    def __init__(self, neuronas_entrada, neuronas_ocultas, neuronas_salida, learning_rate=0.004, activacion_oculta=leaky_relu, derivada_oculta=leaky_relu_derivative, activacion_salida=linear, derivada_salida=linear_derivative, alpha=0.02, epochs = 1000):
        self.neuronas_entrada = neuronas_entrada
        self.neuronas_ocultas = neuronas_ocultas
        self.neuronas_salida = neuronas_salida
        self.learning_rate = learning_rate
        self.activacion_oculta = lambda z: activacion_oculta(z, alpha)
        self.derivada_oculta = lambda z: derivada_oculta(z, alpha)
        self.activacion_salida = activacion_salida
        self.derivada_salida = derivada_salida
        self.loss = 0
        self.epochs = epochs
        self.inicializar_pesos()

    def inicializar_pesos(self):
        self.W1 = np.random.randn(self.neuronas_entrada, self.neuronas_ocultas) * 0.01
        self.b1 = np.zeros((1, self.neuronas_ocultas))
        self.W2 = np.random.randn(self.neuronas_ocultas, self.neuronas_salida) * 0.01
        self.b2 = np.zeros((1, self.neuronas_salida))

    def forward(self, X):
        Z1 = X @ self.W1 + self.b1
        A1 = self.activacion_oculta(Z1)
        Z2 = A1 @ self.W2 + self.b2
        y_pred = self.activacion_salida(Z2)
        return Z1, A1, Z2, y_pred

    def train(self, X, Y, verbose=True):
        losses = []
        for epoch in range(self.epochs):
            Z1, A1, Z2, y_pred = self.forward(X)
            loss = np.mean((Y - y_pred) ** 2)
            dL_dy = 2 * (y_pred - Y) / Y.shape[0]
            dZ2 = dL_dy * self.derivada_salida(Z2)
            dW2 = A1.T @ dZ2
            db2 = np.sum(dZ2, axis=0, keepdims=True)
            dA1 = dZ2 @ self.W2.T
            dZ1 = dA1 * self.derivada_oculta(Z1)
            dW1 = X.T @ dZ1
            db1 = np.sum(dZ1, axis=0, keepdims=True)
            # Actualizar pesos
            self.W1 -= self.learning_rate * dW1
            self.b1 -= self.learning_rate * db1
            self.W2 -= self.learning_rate * dW2
            self.b2 -= self.learning_rate * db2
            losses.append(loss)
            self.loss = loss
            if verbose and epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")
        return losses

    def predict(self, X):
        _, _, _, y_pred = self.forward(X)
        return y_pred

    def save(self, filename):
        np.savez(filename, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2)

    def load(self, filename):
        data = np.load(filename)
        self.W1 = data['W1']
        self.b1 = data['b1']
        self.W2 = data['W2']
        self.b2 = data['b2']

if __name__ == "__main__":
    # Cargar los datos
    puntos = cargar_datos()
    X = puntos[:, 0].reshape(-1, 1)
    Y = puntos[:, 1].reshape(-1, 1)
    grado = 2
    X_poly = np.hstack([X ** i for i in range(1, grado + 1)])
    #X_poly = (X_poly - X_poly.mean(axis=0)) / X_poly.std(axis=0)

    modelo = RedNeuronal(
        neuronas_entrada=grado,
        neuronas_ocultas=6,
        neuronas_salida=1,
        learning_rate=0.0081,
        activacion_oculta=leaky_relu,
        derivada_oculta=leaky_relu_derivative,
        activacion_salida=linear,
        derivada_salida=linear_derivative,
        alpha=0.02,
        epochs = 1000
    )
    modelo.train(X_poly, Y)
    x_min, x_max = X.min(), X.max()
    x_range = x_max - x_min
    x_extended = np.linspace(x_min - 0.3 * x_range, x_max + 0.3 * x_range, 300).reshape(-1, 1)
    
    # Crear características polinómicas para el rango extendido
    X_poly_extended = np.hstack([x_extended ** i for i in range(1, grado + 1)])
    
    # Hacer predicciones sobre el rango extendido
    y_tendencia = modelo.predict(X_poly_extended)
    
    # Predicciones solo para los datos de entrenamiento
    y_final = modelo.predict(X_poly)
    
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
    plt.figtext(0.5,0,f"{modelo.W1.shape[0]} entradas, {modelo.W1.shape[1]} neuronas ocultas, {modelo.W2.shape[1]} salidas, LR :{modelo.learning_rate}, Loss:{modelo.loss:.4f} ", ha='center', fontsize=13)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    modelo.save('pesos_entrenados.npz')