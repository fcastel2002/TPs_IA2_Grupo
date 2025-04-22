from abc import ABC, abstractmethod

class MembershipFunction(ABC):
    """
    Interfaz base para una función de pertenencia borrosa.
    Cada función retorna un grado de pertenencia μ(x) en [0,1].
    """
    @abstractmethod
    def μ(self, x: float) -> float:
        """Devuelve el grado de pertenencia para el valor crisp x."""
        pass

class TriangularMF(MembershipFunction):
    """
    Función de pertenencia triangular definida por los puntos (a,0), (b,1), (c,0).
    """
    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c

    def μ(self, x: float) -> float:
        if x <= self.a or x >= self.c:
            return 0.0
        if self.a < x <= self.b:
            return (x - self.a) / (self.b - self.a)
        # self.b < x < self.c
        return (self.c - x) / (self.c - self.b)

class TrapezoidalMF(MembershipFunction):
    """
    Función de pertenencia trapezoidal definida por los puntos (a,0), (b,1), (c,1), (d,0).
    """
    def __init__(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def μ(self, x: float) -> float:
        if x < self.a or x > self.d:
            return 0.0
        if self.a <= x < self.b:
            if self.a == self.b:
                return 1.0 if x == self.a else 0.0
            return (x - self.a) / (self.b - self.a)
        if self.b <= x <= self.c:
            return 1.0
        # self.c < x <= self.d
        if self.c == self.d:
            return 1.0 if x == self.c else 0.0

        return (self.d - x) / (self.d - self.c)

class SingletonMF(MembershipFunction):
    """
    Función de pertenencia singleton: μ(x0)=1, μ(x)!=x0 -> 0.
    """
    def __init__(self, x0: float):
        self.x0 = x0

    def μ(self, x: float) -> float:
        return 1.0 if x == self.x0 else 0.0
