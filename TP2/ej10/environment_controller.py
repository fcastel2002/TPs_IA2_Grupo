from typing import Dict

class Environment:
    """
    Modelo del entorno: lectura de sensores y cálculo de la variable Z.
    El método read_sensors debe ser implementado por el usuario o subclases.
    """
    def __init__(self,
                 comfort_day: float,
                 comfort_night_cal: float,
                 comfort_night_enf: float):
        self.comfort_day = comfort_day
        self.comfort_night_cal = comfort_night_cal
        self.comfort_night_enf = comfort_night_enf

    def read_sensors(self) -> Dict[str, float]:
        """
        Debe devolver un dict con:
          - 'hora': float en [0,24]
          - 'temp_int': temperatura interior
          - 'temp_ext': temperatura exterior
        """
        raise NotImplementedError("Subclase debe implementar read_sensors() con datos reales")

    def compute_z(self, v_int: float, v_ext: float, hour: float) -> float:
        """
        Calcula la variable Z para inferencia:
        - Modo DÍA (8–20h): z = (v_int - comfort_day)*(v_ext - v_int)
        - Modo NOCHE: usa comfort_night_cal o comfort_night_enf según heating/cooling
        """
        if 8 <= hour < 20:
            v0 = self.comfort_day
        else:
            # Noche: elegir punto de referencia
            if v_int < self.comfort_night_cal:
                v0 = self.comfort_night_cal
            elif v_int > self.comfort_night_enf:
                v0 = self.comfort_night_enf
            else:
                return 0.0
        return (v_int - v0) * (v_ext - v_int)

    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y entrega dict compatible con FIS:
        {'Hora': ..., 'Z': ...}
        """
        s = self.read_sensors()
        z = self.compute_z(s['temp_int'], s['temp_ext'], s['hora'])
        print(z)
        return {'Hora': s['hora'], 'Z': z}

class FuzzyController:
    """
    Orquesta el sistema de control difuso:
    - Lee inputs nítidos del Environment
    - Ejecuta inferencia
    - Desborrosifica
    """
    def __init__(self,
                 fis,
                 defuzzifier,
                 environment: Environment):
        self.fis = fis
        self.defuzzifier = defuzzifier
        self.env = environment

    def step(self) -> float:
        """
        Realiza un ciclo de control:
          1) Obtener entradas nítidas
          2) Inferir salidas difusas
          3) Desborrosificar y devolver acción (apertura ventana)
        """
        crisp_inputs = self.env.get_crisp_inputs()

        fuzzy_outputs = self.fis.infer(crisp_inputs)
        action = self.defuzzifier.defuzzify(fuzzy_outputs)
        return action


# Al final de environment_controller.py o en un archivo de pruebas

if __name__ == "__main__":
    import numpy as np

    # Rango de temperaturas interiores y exteriores que queremos analizar
    v_int_range = np.linspace(10, 30, 5)  # Temperaturas interiores de 10°C a 30°C
    v_ext_range = np.linspace(5, 35, 7)   # Temperaturas exteriores de 5°C a 35°C

    # Definir la clase Environment, que contiene el método compute_z (ya está en tu código)
    comfort_day = 25.0
    comfort_night_cal = 18.0
    comfort_night_enf = 26.0

    # Crear la instancia de Environment
    env = Environment(comfort_day, comfort_night_cal, comfort_night_enf)

    # Crear una lista para almacenar los valores de z
    z_values = []

    # Iterar sobre cada combinación de v_int (temperatura interior), v_ext (temperatura exterior) y hour (hora del día)
    for hour in range(24):
        for v_int in v_int_range:
            for v_ext in v_ext_range:
                z = env.compute_z(v_int, v_ext, hour)
                z_values.append((hour, v_int, v_ext, z))

    # Mostrar los resultados (hora, temperatura interior, temperatura exterior, z)
    for entry in z_values:
        print(f"Hora: {entry[0]}h | T_int: {entry[1]}°C | T_ext: {entry[2]}°C | Z: {entry[3]}")

    # Graficar los resultados para ver los patrones
    import matplotlib.pyplot as plt
    z_matrix = np.array([[env.compute_z(v_int, v_ext, hour) for v_ext in v_ext_range] for v_int in v_int_range for hour in range(24)])

    # Crear el gráfico
    plt.imshow(z_matrix, extent=[min(v_ext_range), max(v_ext_range), min(v_int_range), max(v_int_range)], aspect='auto', origin='lower', cmap='viridis')
    plt.colorbar(label='Valor de Z')
    plt.xlabel('Temperatura Exterior (°C)')
    plt.ylabel('Temperatura Interior (°C)')
    plt.title('Mapa de valores de Z a lo largo del día')
    plt.show()
