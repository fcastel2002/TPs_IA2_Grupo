from typing import Any
from membership_functions import MembershipFunction

class FuzzySet:
    """
    Representa un conjunto difuso: asocia un nombre a una función de pertenencia.
    """
    def __init__(self, name: str, mf: MembershipFunction):
        self.name = name
        self.mf = mf

    def membership(self, x: float) -> float:
        """
        Devuelve el grado de pertenencia μ(x) para este conjunto difuso.
        """
        return self.mf.μ(x)

    def __repr__(self) -> str:
        return f"FuzzySet('{self.name}')"
