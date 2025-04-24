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
        Calcula la temperatura predicha usando SOLO los datos del día siguiente al actual.
        Si no hay suficientes datos para el día siguiente, devuelve 'CERO'.
        """
        pasos_por_dia = 24  # Asumiendo 1 paso por hora
        dia_siguiente = (self.current_step // pasos_por_dia) + 1
        inicio = dia_siguiente * pasos_por_dia
        fin = min(inicio + pasos_por_dia, len(self.ext_series))
        if inicio >= len(self.ext_series):
            return "CERO"  # No hay datos del día siguiente
        diff_sum = 0
        count = 0
        for idx in range(inicio, fin):
            hora_del_paso = idx % pasos_por_dia
            if 8 < hora_del_paso <= 20:  # Solo horario diurno
                diff_sum += self.ext_series[idx] - self.comfort_day
                count += 1
        if count == 0:
            promedio_diferencia = 0
        else:
            promedio_diferencia = diff_sum / count
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
