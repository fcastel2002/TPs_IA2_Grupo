import numpy as np
from typing import Dict, List, Tuple, Any

class Simulator:
    """Clase para ejecutar simulaciones de control de temperatura."""
    
    def __init__(self, 
                 controller, 
                 physical_params: Dict[str, float] = None):
        """
        Inicializa el simulador.
        
        Args:
            controller: Controlador a utilizar
            physical_params: Parámetros físicos del modelo
        """
        self.controller = controller
        # Valores por defecto si no se proporcionan
        self.physical_params = physical_params or {
            'Rv_max': 0.8,
            'RC': 24 * 720,
            'dt': 3600.0
        }
    
    def run_simulation(self, hours: List[int]) -> Dict[str, List[float]]:
        """
        Ejecuta la simulación para las horas especificadas.
        
        Args:
            hours: Lista de índices de hora para simular
            
        Returns:
            Diccionario con resultados de la simulación
        """
        env = self.controller.env
        T_int_list, T_ext_list, acts = [], [], []
        
        for hour in hours:
            if hasattr(env, 'ext_series') and hour >= len(env.ext_series):
                break
                
            # Actualizar hora en el entorno si es necesario
            if hasattr(env, 'hour'):
                env.hour = hour
            
            # Obtener acción del controlador
            act = self.controller.step()
            
            # Obtener temperatura exterior
            if hasattr(env, 'ext_series'):
                T_ext = env.ext_series[hour]
            else:
                T_ext = env.read_sensors()['temp_ext']
            
            # Calcular nueva temperatura interior
            T_int = env.read_sensors()['temp_int']
            T_int_new = self._calculate_new_temperature(T_int, T_ext, act)
            
            # Registrar estado
            T_int_list.append(T_int)
            T_ext_list.append(T_ext)
            acts.append(act)
            
            # Actualizar estado
            if hasattr(env, 'update_state'):
                env.update_state(T_int_new)
            else:
                env.temp_int = T_int_new
        
        # Calcular promedios
        avg_temp_int = np.mean(T_int_list) if T_int_list else env.comfort_settings['day']
        avg_temp_ext = np.mean(T_ext_list) if T_ext_list else avg_temp_int
        
        return {
            'T_int': T_int_list,
            'T_ext': T_ext_list,
            'actions': acts,
            'avg_T_int': avg_temp_int,
            'avg_T_ext': avg_temp_ext
        }
    
    def _calculate_new_temperature(self, T_int: float, T_ext: float, act: float) -> float:
        """
        Calcula la nueva temperatura interior basada en el modelo físico.
        
        Args:
            T_int: Temperatura interior actual
            T_ext: Temperatura exterior
            act: Acción de control (0-100)
            
        Returns:
            Nueva temperatura interior
        """
        Rv_max = self.physical_params['Rv_max']
        RC = self.physical_params['RC']
        dt = self.physical_params['dt']
        
        denominator = RC * (1 + Rv_max * (1 - act/100.0))
        if abs(denominator) < 1e-9:
            return T_int
        else:
            return T_int + dt * (T_ext - T_int) / denominator