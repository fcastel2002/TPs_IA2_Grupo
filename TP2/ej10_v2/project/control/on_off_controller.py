from control.controller_base import Controller
from typing import Dict

class OnOffController(Controller):
    """
    Implementa un controlador ON-OFF simple para comparación.
    """
    def __init__(self, environment, target_temp: float):
        super().__init__(environment)
        self.target_temp = target_temp

    def compute_action(self, inputs: Dict[str, float]) -> float:
        """
        Implementa lógica de control ON-OFF.
        
        Args:
            inputs: Diccionario con valores de entrada
            
        Returns:
            Valor de acción de control (0 o 100)
        """
        # Obtener datos del entorno
        sensors = self.env.read_sensors()
        current_temp_int = sensors['temp_int']
        T_ext = sensors['temp_ext']
        
        # Lógica ON-OFF: abrir ventana (act=100) si beneficia el acercamiento a la temperatura objetivo
        if (current_temp_int > self.target_temp and T_ext < current_temp_int) or \
           (current_temp_int < self.target_temp and T_ext > current_temp_int):
            # Abrir ventana ayuda a acercarse a target_temp
            return 100
        else:
            # Cerrar ventana es mejor
            return 0

def simulate_on_off(ext_series: list,
                    hours: list,
                    target_temp: float,
                    initial_temp_int: float,
                    comfort_night_cal: float,
                    comfort_night_enf: float) -> tuple:
    """
    Función de compatibilidad con el código original.
    Simula el comportamiento del sistema con un controlador ON-OFF.
    
    Esta función se mantiene para compatibilidad con el código existente.
    Para nuevos desarrollos, usar la clase OnOffController con Simulator.
    """
    from environment.series_environment import SeriesEnvironment
    import numpy as np
    
    # Parámetros físicos
    Rv_max = 0.8
    RC = 24 * 720
    dt = 3600.0
    
    # Instanciar el entorno
    env = SeriesEnvironment(target_temp, comfort_night_cal, comfort_night_enf, ext_series)
    env.temp_int = initial_temp_int  # Establecer la temperatura inicial

    T_int_list, T_ext_list, acts = [], [], []

    for hour in hours:
        if hour >= len(env.ext_series): break
        env.hour = hour  # Actualizar hora en el entorno
        
        # Obtener temp exterior
        T_ext = env.ext_series[hour]

        # Lógica de control ON-OFF
        current_temp_int = env.temp_int
        
        if (current_temp_int > target_temp and T_ext < current_temp_int) or \
           (current_temp_int < target_temp and T_ext > current_temp_int):
            # Abrir ventana ayuda a acercarse a target_temp
            act = 100
        else:
            # Cerrar ventana es mejor
            act = 0

        # Calcular nueva temp interior
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

        # Actualizar estado del entorno
        env.temp_int = T_int_new

    # Calcular Temperatura Promedio
    avg_temp_int = np.mean(T_int_list) if T_int_list else initial_temp_int
    avg_temp_ext = np.mean(T_ext_list) if T_ext_list else initial_temp_int

    # Devolver resultados
    return T_int_list, T_ext_list, acts, avg_temp_int, avg_temp_ext