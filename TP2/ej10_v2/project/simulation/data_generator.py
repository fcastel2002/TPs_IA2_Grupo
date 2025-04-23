import random
import math
from typing import List

def generate_sine_series_randomized_interval(mean: float,
                                             base_amplitude: float,
                                             num_steps: int,
                                             dt_seconds: float,
                                             time_in_hours: List[float],
                                             hourly_amplitude_variation: float = 0.4,
                                             variation_interval_hours: int = 3,
                                             phase_shift: float = 6.0
                                             ) -> List[float]:
    """
    Genera una serie temporal de temperatura con variación sinusoidal y ruido aleatorio.
    
    Args:
        mean: Temperatura media
        base_amplitude: Amplitud base de la variación sinusoidal
        num_steps: Número total de pasos de simulación
        dt_seconds: Duración de cada paso en segundos
        time_in_hours: Lista de tiempos en horas para cada paso
        hourly_amplitude_variation: Magnitud de la variación aleatoria por hora
        variation_interval_hours: Intervalo de horas para actualizar la variación aleatoria
        phase_shift: Desplazamiento de fase (horas)
        
    Returns:
        Lista de temperaturas para cada paso de simulación
    """
    total_series = []
    last_random_variation = 0.0
    variation_interval_steps = max(1, int(variation_interval_hours * 3600 / dt_seconds))

    for step_index in range(num_steps):
        if step_index % variation_interval_steps == 0:
            last_random_variation = random.uniform(-hourly_amplitude_variation, hourly_amplitude_variation)
        current_hour = time_in_hours[step_index] % 24
        sin_component = base_amplitude * math.sin(2 * math.pi * (current_hour - phase_shift) / 24.0)
        temp_step = mean + sin_component + last_random_variation
        total_series.append(temp_step)
    return total_series