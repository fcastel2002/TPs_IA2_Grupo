from abc import ABC, abstractmethod
from typing import Dict

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
        raise NotImplementedError("Subclase debe implementar calculate_temperatura_predicha()")
            
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
        
        return (v_int - v0) * (v_ext - v_int)

    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y entrega dict compatible con FIS:
        {'Hora': ..., 'Z': ...}
        """
        s = self.read_sensors()
        z = self.compute_z(s['temp_int'], s['temp_ext'], s['hora'])
        return {'Hora': s['hora'], 'Z': z}