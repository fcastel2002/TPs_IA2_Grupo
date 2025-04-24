from environment.environment import Environment
from typing import Dict

class SeriesEnvironment(Environment):
    def __init__(self,
                 comfort_day: float,
                 comfort_night_cal: float,
                 comfort_night_enf: float,
                 ext_series: list[float],
                 initial_temp_int: float):
        super().__init__(comfort_day, comfort_night_cal, comfort_night_enf)
        self.ext_series = ext_series
        self.current_step = 0 # Índice del paso actual en la simulación
        self.temp_int = initial_temp_int
        self.hour = 0.0 # Hora actual del día
        # Inicializar la predicción al comenzar
        self.update_daily_prediction()

    def read_sensors(self) -> Dict[str, float]:
        """Devuelve los valores de los sensores para el paso actual."""
        # Asegurarse de que el índice no exceda la longitud de la serie
        step = min(self.current_step, len(self.ext_series) - 1)
        
        return {
            'hora': self.hour, # Hora actual del día [0-24)
            'temp_int': self.temp_int,
            'temp_ext': self.ext_series[step]
        }

    def calculate_temperatura_predicha(self) -> str:
        """
        Calcula la temperatura predicha como el promedio de las diferencias
        entre la temperatura exterior y la temperatura de confort diurna.
        Solo para las horas de 8:00 a 20:00 de toda la serie.
        Devuelve 'ALTA', 'BAJA' o 'CERO'.
        """
        diff_sum = 0
        count = 0
        # Itera sobre toda la serie para calcular la predicción basada en el historial completo
        # Esto asume que ext_series representa un ciclo típico o el historial relevante.
        # Idealmente, esto usaría un pronóstico real.
        for idx, temp_ext_step in enumerate(self.ext_series):
             # Asumiendo dt=3600s, idx es la hora. Si dt es diferente, se necesita un array de horas.
             # Para simplificar, mantenemos la lógica original asumiendo que la longitud
             # de ext_series corresponde a pasos horarios, o que el patrón es representativo.
            hora_del_paso = idx % 24 # Estimación de la hora del día para ese paso
            if 8 < hora_del_paso <= 20: # Solo horario diurno
                 diff_sum += temp_ext_step - self.comfort_day
                 count += 1

        if count == 0:  # Evitar división por cero
            promedio_diferencia = 0
        else:
            promedio_diferencia = diff_sum / count

        # Clasificación basada en umbrales
        if promedio_diferencia > 2.5:
            return "ALTA"
        elif promedio_diferencia < -2.5:
            return "BAJA"
        else:
            return "CERO"

    def update_daily_prediction(self):
        """
        Actualiza la predicción diaria almacenada.
        Llamar una vez al día (p.ej., a medianoche).
        """
        self.prediccion_diaria = self.calculate_temperatura_predicha()
        # print(f"Debug: Predicción actualizada a {self.prediccion_diaria} en paso {self.current_step}") # Para depuración

    def update_state(self, new_temp_int: float, current_hour_in_day: float, step_index: int):
        """Actualiza la temperatura interior, la hora y el índice del paso."""
        self.temp_int = new_temp_int
        self.hour = current_hour_in_day
        self.current_step = step_index

    def set_comfort_day(self, new_value: float):
        """
        Permite cambiar la temperatura de confort diurna durante la simulación.
        """
        self.comfort_day = new_value
        self.update_daily_prediction()
