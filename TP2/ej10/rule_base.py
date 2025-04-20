from typing import List, Iterator
from rule import FuzzyRule

class RuleBase:
    """
    Contiene un conjunto de reglas difusas.
    Permite agregar y iterar sobre ellas.
    """
    def __init__(self):
        self.rules: List[FuzzyRule] = []

    def add_rule(self, rule: FuzzyRule):
        """
        Agrega una regla a la base.
        """
        self.rules.append(rule)

    def __iter__(self) -> Iterator[FuzzyRule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    def __repr__(self) -> str:
        return f"RuleBase({len(self.rules)} reglas)"
