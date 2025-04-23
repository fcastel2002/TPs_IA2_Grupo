from abc import ABC, abstractmethod
from typing import Dict, Any

class Controller(ABC):
    """Clase base para todos los controladores."""
    
    def __init__(self, environment):
        """
        Inicializa el controlador con un entorno.
        
        Args:
            environment: Objeto de entorno que proporciona datos de sensores
        """
        self.env = environment
    
    @abstractmethod
    def compute_action(self, inputs: Dict[str, float]) -> float:
        """
        Calcula la acción de control basada en las entradas.
        
        Args:
            inputs: Diccionario con valores de entrada
            
        Returns:
            Valor de acción de control (0-100)
        """
        pass
    
    def step(self) -> float:
        """
        Realiza un ciclo de control:
          1) Obtener entradas
          2) Calcular acción
          3) Devolver acción
          
        Returns:
            Acción de control (0-100)
        """
        self.env.set_temperatura_predicha()
        inputs = self.env.get_crisp_inputs()
        action = self.compute_action(inputs)
        return action