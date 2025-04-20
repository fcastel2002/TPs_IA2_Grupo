from typing import Dict, Tuple
from fuzzy_set import FuzzySet

class LinguisticVariable:
    """
    Representa una variable lingüística: un nombre, un universo de discurso y varios conjuntos difusos.
    """
    def __init__(self, name: str, universe: Tuple[float, float]):
        self.name = name
        self.universe = universe  # (min, max)
        self.sets: Dict[str, FuzzySet] = {}

    def add_set(self, fuzzy_set: FuzzySet):
        """
        Agrega un FuzzySet a esta variable. El nombre debe ser único.
        """
        if fuzzy_set.name in self.sets:
            raise ValueError(f"Ya existe un conjunto difuso con nombre '{fuzzy_set.name}' en '{self.name}'")
        self.sets[fuzzy_set.name] = fuzzy_set

    def fuzzify(self, x: float) -> Dict[str, float]:
        """
        Convierte un valor nítido x en un mapeo de nombre de conjunto → grado de pertenencia.
        """
        if not (self.universe[0] <= x <= self.universe[1]):
            raise ValueError(f"Valor {x} fuera del universo {self.universe} de la variable '{self.name}'")
        return {name: fs.membership(x) for name, fs in self.sets.items()}

    def __repr__(self) -> str:
        sets = ", ".join(self.sets.keys())
        return f"LinguisticVariable('{self.name}', sets=[{sets}])"
