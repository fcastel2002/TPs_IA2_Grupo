import math
import random
from typing import List

def generate_sine_series_smooth(mean: float,
                                 base_amplitude: float,
                                 num_steps: int,
                                 dt_seconds: float,
                                 time_in_hours: List[float],
                                 phase_shift: float = 6.0
                                 ) -> List[float]:
    """
    Genera una serie temporal de temperatura con variación sinusoidal suave (sin ruido aleatorio),
    pero la media puede variar cada día dentro de un margen de ±3 grados respecto al valor inicial.
    Args:
        mean: Temperatura media base
        base_amplitude: Amplitud base de la variación sinusoidal
        num_steps: Número total de pasos de simulación
        dt_seconds: Duración de cada paso en segundos
        time_in_hours: Lista de tiempos en horas para cada paso
        phase_shift: Desplazamiento de fase (horas)
    Returns:
        Lista de temperaturas para cada paso de simulación
    """
    steps_per_day = int(24 * 3600 / dt_seconds)
    num_days = (num_steps + steps_per_day - 1) // steps_per_day
    # Generar una media aleatoria para cada día dentro del margen de ±3 grados
    daily_means = [random.uniform(mean - 0, mean + 0) for _ in range(num_days)]
    total_series = []
    for step_index in range(num_steps):
        day_idx = step_index // steps_per_day
        current_mean = daily_means[day_idx]
        current_hour = time_in_hours[step_index] % 24
        sin_component = base_amplitude * math.sin(2 * math.pi * (current_hour - phase_shift) / 24.0)
        temp_step = current_mean + sin_component
        total_series.append(temp_step)
    return total_series