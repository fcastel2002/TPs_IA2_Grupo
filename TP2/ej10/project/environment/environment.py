from abc import ABC, abstractmethod
from typing import Dict

class Environment(ABC):
    """
    Modelo abstracto del entorno: lectura de sensores y cálculo de la variable Z.
    """
    def __init__(self, comfort_settings: Dict[str, float]):
        """
        Inicializa el entorno con configuraciones de confort.
        
        Args:
            comfort_settings: Diccionario con configuraciones de confort
                (ej: {'day': 25.0, 'night_cal': 50.0, 'night_enf': 5.0})
        """
        self.comfort_settings = comfort_settings
        self.temperatura_predicha = None  # Será asignada según el cálculo

    @abstractmethod
    def read_sensors(self) -> Dict[str, float]:
        """
        Debe devolver un dict con:
          - 'hora': float en [0,24]
          - 'temp_int': temperatura interior
          - 'temp_ext': temperatura exterior
        """
        pass
    
    @abstractmethod
    def calculate_temperatura_predicha(self):
        """Calcula la temperatura predicha para el día siguiente."""
        pass
    
    def set_temperatura_predicha(self):
        """Establece la temperatura predicha para el día siguiente."""
        self.calculate_temperatura_predicha()

    def compute_z(self, v_int: float, v_ext: float, hour: float) -> float:
        """
        Recalcula Z en función de la temperatura predicha.
        
        Args:
            v_int: Temperatura interior
            v_ext: Temperatura exterior
            hour: Hora del día [0-24]
            
        Returns:
            Valor Z calculado
        """
        if 8 < hour <= 20:
            v0 = self.comfort_settings['day']
        else:  
            if self.temperatura_predicha == "ALTA":
                v0 = self.comfort_settings['night_enf']  # Para enfriar
            elif self.temperatura_predicha == "BAJA":
                v0 = self.comfort_settings['night_cal']  # Para calentar
            else:
                v0 = self.comfort_settings['day']  # Temperatura de confort
        
        return (v_int - v0) * (v_ext - v_int)

    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y entrega dict compatible con FIS:
        {'Hora': ..., 'Z': ...}
        """
        s = self.read_sensors()
        z = self.compute_z(s['temp_int'], s['temp_ext'], s['hora'])
        return {'Hora': s['hora'], 'Z': z}