from control.controller_base import Controller
from typing import Dict

class FuzzyController(Controller):
    """
    Orquesta el sistema de control difuso:
    - Lee inputs nítidos del Environment
    - Ejecuta inferencia
    - Desborrosifica
    """
    def __init__(self, fis, defuzzifier, environment):
        super().__init__(environment)
        self.fis = fis
        self.defuzzifier = defuzzifier

    def compute_action(self, inputs: Dict[str, float]) -> float:
        """
        Calcula la acción de control usando el sistema difuso.
        
        Args:
            inputs: Diccionario con valores de entrada
            
        Returns:
            Valor de acción de control (0-100)
        """
        fuzzy_outputs = self.fis.infer(inputs)
        action = self.defuzzifier.defuzzify(fuzzy_outputs)
        return action