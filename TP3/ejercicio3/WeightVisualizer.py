# WeightVisualizer.py

import numpy as np
import matplotlib.pyplot as plt
import os

def plot_weight_histograms(dino, save_path=None):
    """
    Genera histogramas de la distribución de pesos de un Dinosaur y, opcionalmente, los guarda en un archivo PNG.

    - dino: instancia de la clase Dinosaur (debe tener atributos W1, b1, W2, b2).
    - save_path: ruta (string) donde guardar el PNG. Si es None, sólo muestra el gráfico.
    """

    # Aplanamos las matrices en vectores para facilitar el histograma
    w1 = dino.W1.flatten()
    w2 = dino.W2.flatten()
    b1 = dino.b1.flatten() if hasattr(dino, 'b1') else np.array([])
    b2 = dino.b2.flatten() if hasattr(dino, 'b2') else np.array([])

    # Configuración de la figura
    plt.figure(figsize=(10, 6))

    # 1) Histograma de W1
    plt.subplot(2, 2, 1)
    plt.hist(w1, bins=40, color='skyblue', edgecolor='black')
    plt.title("W1 (Entrada → Oculta)")
    plt.ylabel("Frecuencia")
    plt.xlabel("Valor de peso")

    # 2) Histograma de W2
    plt.subplot(2, 2, 2)
    plt.hist(w2, bins=40, color='salmon', edgecolor='black')
    plt.title("W2 (Oculta → Salida)")
    plt.ylabel("Frecuencia")
    plt.xlabel("Valor de peso")

    # 3) Histograma de b1 (si existe)
    if b1.size > 0:
        plt.subplot(2, 2, 3)
        plt.hist(b1, bins=40, color='lightgreen', edgecolor='black')
        plt.title("b1 (bias capa oculta)")
        plt.ylabel("Frecuencia")
        plt.xlabel("Valor de bias")
    else:
        plt.subplot(2, 2, 3)
        plt.text(0.5, 0.5, "No hay bias b1", ha='center', va='center')
        plt.axis('off')

    # 4) Histograma de b2 (si existe)
    if b2.size > 0:
        plt.subplot(2, 2, 4)
        plt.hist(b2, bins=40, color='plum', edgecolor='black')
        plt.title("b2 (bias capa salida)")
        plt.ylabel("Frecuencia")
        plt.xlabel("Valor de bias")
    else:
        plt.subplot(2, 2, 4)
        plt.text(0.5, 0.5, "No hay bias b2", ha='center', va='center')
        plt.axis('off')

    plt.tight_layout()

    if save_path:
        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        plt.close()
    else:
        plt.show()
