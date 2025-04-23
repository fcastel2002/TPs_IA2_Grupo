import random
import math
from typing import List

def generate_sine_series_randomized_interval(mean: float,
                                             base_amplitude: float,
                                             days: int,
                                             hourly_amplitude_variation: float = 0.4,
                                             variation_interval_hours: int = 3,
                                             phase_shift: float = 6.0
                                             ) -> List[float]:
    """
    Genera una serie temporal de temperatura con variación sinusoidal y ruido aleatorio.
    
    Args:
        mean: Temperatura media
        base_amplitude: Amplitud base de la variación sinusoidal
        days: Número de días a simular
        hourly_amplitude_variation: Magnitud de la variación aleatoria por hora
        variation_interval_hours: Intervalo de horas para actualizar la variación aleatoria
        phase_shift: Desplazamiento de fase (horas)
        
    Returns:
        Lista de temperaturas horarias
    """
    total_series = []
    total_simulation_hours = days * 24
    last_random_variation = 0.0
    if variation_interval_hours < 1: variation_interval_hours = 1

    for hour_index in range(total_simulation_hours):
        if hour_index % variation_interval_hours == 0:
            last_random_variation = random.uniform(-hourly_amplitude_variation, hourly_amplitude_variation)
        h = hour_index % 24
        sin_component = base_amplitude * math.sin(2 * math.pi * (h - phase_shift) / 24.0)
        temp_hour = mean + sin_component + last_random_variation
        total_series.append(temp_hour)
    return total_series