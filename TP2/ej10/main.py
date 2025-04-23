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
from environment_controller import Environment, FuzzyController, ControladorOnOff

# 1) Variables lingüísticas
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(8.5, 8.5, 20.5, 20.5)))
hora.add_set(FuzzySet('NOCHE',  TrapezoidalMF(0.0,  0.0,  8.5,  8.5)))
hora.add_set(FuzzySet('NOCHE2', TrapezoidalMF(20.5, 20.5, 24.0, 24.0)))

z = LinguisticVariable('Z', (-500.0, 500.0))
z.add_set(FuzzySet('POSITIVO', TrapezoidalMF(0.0,   50.0,  500.0, 500.0)))
z.add_set(FuzzySet('CERO',      TriangularMF(-10.0, 0.0,   10.0)))
z.add_set(FuzzySet('NEGATIVO',  TrapezoidalMF(-500.0, -500.0, -50.0, 0.0)))

ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  10.0, 40)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(35, 50.0,  65)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(60,  90.0, 100.0, 100.0)))

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
            'hora':     float(self.hour) % 24.0,
            'temp_int': self.temp_int,
            'temp_ext': self.ext_series[self.hour]
        }

# 5) Tres series de temperatura exterior
import math

# --- Horas 0..23 ---
hours = list(range(24))

def generate_sine_series(mean: float,
                         amplitude: float,
                         days: int,  # Nuevo parámetro: cantidad de días
                         phase_shift: float = 6.0  # fase en horas: 6h antes del pico
                        ) -> list:
    """
    Genera una serie de temperatura de 24 horas repetida para la cantidad de días especificada.
    T(h) = mean + amplitude * sin(2π * (h - phase_shift) / 24)
    Con phase_shift=6: mínimo a 0h, máximo a 12h.
    """
    # Generamos una serie de 24 horas
    daily_series = [
        mean + amplitude * math.sin(2 * math.pi * (h - phase_shift) / 24.0)
        for h in hours
    ]
    
    # Repetimos la serie tantas veces como días especificados
    return daily_series * days

# --- Parámetros ajustables ---
# Serie “Bajo”  (p. ej. noches muy frescas)
mean_low,  amp_low  = 11.0, 2.0
# Serie “Medio” (incluye confort)
mean_mid,  amp_mid  = 22.0, 5.0
# Serie “Alto”  (días muy calurosos)
mean_high, amp_high = 30.0, 8.0

# --- Generar las tres series (para 7 días como ejemplo) ---
days = 1  # Parámetro que define la cantidad de días
ext_low  = generate_sine_series(mean_low,  amp_low,  days)
ext_mid  = generate_sine_series(mean_mid,  amp_mid,  days)
ext_high = generate_sine_series(mean_high, amp_high, days)


hours = list(range(len(hours*days)))
# 6) Simulación EULER + FuzzyController
def simulate(ext_series):
    env  = SeriesEnvironment(25, 50, 5, ext_series)
    ctrl = FuzzyController(fis, defuzz, env)
    ctrl_on_off = ControladorOnOff(env)
    T_int_list, T_ext_list, acts = [], [], []

    T_int_oo_list = []
    acts_oo = []
    
    Rv_max = 0.2
    RC   = 24 * 720/1.5  # τ = 5 h
    dt   = 3600.0      # 1 h
    
    temp_int_oo = env.temp_int  # Inicializar temperatura interior para control On-Off

    for hour in hours:
        T_ext = env.ext_series[hour]
        T_ext_list.append(T_ext)
            
        # Control difuso
        act = ctrl.step()
        T_int = env.temp_int + dt * ((T_ext - env.temp_int) / (RC*(1 + Rv_max*(1-act/100.0))))
        T_int_list.append(T_int)
        acts.append(act)

        env.temp_int = T_int # Actualizar temperatura interior para control difuso
        # Control On-Off (sin control difuso)
        act_oo = ctrl_on_off.step(temp_int_oo)
        T_int_oo = temp_int_oo + dt * ((T_ext - temp_int_oo) / (RC*(1 + Rv_max*(1-act_oo/100.0))))
        T_int_oo_list.append(T_int_oo)
        acts_oo.append(act_oo)
        temp_int_oo = T_int_oo  # Actualizar temperatura interior para control On-Off
        
        env.hour    += 1
    return T_int_list, T_ext_list, acts, T_int_oo_list, acts_oo

data = {
    'Bajo':  simulate(ext_low),
    'Medio': simulate(ext_mid),
    'Alto':  simulate(ext_high)
}


# 7) Graficar cada serie en su propia ventana
for label, (T_int, T_ext, act, T_int_oo, act_oo) in data.items():
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(hours, T_int,   label='Interior', color='tab:blue')
    ax1.plot(hours, T_ext,   label='Exterior', linestyle='--', color='tab:orange')
    ax2.plot(hours, [a/100 for a in act], label='Apertura', color='tab:green')


    # Interior ON-OFF
    ax1.plot(hours, T_int_oo, label=f'Interior ON-OFF', color='tab:red', linestyle='-.', linewidth=1.5)
    # Acción ON-OFF (en magenta)
    ax2.plot(hours, [a/100.0 for a in act_oo], label='Apertura ON-OFF', color='tab:purple', drawstyle='steps-post', alpha=0.6, linewidth=1.0)

    # Ajuste del límite del eje y para la apertura (0 a 1)
    ax2.set_ylim(-0.05, 1.05)

    # Graficar la línea horizontal para la temperatura de confort (25°C)
    ax1.axhline(y=25, color='r', linestyle='--', label="Temperatura de confort (25°C)")

    # Colorear zonas del gráfico: día (8 a 20) y noche (20 a 8)
    for i in range(0, len(hours), 24):  # Iterar por días
        # Día: de 8:00 a 20:00
        ax1.axvspan(i + 8, i + 20, color='yellow', alpha=0.2)  # Día en amarillo
        # Noche: de 20:00 a 8:00
        ax1.axvspan(i + 20, i + 24, color='blue', alpha=0.1)  # Noche en azul claro
        ax1.axvspan(i + 0, i + 8, color='blue', alpha=0.1)

    ax1.set_xlabel('Hora (h)')
    ax1.set_ylabel('Temperatura (°C)')
    ax2.set_ylabel('Apertura ventana (fracción)')
    ax1.set_title(f'Simulación 24 h – Serie {label}')

    # Unir leyendas
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
