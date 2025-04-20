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
