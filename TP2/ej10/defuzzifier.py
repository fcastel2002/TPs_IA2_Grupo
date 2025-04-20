from typing import Dict, List, Tuple, Callable
from fuzzy_set import FuzzySet
from membership_functions import TriangularMF, TrapezoidalMF, SingletonMF

class Defuzzifier:
    """
    Convierte conjuntos difusos agregados en un valor nítido.
    Métodos soportados: 'COG', 'SOM', 'MOM', 'LOM', 'WAM'.
    """
    def __init__(self,
                 output_var,
                 method: str = 'COG',
                 resolution: int = 1001):
        self.output_var = output_var
        self.method = method.upper()
        self.resolution = resolution
        if self.method not in {'COG','SOM','MOM','LOM','WAM'}:
            raise ValueError(f"Método de desborrosificación '{method}' no soportado")

    def defuzzify(self,
                  fuzzy_outputs: Dict[str, List[Tuple[FuzzySet, float]]]
                 ) -> float:
        # 1) Agregar fuerzas por set (max strength)
        agg_strength: Dict[str, float] = {}
        for set_name, lst in fuzzy_outputs.items():
            strengths = [strength for (_,strength) in lst]
            agg_strength[set_name] = max(strengths) if strengths else 0.0
        # 2) Construir función agregada μ(x)
        u_min, u_max = self.output_var.universe
        step = (u_max - u_min) / (self.resolution - 1)
        xs = [u_min + i*step for i in range(self.resolution)]
        mus = []
        for x in xs:
            mu_x = 0.0
            for set_name, strength in agg_strength.items():
                if strength <= 0: continue
                fs = self.output_var.sets[set_name]
                mu_set = fs.membership(x)
                mu_x = max(mu_x, min(strength, mu_set))
            mus.append(mu_x)
        # 3) Desborrosificación
        if self.method == 'COG':
            num = sum(x*mu for x,mu in zip(xs,mus))
            den = sum(mus)
            return num/den if den>0 else (u_min+u_max)/2
        # localizadores de máximos
        max_mu = max(mus)
        if max_mu == 0:
            return (u_min+u_max)/2
        max_points = [x for x,mu in zip(xs,mus) if abs(mu-max_mu)<1e-9]
        if self.method == 'SOM':  # smallest of maxima
            return min(max_points)
        if self.method == 'LOM':  # largest of maxima
            return max(max_points)
        if self.method == 'MOM':  # mean of maxima
            return sum(max_points)/len(max_points)
        # Weighted average of maxima (WAM)
        # calcular centro representativo por set
        centers = {}
        for set_name, strength in agg_strength.items():
            if strength<=0: continue
            fs = self.output_var.sets[set_name]
            mf = fs.mf
            if isinstance(mf, TriangularMF):
                center = mf.b
            elif isinstance(mf, TrapezoidalMF):
                center = (mf.b + mf.c)/2
            elif isinstance(mf, SingletonMF):
                center = mf.x0
            else:
                center = (u_min+u_max)/2
            centers[set_name] = center
        # weighted average
        num = sum(centers[name]*strg for name,strg in agg_strength.items() if strg>0)
        den = sum(strg for strg in agg_strength.values() if strg>0)
        return num/den if den>0 else (u_min+u_max)/2

