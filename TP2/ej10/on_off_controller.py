# on_off_controller.py

import numpy as np
# Necesitamos importar SeriesEnvironment desde main.py donde está definida
# y también los parámetros físicos si no se pasan como argumentos.
from series_enviroment import SeriesEnvironment # Importa la clase definida en main.py

# Parámetros físicos (podrían pasarse como argumentos si prefieres)
# Si se definen aquí, asegúrate que coincidan con los de main.py
Rv_max = 0.1
RC   = 24 * 720
dt   = 3600.0

def simulate_on_off(ext_series: list,
                    hours: list, # Lista de índices de tiempo
                    target_temp: float,
                    initial_temp_int: float,
                    comfort_night_cal: float, # Necesario para instanciar SeriesEnvironment
                    comfort_night_enf: float  # Necesario para instanciar SeriesEnvironment
                    ) -> tuple:
    """
    Simula el comportamiento del sistema con un controlador ON-OFF.

    Args:
        ext_series: Lista de temperaturas exteriores por hora.
        hours: Lista de índices de hora para la simulación.
        target_temp: Temperatura objetivo para el control ON-OFF (usualmente comfort_day).
        initial_temp_int: Temperatura interior inicial.
        comfort_night_cal: Parámetro de confort nocturno (calentar).
        comfort_night_enf: Parámetro de confort nocturno (enfriar).

    Returns:
        Una tupla con: (T_int_list, T_ext_list, acts, avg_temp_int, avg_temp_ext)
    """
    # Instanciar el entorno. Pasamos target_temp como comfort_day,
    # y los parámetros de noche aunque no los usemos directamente en la lógica ON-OFF.
    env = SeriesEnvironment(target_temp, comfort_night_cal, comfort_night_enf, ext_series)
    env.temp_int = initial_temp_int # Establecer la temperatura inicial

    T_int_list, T_ext_list, acts = [], [], []

    for hour in hours:
        if hour >= len(env.ext_series): break
        env.hour = hour # Actualizar hora en el entorno

        # --- Lógica de control ON-OFF ---
        current_temp_int = env.temp_int
        if current_temp_int > target_temp:
            act = 100.0 # Abrir ventana
        else:
            act = 0.0   # Cerrar ventana
        # --------------------------------

        # Obtener temp exterior
        T_ext = env.ext_series[hour]

        # Calcular nueva temp interior (misma fórmula física)
        denominator = RC * (1 + Rv_max * (1 - act / 100.0))
        if abs(denominator) < 1e-9:
            T_int_new = env.temp_int
        else:
            dT_dt = (T_ext - env.temp_int) / denominator
            T_int_new = env.temp_int + dt * dT_dt

        # Registrar estado ANTES de actualizar
        T_int_list.append(env.temp_int)
        T_ext_list.append(T_ext)
        acts.append(act)

        # Actualizar estado del entorno para la siguiente iteración
        # Asumiendo que SeriesEnvironment tiene un método update_state o
        # simplemente actualizamos el atributo directamente.
        env.temp_int = T_int_new # Actualizamos directamente si no hay método update_state

    # --- Calcular Temperatura Promedio ---
    avg_temp_int = np.mean(T_int_list) if T_int_list else initial_temp_int
    avg_temp_ext = np.mean(T_ext_list) if T_ext_list else initial_temp_int

    # --- Devolver resultados ---
    return T_int_list, T_ext_list, acts, avg_temp_int, avg_temp_ext