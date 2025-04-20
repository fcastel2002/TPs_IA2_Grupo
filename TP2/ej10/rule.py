from typing import List, Tuple, Dict
from linguistic_variable import LinguisticVariable

class FuzzyRule:
    """
    Representa una regla difusa tipo Mamdani:
    IF (var1 IS set1) AND (var2 IS set2) AND ... THEN (out_var IS out_set)
    """
    def __init__(self,
                 antecedents: List[Tuple[LinguisticVariable, str]],
                 consequent: Tuple[LinguisticVariable, str]):
        # antecedents: lista de (Variable, nombre_de_conjunto)
        # consequent: (Variable_salida, nombre_de_conjunto)
        self.antecedents = antecedents
        self.consequent = consequent

    def evaluate(self, fuzzified_inputs: Dict[str, Dict[str, float]]) -> float:
        """
        Dado un diccionario mapping variable_name -> {set_name: grado},
        retorna el grado de activación de la regla (min de antecedentes).
        """
        degrees = []
        for var, set_name in self.antecedents:
            var_name = var.name
            if var_name not in fuzzified_inputs:
                raise KeyError(f"Valor fuzzificado para variable '{var_name}' no encontrado")
            sets_map = fuzzified_inputs[var_name]
            if set_name not in sets_map:
                raise KeyError(f"Conjunto '{set_name}' no definido para variable '{var_name}'")
            degrees.append(sets_map[set_name])
        return min(degrees) if degrees else 0.0

    def __repr__(self) -> str:
        ants = " AND ".join([f"({v.name} IS {s})" for v, s in self.antecedents])
        out_v, out_s = self.consequent
        return f"IF {ants} THEN ({out_v.name} IS {out_s})"
