from typing import List, Dict, Tuple, Callable
from linguistic_variable import LinguisticVariable
from rule_base import RuleBase
from rule import FuzzyRule
from fuzzy_set import FuzzySet

class FuzzyInferenceSystem:
    """
    Sistema de inferencia difusa Mamdani.
    Toma variables de entrada, una variable de salida y una base de reglas.
    """
    def __init__(self,
                 inputs: List[LinguisticVariable],
                 output: LinguisticVariable,
                 rule_base: RuleBase,
                 t_norm: Callable[[float, float], float] = min,
                 s_norm: Callable[[float, float], float] = max,
                 implic: Callable[[float, float], float] = min):
        self.inputs = {var.name: var for var in inputs}
        self.output = output
        self.rule_base = rule_base
        self.t_norm = t_norm
        self.s_norm = s_norm
        self.implic = implic

    def infer(self, crisp_inputs: Dict[str, float]) -> Dict[str, List[Tuple[FuzzySet, float]]]:
        """
        Ejecuta el proceso de inferencia:
        1) Fuzzificación de entradas.
        2) Evaluación de cada regla → grado de activación.
        3) Implicación (recorte) de conjuntos de salida.
        4) Agregación por regla (lista de (FuzzySet, grado)).
        Devuelve un dict: nombre_set_salida -> lista de (FuzzySet, grado).
        """
        # 1) Fuzzificación
        fuzzified: Dict[str, Dict[str, float]] = {}
        for name, var in self.inputs.items():
            if name not in crisp_inputs:
                raise KeyError(f"Falta entrada nítida para variable '{name}'")
            fuzzified[name] = var.fuzzify(crisp_inputs[name])
        # 2) Evaluación y recorte
        output_clipped: Dict[str, List[Tuple[FuzzySet, float]]] = {s: [] for s in self.output.sets}
        for rule in self.rule_base:
            strength = rule.evaluate(fuzzified)
            # 3) Consecuente
            out_var, out_set_name = rule.consequent
            if out_var.name != self.output.name:
                continue
            fs: FuzzySet = self.output.sets[out_set_name]
            # 4) Agregación: añadir recorte de este rule
            output_clipped[out_set_name].append((fs, strength))
        return output_clipped

    def fuzzified_inputs(self, crisp_inputs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Útil para debug: devuelve la fuzzificación de las entradas.
        """
        return {name: var.fuzzify(crisp_inputs[name]) for name, var in self.inputs.items()}
