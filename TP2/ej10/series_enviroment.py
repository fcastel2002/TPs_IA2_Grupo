# --------------------------------------------------------------------------
# 4) Entorno dinámico (Definición de SeriesEnvironment permanece aquí por ahora)
# --------------------------------------------------------------------------
# La clase Environment base se importa de environment_controller.py
import numpy as np
from environment_controller import Environment

class SeriesEnvironment(Environment):
    def __init__(self, comfort_day, comfort_night_cal, comfort_night_enf, ext_series):
        # Llama al init de la clase base Environment
        super().__init__(comfort_day, comfort_night_cal, comfort_night_enf) #
        self.ext_series = ext_series
        self.hour       = 0
        self.temp_int   = comfort_day # Temperatura inicial por defecto
        # La predicción se calcula/usa dentro de los métodos de Environment/FuzzyController

    def read_sensors(self): #
        current_hour_index = int(self.hour)
        if current_hour_index >= len(self.ext_series):
            current_hour_index = len(self.ext_series) - 1
        return {
            'hora':     float(current_hour_index % 24),
            'temp_int': self.temp_int,
            'temp_ext': self.ext_series[current_hour_index]
        }

    def update_state(self, new_temp_int):
         self.temp_int = new_temp_int
         # La hora se actualiza en el bucle de simulación
