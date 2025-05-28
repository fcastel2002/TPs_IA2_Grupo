

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
    def __init__(self, capas_entrada, capas_ocultas, capas_salida, learning_rate=0.004, activacion_oculta=leaky_relu, derivada_oculta=leaky_relu_derivative, activacion_salida=linear, derivada_salida=linear_derivative, alpha=0.02):
        self.capas_entrada = capas_entrada
        self.capas_ocultas = capas_ocultas
        self.capas_salida = capas_salida
        self.learning_rate = learning_rate
        self.activacion_oculta = lambda z: activacion_oculta(z, alpha)
        self.derivada_oculta = lambda z: derivada_oculta(z, alpha)
        self.activacion_salida = activacion_salida
        self.derivada_salida = derivada_salida
        self.inicializar_pesos()

    def inicializar_pesos(self):
        self.W1 = np.random.randn(self.capas_entrada, self.capas_ocultas) * 0.1
        self.b1 = np.zeros((1, self.capas_ocultas))
        self.W2 = np.random.randn(self.capas_ocultas, self.capas_salida) * 0.1
        self.b2 = np.zeros((1, self.capas_salida))

    def forward(self, X):
        Z1 = X @ self.W1 + self.b1
        A1 = self.activacion_oculta(Z1)
        Z2 = A1 @ self.W2 + self.b2
        y_pred = self.activacion_salida(Z2)
        return Z1, A1, Z2, y_pred

    def train(self, X, Y, epochs=1000, verbose=True):
        losses = []
        for epoch in range(epochs):
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
    modelo = RedNeuronal(
        capas_entrada=grado,
        capas_ocultas=4,
        capas_salida=1,
        learning_rate=0.0081,
        activacion_oculta=leaky_relu,
        derivada_oculta=leaky_relu_derivative,
        activacion_salida=linear,
        derivada_salida=linear_derivative,
        alpha=0.02
    )
    modelo.train(X_poly, Y, epochs=1000)
    y_final = modelo.predict(X_poly)
    plt.scatter(X, Y, s=10, label='Datos Originales', color='blue')
    plt.scatter(X, y_final, s=10, label='Predicciones', color='red')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Predicciones de la Red Neuronal')
    plt.legend()
    plt.show()
    modelo.save('pesos_entrenados.npz')