# main.py

import matplotlib.pyplot as plt
import numpy as np
from membership_functions import TriangularMF, TrapezoidalMF
from fuzzy_set import FuzzySet
from linguistic_variable import LinguisticVariable
from rule import FuzzyRule
from rule_base import RuleBase
from inference import FuzzyInferenceSystem
from defuzzifier import Defuzzifier
from environment_controller import Environment, FuzzyController

# 1) Variables lingüísticas
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(6.0,  8.0, 20.0, 22.0)))
hora.add_set(FuzzySet('NOCHE',  TrapezoidalMF(0.0,  0.0,  6.0,  8.0)))
hora.add_set(FuzzySet('NOCHE2', TrapezoidalMF(20.0, 22.0, 24.0, 24.0)))

z = LinguisticVariable('Z', (-100.0, 100.0))
z.add_set(FuzzySet('POSITIVO', TriangularMF(0.0,   50.0,  100.0)))
z.add_set(FuzzySet('CERO',      TriangularMF(-10.0, 0.0,   10.0)))
z.add_set(FuzzySet('NEGATIVO',  TriangularMF(-100.0, -50.0, 0.0)))

ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  10.0, 30.0)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(25.0, 50.0,  75.0)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(70.0,  90.0, 100.0, 100.0)))

# 2) Base de reglas
rb = RuleBase()
# Día
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'POSITIVO')], (ventana, 'CERRAR')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'CERO')],     (ventana, 'CENTRO')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'NEGATIVO')], (ventana, 'ABRIR')))
# Noche
for nh in ('NOCHE','NOCHE2'):
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'NEGATIVO')], (ventana, 'ABRIR')))
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'POSITIVO')],(ventana, 'CERRAR')))

# 3) Sistema difuso y desborrosificador
fis    = FuzzyInferenceSystem(inputs=[hora, z], output=ventana, rule_base=rb)
defuzz = Defuzzifier(output_var=ventana, method='COG')

# 4) Entorno dinámico
class SeriesEnvironment(Environment):
    def __init__(self, comfort_day, comfort_night_cal, comfort_night_enf, ext_series):
        super().__init__(comfort_day, comfort_night_cal, comfort_night_enf)
        self.ext_series = ext_series
        self.hour       = 0
        self.temp_int   = comfort_day

    def read_sensors(self):
        return {
            'hora':     float(self.hour),
            'temp_int': self.temp_int,
            'temp_ext': self.ext_series[self.hour]
        }

# 5) Tres series de temperatura exterior
base_low = {
    **{h:11 for h in range(9)},
    9:11,10:13,11:13,12:14,13:15,14:16,15:17,16:17,17:17,18:16,19:15,20:14,21:13,22:13,23:13
}
hours    = list(range(24))
ext_low  = [base_low[h] for h in hours]
ext_mid  = [t + 11 for t in ext_low]
ext_high = [t + 20 for t in ext_low]

# 6) Simulación EULER + FuzzyController
def simulate(ext_series):
    env  = SeriesEnvironment(22.0, 18.0, 26.0, ext_series)
    ctrl = FuzzyController(fis, defuzz, env)
    T_int_list, T_ext_list, acts = [], [], []

    R, Rv_max = 1.0, 0.1
    RC   = 24 * 720  # τ = 5 h
    C    = RC / R
    dt   = 3600.0      # 1 h

    for _ in hours:
        act = ctrl.step()
        T_ext = env.ext_series[env.hour]
        #T_int = env.temp_int + dt/C * ((T_ext - env.temp_int) / (R + Rv_max*(1-act/100.0)))
        T_int = env.temp_int + dt * ((T_ext - env.temp_int) / (RC*(1 + Rv_max*(1-act/100.0))))
        
        T_int_list.append(T_int)
        T_ext_list.append(T_ext)
        acts.append(act)

        env.temp_int = T_int
        env.hour    += 1

    return T_int_list, T_ext_list, acts

data = {
    'Bajo':  simulate(ext_low),
    'Medio': simulate(ext_mid),
    'Alto':  simulate(ext_high)
}

# 7) Graficar cada serie en su propia ventana
for label, (T_int, T_ext, act) in data.items():
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(hours, T_int,   label='Interior', color='tab:blue')
    ax1.plot(hours, T_ext,   label='Exterior', linestyle='--', color='tab:orange')
    ax2.plot(hours, [a/100 for a in act], label='Apertura', color='tab:green')

    ax1.set_xlabel('Hora (h)')
    ax1.set_ylabel('Temperatura (°C)')
    ax2.set_ylabel('Apertura ventana (fracción)')
    ax1.set_title(f'Simulación 24 h – Serie {label}')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left')

    plt.tight_layout()

def plot_fuzzy_variable(var):
    """
    Grafica los conjuntos difusos de una LinguisticVariable en una nueva figura.
    """
    u_min, u_max = var.universe
    xs = np.linspace(u_min, u_max, 500)
    plt.figure()
    for name, fs in var.sets.items():
        ys = [fs.membership(x) for x in xs]
        plt.plot(xs, ys, label=name)
    plt.title(f"Conjuntos borrosos para '{var.name}'")
    plt.xlabel(f"Universo de '{var.name}'")
    plt.ylabel("Grado de pertenencia μ(x)")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

# Graficar conjuntos borrosos de cada variable lingüística
plot_fuzzy_variable(hora)
plot_fuzzy_variable(z)
plot_fuzzy_variable(ventana)

# Mostrar todas las figuras
plt.show()
