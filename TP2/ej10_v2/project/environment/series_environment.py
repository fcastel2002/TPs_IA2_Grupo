from environment.environment import Environment

class SeriesEnvironment(Environment):
    def __init__(self, comfort_day, comfort_night_cal, comfort_night_enf, ext_series):
        # Llama al init de la clase base Environment
        super().__init__(comfort_day, comfort_night_cal, comfort_night_enf)
        self.ext_series = ext_series
        self.hour = 0
        self.temp_int = comfort_day  # Temperatura inicial por defecto
        # La predicción se calcula/usa dentro de los métodos de Environment/FuzzyController

    def read_sensors(self):
        current_hour_index = int(self.hour)
        if current_hour_index >= len(self.ext_series):
            current_hour_index = len(self.ext_series) - 1
        return {
            'hora': float(current_hour_index % 24),
            'temp_int': self.temp_int,
            'temp_ext': self.ext_series[current_hour_index]
        }

    def calculate_temperatura_predicha(self):
        """
        Calcula la temperatura predicha como el promedio de las diferencias
        entre la temperatura exterior y la temperatura de confort.
        Solo para las horas de 8:00 a 20:00.
        """
        diff_sum = 0
        count = 0
        for hora in range(len(self.ext_series)):  # Solo de 8:00 a 20:00
            if hora % 24 <= 8 or hora % 24 > 20:
                continue
            diff_sum += self.ext_series[hora] - self.comfort_day
            count += 1
        
        if count == 0:  # Evitar división por cero
            promedio_diferencia = 0
        else:
            promedio_diferencia = diff_sum / count
            
        if promedio_diferencia > 2.5:  # Si la diferencia es alta
            self.temperatura_predicha = "ALTA"
        elif promedio_diferencia < -2.5:  # Si la diferencia es baja
            self.temperatura_predicha = "BAJA"
        else:
            self.temperatura_predicha = "CERO"

    def update_state(self, new_temp_int):
        """Actualiza la temperatura interior."""
        self.temp_int = new_temp_int
        # La hora se actualiza en el bucle de simulación