
"""
Este módulo parsea los datos de datos.txt y los expone para ser usados en otros scripts.
"""
import os

DATOS_PATH = os.path.join(os.path.dirname(__file__), '../datos.txt')

import numpy as np

def cargar_datos():
    """Lee y parsea los datos de datos.txt, devolviendo un np.ndarray de shape (N, 2)."""
    datos = []
    with open(DATOS_PATH, 'r') as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith('//'):
                try:
                    punto = eval(linea, {"__builtins__": None}, {})
                    if isinstance(punto, tuple) and len(punto) == 2:
                        datos.append((float(punto[0]), float(punto[1])))
                except Exception:
                    continue
    return np.array(datos)
