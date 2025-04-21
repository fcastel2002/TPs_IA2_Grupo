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

# --- Valores de Consigna (Originales de la consigna) ---
V0_DIA = 25.0
V0_CAL = 50.0
V0_ENF = 5.0
# ---------------------------------------------------------

# 1) Variables lingüísticas

# Hora (sin cambios)
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(7.5,  8.0, 20.0, 20.5)))
hora.add_set(FuzzySet('NOCHE_PM', TrapezoidalMF(20.0, 20.5, 23.99, 23.99)))
hora.add_set(FuzzySet('NOCHE_AM', TrapezoidalMF(0.0,  0.0,  7.5,  8.0)))

# Temperatura Predicha (TPREDICHA) (sin cambios en definición)
tpredicha = LinguisticVariable('TPREDICHA', (-5.0, 40.0))
tpredicha.add_set(FuzzySet('BAJA', TrapezoidalMF(-5.0, 0.0, 10.0, 15.0)))
tpredicha.add_set(FuzzySet('ALTA', TrapezoidalMF(15.0, 20.0, 35.0, 40.0)))

# Variables Z, ZCAL, ZENF
z_universe = (-800.0, 800.0) # Mantener universo amplio por ahora

# --- Ajuste de Conjuntos Z ---
# Hacer 'CERO' más estrecho y ajustar los otros
z_sets_def = {
    # CERO: Más estrecho, ej. -20 a 20
    'CERO':     FuzzySet('CERO',     TriangularMF(-10.0,  0.0,   10.0)),
    # POSITIVO: Rampa desde el final de CERO (20).
    'POSITIVO': FuzzySet('POSITIVO', TrapezoidalMF(10.0, 50.0, 800.0, 800.0)),
    # NEGATIVO: Imagen especular. Rampa de -100 a -20.
    'NEGATIVO': FuzzySet('NEGATIVO', TrapezoidalMF(-800.0, -800.0, -50.0, -10.0))
}
# -----------------------------

z = LinguisticVariable('Z', z_universe)
z_cal = LinguisticVariable('ZCAL', z_universe)
z_enf = LinguisticVariable('ZENF', z_universe)

for name, fs in z_sets_def.items():
    z.add_set(FuzzySet(name, fs.mf))
    z_cal.add_set(FuzzySet(name, fs.mf))
    z_enf.add_set(FuzzySet(name, fs.mf))


# Ventana (Salida) (sin cambios)
ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  10.0, 30.0)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(25.0, 50.0,  75.0)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(70.0,  90.0, 100.0, 100.0)))


# 2) Base de reglas (Sin cambios en la lógica)
rb = RuleBase()
# Reglas de DÍA (usan Z)
rb.add_rule(FuzzyRule([(hora, 'DIA'), (z, 'POSITIVO')], (ventana, 'CERRAR')))
rb.add_rule(FuzzyRule([(hora, 'DIA'), (z, 'CERO')],     (ventana, 'CENTRO')))
rb.add_rule(FuzzyRule([(hora, 'DIA'), (z, 'NEGATIVO')], (ventana, 'ABRIR')))
# Reglas de NOCHE (usan TPREDICHA y ZCAL o ZENF)
for h_noche in ['NOCHE_PM', 'NOCHE_AM']:
    # TPREDICHA ALTA -> usar ZENF
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'ALTA'), (z_enf, 'POSITIVO')], (ventana, 'CERRAR')))
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'ALTA'), (z_enf, 'CERO')],     (ventana, 'CENTRO')))
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'ALTA'), (z_enf, 'NEGATIVO')], (ventana, 'ABRIR')))
    # TPREDICHA BAJA -> usar ZCAL
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'BAJA'), (z_cal, 'POSITIVO')], (ventana, 'CERRAR')))
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'BAJA'), (z_cal, 'CERO')],     (ventana, 'CENTRO')))
    rb.add_rule(FuzzyRule([(hora, h_noche), (tpredicha, 'BAJA'), (z_cal, 'NEGATIVO')], (ventana, 'ABRIR')))


