from abc import ABC, abstractmethod
from typing import Dict

class Environment(ABC):
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
        # La predicción diaria será manejada por la subclase
        self.prediccion_diaria: str | None = "CERO" # Valor inicial por defecto

    @abstractmethod
    def read_sensors(self) -> Dict[str, float]:
        """
        Debe devolver un dict con:
          - 'hora': float en [0,24]
          - 'temp_int': temperatura interior
          - 'temp_ext': temperatura exterior
        """
        raise NotImplementedError("Subclase debe implementar read_sensors()")

    @abstractmethod
    def calculate_temperatura_predicha(self) -> str:
        """
        Calcula la temperatura predicha como el promedio de las diferencias
        entre la temperatura exterior y la temperatura de confort (25°C).
        Solo para las horas de 8:00 a 20:00.
        Debe devolver 'ALTA', 'BAJA' o 'CERO'.
        """
        raise NotImplementedError("Subclase debe implementar calculate_temperatura_predicha()")

    @abstractmethod
    def update_daily_prediction(self):
        """
        Actualiza el atributo prediccion_diaria llamando a
        calculate_temperatura_predicha. Debe ser llamada una vez al día.
        """
        raise NotImplementedError("Subclase debe implementar update_daily_prediction()")


    def compute_z(self, v_int: float, v_ext: float, hour: float) -> float:
        """
        Recalcula Z en función de la predicción diaria almacenada.
        """
        if 8 < hour <= 20: # Horario diurno
            v0 = self.comfort_day
        else: # Horario nocturno
            # Usa la predicción almacenada para el día actual
            if self.prediccion_diaria == "ALTA":
                v0 = self.comfort_night_enf  # Noche cálida -> objetivo enfriar
            elif self.prediccion_diaria == "BAJA":
                v0 = self.comfort_night_cal  # Noche fría -> objetivo calentar
            else: # Predicción CERO o None
                v0 = self.comfort_day  # Mantener confort diurno por defecto
        
        # Definición de Z (sin cambios)
        return (v_int - v0) * (v_ext - v_int)

    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y entrega dict compatible con FIS:
        {'Hora': ..., 'Z': ...}
        """
        s = self.read_sensors()
        # Calcula Z usando la predicción diaria actual
        z_val = self.compute_z(s['temp_int'], s['temp_ext'], s['hora'])
        return {'Hora': s['hora'], 'Z': z_val}

    @abstractmethod
    def update_state(self, new_temp_int: float, current_hour: float):
        """Actualiza el estado del entorno."""
        pass
