import numpy as np
from typing import Dict, List, Tuple, Any
# Asegúrate de importar correctamente las clases base/interfaces necesarias
from control.controller_base import Controller
from environment.environment import Environment # O la clase base específica como SeriesEnvironment

class Simulator:
    """Clase para ejecutar simulaciones de control de temperatura de forma centralizada."""

    def __init__(self,
                 environment: Environment,
                 controller: Controller,
                 physical_params: Dict[str, float]):
        """
        Inicializa el simulador.

        Args:
            environment: Instancia del entorno de simulación (ej. SeriesEnvironment).
            controller: Instancia del controlador a utilizar (ej. FuzzyController, OnOffController).
            physical_params: Diccionario con parámetros físicos: {'Rv_max', 'RC', 'dt'}.
        """
        self.env = environment
        self.controller = controller
        self.physical_params = physical_params
        # Extraer parámetros físicos para fácil acceso
        self.Rv_max = physical_params['Rv_max']
        self.RC = physical_params['RC']
        self.dt = physical_params['dt']
        if self.dt <= 0:
            raise ValueError("El paso de tiempo dt debe ser positivo.")

    def run_simulation(self, num_steps: int, time_hours: List[float]) -> Dict[str, List[float] | float]:
        """
        Ejecuta la simulación para el número de pasos especificado.

        Args:
            num_steps: Número total de pasos de simulación.
            time_hours: Lista de tiempos acumulados en horas para cada paso.

        Returns:
            Diccionario con resultados de la simulación:
            {'T_int': Lista de T_int, 'T_ext': Lista de T_ext, 'actions': Lista de acciones,
             'avg_T_int': Promedio T_int, 'avg_T_ext': Promedio T_ext}
        """
        T_int_list, T_ext_list, acts = [], [], []
        last_day_index = -1

        # Asegurarse de que el entorno tenga la temperatura inicial correcta (ya debería estar en el init del env)
        initial_temp_int = self.env.temp_int 

        for step_index in range(num_steps):
            # Obtener la hora actual del día y el día actual
            current_total_hours = time_hours[step_index]
            current_hour_in_day = current_total_hours % 24
            current_day_index = int(current_total_hours // 24)

            # Actualizar estado del entorno (índice y hora) ANTES de actuar/sensar
            # Esto es importante para que read_sensors() use el estado correcto
            if hasattr(self.env, 'update_state'):
                 # Pasamos T_int actual porque aún no calculamos la nueva
                self.env.update_state(self.env.temp_int, current_hour_in_day, step_index)
            else: # Fallback si el entorno no tiene update_state explícito
                if hasattr(self.env, 'hour'): self.env.hour = current_hour_in_day
                if hasattr(self.env, 'current_step'): self.env.current_step = step_index


            # Actualizar la predicción diaria si es un nuevo día
            if current_day_index != last_day_index:
                if hasattr(self.env, 'update_daily_prediction'):
                    self.env.update_daily_prediction()
                    last_day_index = current_day_index
                else:
                     # Advertir si el entorno no soporta predicción diaria
                     if step_index == 0: # Solo advertir una vez
                         print("Advertencia: El entorno no tiene 'update_daily_prediction'. La predicción no se actualizará.")
                         last_day_index = current_day_index # Para evitar mensajes repetidos


            # --- Ciclo de Control ---
            # 1. Obtener acción del controlador (basada en el estado actual del entorno)
            #    El método step() del controlador llama a env.get_crisp_inputs() que usa compute_z()
            #    el cual ahora utiliza self.env.prediccion_diaria.
            action = self.controller.step()
            
            # 2. Leer sensores (después de la acción, por si la acción influyera en lecturas futuras)
            #    Aunque en este modelo no influye inmediatamente. Lo usamos para obtener T_ext y T_int actuales.
            sensors = self.env.read_sensors()
            T_int_current = sensors['temp_int']
            T_ext_current = sensors['temp_ext']

            # 3. Calcular la nueva temperatura interior usando el modelo físico
            T_int_new = self._calculate_new_temperature(T_int_current, T_ext_current, action)

            # --- Registro ---
            # Guardamos el estado *antes* de la actualización para el gráfico
            T_int_list.append(T_int_current)
            T_ext_list.append(T_ext_current)
            acts.append(action)

            # 4. Actualizar el estado del entorno con la nueva temperatura
            #    La hora y el step ya se actualizaron al inicio del bucle
            if hasattr(self.env, 'update_state'):
                 # Actualizamos solo T_int ya que hora y step se actualizaron antes
                 self.env.temp_int = T_int_new 
            else:
                 # Fallback si no hay update_state
                 self.env.temp_int = T_int_new


        # Calcular promedios al final
        avg_temp_int = np.mean(T_int_list) if T_int_list else initial_temp_int
        # Para T_ext, usamos la lista registrada o la serie original si está disponible
        avg_temp_ext = np.mean(T_ext_list) if T_ext_list else (np.mean(self.env.ext_series) if hasattr(self.env, 'ext_series') and self.env.ext_series else initial_temp_int)


        return {
            'T_int': T_int_list,
            'T_ext': T_ext_list, # Usamos la lista registrada consistente con T_int
            'actions': acts,
            'avg_T_int': avg_temp_int,
            'avg_T_ext': avg_temp_ext
        }

    def _calculate_new_temperature(self, T_int: float, T_ext: float, act: float) -> float:
        """
        Calcula la nueva temperatura interior basada en el modelo físico.
        """
        denominator = self.RC * (1 + self.Rv_max * (1 - act / 100.0))
        if abs(denominator) < 1e-9: # Evitar división por cero
            # Si el denominador es cero, no hay cambio de temperatura o es un caso extremo
            T_int_new = T_int
        else:
            dT_dt = (T_ext - T_int) / denominator
            T_int_new = T_int + self.dt * dT_dt

        # Opcional: Añadir límites físicos si es necesario (ej. no bajo cero absoluto)
        # T_int_new = max(T_int_new, -273.15)

        return T_int_new