# 3) Sistema difuso y desborrosificador (Sin cambios)
fis_inputs = [hora, tpredicha, z, z_cal, z_enf]
fis = FuzzyInferenceSystem(inputs=fis_inputs, output=ventana, rule_base=rb)
defuzz = Defuzzifier(output_var=ventana, method='COG')


# 4) Entorno dinámico (Subclase de Environment - Sin cambios aquí)
class SeriesEnvironment(Environment):
    def __init__(self, comfort_day, comfort_night_cal, comfort_night_enf, ext_series):
        super().__init__(comfort_day, comfort_night_cal, comfort_night_enf)
        self.ext_series = ext_series
        self.hour       = 0
        self.temp_int   = comfort_day

    def read_sensors(self):
        current_ext_temp = self.ext_series[self.hour % len(self.ext_series)]
        predicted_ext_temp = current_ext_temp # Predicción simple
        return {
            'hora':     float(self.hour % 24),
            'temp_int': self.temp_int,
            'temp_ext': current_ext_temp,
            'temp_pred': predicted_ext_temp
        }

    def update_state(self, T_int_new, dt_hours=1):
        self.temp_int = T_int_new
        self.hour = (self.hour + dt_hours)


# 5) Tres series de temperatura exterior (Sin cambios)
base_low = { **{h:11 for h in range(9)}, 9:11,10:13,11:13,12:14,13:15,14:16,15:17,16:17,17:17,18:16,19:15,20:14,21:13,22:13,23:13 }
hours_list = list(range(24))
ext_low  = [base_low[h] for h in hours_list]
ext_mid  = [t + 8 for t in ext_low]
ext_high = [t + 16 for t in ext_low]


# 6) Simulación EULER + FuzzyController
def simulate(ext_series, sim_hours=48):
    env  = SeriesEnvironment(V0_DIA, V0_CAL, V0_ENF, ext_series)
    ctrl = FuzzyController(fis, defuzz, env)

    T_int_list, T_ext_list, T_pred_list, Acts_list = [], [], [], []
    Z_vals_list = [] # Para guardar los 3 Zs

    R = 1.0
    Rv_max = 0.1 * R
    RC = 4.8 * 3600.0
    C = RC / R
    dt_seconds = 3600.0

    print(f"\n--- Iniciando Simulación ({sim_hours}h) ---") # DIAGNÓSTICO
    current_sim_time_hours = 0
    while current_sim_time_hours < sim_hours:
        # --- DIAGNÓSTICO: Imprimir estado antes del paso ---
        sensor_data = env.read_sensors()
        T_int_now = sensor_data['temp_int']
        T_ext_now = sensor_data['temp_ext']
        hora_now = sensor_data['hora']
        z_values_now = env._calculate_z_values(T_int_now, T_ext_now)
        print(f"Hora {hora_now:.1f}: T_int={T_int_now:.2f}, T_ext={T_ext_now:.1f} -> ", end="")
        print(f"Z={z_values_now['Z']:.1f}, ZCAL={z_values_now['ZCAL']:.1f}, ZENF={z_values_now['ZENF']:.1f} -> ", end="")
        # ----------------------------------------------------

        action_percent = ctrl.step()

        # --- DIAGNÓSTICO: Imprimir acción ---
        print(f"Acción={action_percent:.2f}")
        # ------------------------------------

        T_pred_now = sensor_data['temp_pred'] # Leer T_pred usada por ctrl

        apertura = action_percent / 100.0
        Rv = Rv_max * (1.0 - apertura)
        if Rv < 1e-6: Rv = 1e-6

        R_total = R + Rv
        dT_int_dt = (T_ext_now - T_int_now) / (C * R_total)
        T_int_next = T_int_now + dT_int_dt * dt_seconds

        T_int_list.append(T_int_now)
        T_ext_list.append(T_ext_now)
        T_pred_list.append(T_pred_now)
        Acts_list.append(action_percent)
        Z_vals_list.append(z_values_now)

        env.update_state(T_int_next, dt_hours=1)
        current_sim_time_hours += 1
    print("--- Simulación Finalizada ---") # DIAGNÓSTICO

    sim_time_axis = list(range(sim_hours))
    # Devolver Zs también para posible análisis
    return sim_time_axis, T_int_list, T_ext_list, T_pred_list, Acts_list, Z_vals_list


