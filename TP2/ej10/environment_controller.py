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
        self.temperatura_predicha = None  # Será asignada según el cálculo

    def read_sensors(self) -> Dict[str, float]:
        """
        Debe devolver un dict con:
          - 'hora': float en [0,24]
          - 'temp_int': temperatura interior
          - 'temp_ext': temperatura exterior
        """
        raise NotImplementedError("Subclase debe implementar read_sensors() con datos reales")

    def calculate_temperatura_predicha(self):
        """
        Calcula la temperatura predicha como el promedio de las diferencias
        entre la temperatura exterior y la temperatura de confort (25°C).
        Solo para las horas de 8:00 a 20:00.
        """
        diff_sum = 0
        count = 0
        for h in range(9, 21):  # Solo de 8:00 a 20:00
            diff_sum += self.ext_series[h] - self.comfort_day
            count += 1
        promedio_diferencia = diff_sum / count
        
        if promedio_diferencia > 2.5:  # Si la diferencia es alta
            self.temperatura_predicha = "ALTA"
        elif promedio_diferencia < -2.5:  # Si la diferencia es baja
            self.temperatura_predicha = "BAJA"
        else:
            self.temperatura_predicha = "CERO"

    def set_temperatura_predicha(self):
        """
        Establece la temperatura predicha para el día siguiente.
        """
        self.calculate_temperatura_predicha()

    def compute_z(self, v_int: float, v_ext: float, hour: float) -> float:
        """
        Recalcula Z en función de la temperatura predicha.
        """
        if 8 < hour <= 20:
            v0 = self.comfort_day
        else:  
            if self.temperatura_predicha == "ALTA":
                v0 = self.comfort_night_enf  # Para enfriar
            elif self.temperatura_predicha == "BAJA":
                v0 = self.comfort_night_cal  # Para calentar
            else:
                v0 = self.comfort_day  # Temperatura de confort
        
        print(f"{self.temperatura_predicha}, v0 = {v0}")
        return (v_int - v0) * (v_ext - v_int)

    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y entrega dict compatible con FIS:
        {'Hora': ..., 'Z': ...}
        """
        s = self.read_sensors()
        z = self.compute_z(s['temp_int'], s['temp_ext'], s['hora'])
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
        self.env.set_temperatura_predicha()
        crisp_inputs = self.env.get_crisp_inputs()
        fuzzy_outputs = self.fis.infer(crisp_inputs)
        action = self.defuzzifier.defuzzify(fuzzy_outputs)
        return action
