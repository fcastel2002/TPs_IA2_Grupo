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
        # Mapeo de conjuntos de salida a valores crisp
        self.output_crisp_map = {
            "CERRAR": 0,
            "CENTRO": 50,
            "ABRIR": 100
        }

    def compute_action(self, inputs: Dict[str, float]) -> float:
        """
        Calcula la acción de control usando el sistema difuso.
        Si la salida pertenece 100% a un conjunto, devuelve el valor crisp correspondiente.
        
        Args:
            inputs: Diccionario con valores de entrada
            
        Returns:
            Valor de acción de control (0-100)
        """
        fuzzy_outputs = self.fis.infer(inputs)
        # Buscar si algún conjunto tiene pertenencia 1.0
        for label, degree in fuzzy_outputs.items():
            if degree == 1.0 and label in self.output_crisp_map:
                return self.output_crisp_map[label]
        # Si no, desborrosificar normalmente
        action = self.defuzzifier.defuzzify(fuzzy_outputs)
        return action