# Ejecutar las simulaciones
data = {}
# Ejecutar y guardar resultados completos
results_low = simulate(ext_low, sim_hours=48)
results_mid = simulate(ext_mid, sim_hours=48)
results_high = simulate(ext_high, sim_hours=48)
# Guardar en data solo lo necesario para graficar ahora
data['Bajo'] = results_low[:5] # time, Tint, Text, Tpred, Acts
data['Medio'] = results_mid[:5]
data['Alto'] = results_high[:5]


# 7) Graficar cada serie (Sin cambios aquí)
for label, (sim_time, T_int, T_ext, T_pred, act) in data.items():
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    p1, = ax1.plot(sim_time, T_int, label='Interior ($T_{int}$)', color='tab:blue', linewidth=2)
    p2, = ax1.plot(sim_time, T_ext, label='Exterior ($T_{ext}$)', linestyle='--', color='tab:orange')
    ax1.axhline(V0_DIA, color='gray', linestyle='-.', linewidth=1, label=f'$V_0$ Día ({V0_DIA})')
    ax1.axhline(V0_CAL, color='red', linestyle=':', linewidth=1, label=f'$V_{{0CAL}}$ ({V0_CAL})')
    ax1.axhline(V0_ENF, color='cyan', linestyle=':', linewidth=1, label=f'$V_{{0ENF}}$ ({V0_ENF})')
    p4, = ax2.plot(sim_time, act, label='Apertura Ventana (%)', color='tab:green', alpha=0.8)
    ax1.set_xlabel('Tiempo (h)')
    ax1.set_ylabel('Temperatura (°C) / Valor V')
    ax2.set_ylabel('Apertura Ventana (%)')
    ax1.set_title(f'Simulación {len(sim_time)} h – Serie {label}')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax1.set_xticks(np.arange(0, len(sim_time)+1, 6))
    plots = [p1, p2, p4]
    labs = [p.get_label() for p in plots]
    h_lines, h_labels = ax1.get_legend_handles_labels()
    h_lines = [h for h, l in zip(h_lines, h_labels) if l.startswith('$V_')]
    h_labels = [l for l in h_labels if l.startswith('$V_')]
    ax1.legend(plots + h_lines, labs + h_labels, loc='best')
    plt.tight_layout()

# Graficar conjuntos borrosos (Sin cambios aquí)
def plot_fuzzy_variable(var):
    u_min, u_max = var.universe
    num_points = max(500, int((u_max - u_min) * 1))
    xs = np.linspace(u_min, u_max, num_points)
    plt.figure(figsize=(8, 4))
    for name, fs in var.sets.items():
        if hasattr(fs, 'mf') and callable(fs.mf.μ):
             ys = [fs.mf.μ(x) for x in xs]
             plt.plot(xs, ys, label=name, linewidth=2)
        else:
             print(f"Advertencia: No se pudo graficar el conjunto '{name}' para la variable '{var.name}'")
    plt.title(f"Conjuntos Difusos para '{var.name}'")
    plt.xlabel(f"Universo de '{var.name}'")
    plt.ylabel("Grado de Pertenencia μ(x)")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

plot_fuzzy_variable(hora)
plot_fuzzy_variable(tpredicha)
plot_fuzzy_variable(z)
plot_fuzzy_variable(ventana)

plt.show()

# --- ANÁLISIS ADICIONAL (Opcional) ---
# Puedes descomentar esto para ver los rangos de Z obtenidos
# all_z_vals = results_low[5] + results_mid[5] + results_high[5]
# z_flat = [z['Z'] for z in all_z_vals]
# zcal_flat = [z['ZCAL'] for z in all_z_vals]
# zenf_flat = [z['ZENF'] for z in all_z_vals]
# print("\n--- Rangos de Z observados ---")
# print(f"Z    : min={min(z_flat):.1f}, max={max(z_flat):.1f}")
# print(f"ZCAL : min={min(zcal_flat):.1f}, max={max(zcal_flat):.1f}")
# print(f"ZENF : min={min(zenf_flat):.1f}, max={max(zenf_flat):.1f}")
# ------------------------------------