from abc import ABC, abstractmethod
from typing import Dict, Any
# Asegúrate de que la importación del entorno sea correcta si es necesaria aquí
# from environment.environment import Environment # O la clase base/interfaz que uses

class Controller(ABC):
    """Clase base para todos los controladores."""

    def __init__(self, environment):
        """
        Inicializa el controlador con un entorno.

        Args:
            environment: Objeto de entorno que proporciona datos de sensores y estado.
                         Se espera que tenga métodos como get_crisp_inputs, read_sensors.
        """
        self.env = environment

    @abstractmethod
    def compute_action(self, inputs: Dict[str, float]) -> float:
        """
        Calcula la acción de control basada en las entradas.

        Args:
            inputs: Diccionario con valores de entrada (ej: {'Hora': H, 'Z': Z_val})

        Returns:
            Valor de acción de control (normalmente 0-100)
        """
        pass

    def step(self) -> float:
        """
        Realiza un ciclo de control:
          1) Obtener entradas nítidas (crisp) del entorno (incluyendo Z calculado con predicción diaria).
          2) Calcular acción usando compute_action.
          3) Devolver acción.

        Returns:
            Acción de control (0-100)
        """
        # La predicción diaria ahora se actualiza en el bucle de simulación principal.
        # self.env.set_temperatura_predicha() # <--- ELIMINADO
        
        # Obtener inputs, que incluye Z calculado con la predicción DIARIA actual del entorno
        inputs = self.env.get_crisp_inputs() 
        
        # Calcular la acción basada en esos inputs
        action = self.compute_action(inputs)
        
        return action