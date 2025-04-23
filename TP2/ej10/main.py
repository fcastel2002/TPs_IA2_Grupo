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
from environment_controller import  FuzzyController
from series_enviroment import SeriesEnvironment
import random
import math

### NUEVO ###
# Importar la función de simulación ON-OFF del nuevo archivo
from on_off_controller import simulate_on_off

# --------------------------------------------------------------------------
# 1) Variables lingüísticas (Sin cambios)
# --------------------------------------------------------------------------
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(8.5, 8.5, 20.5, 20.5)))
hora.add_set(FuzzySet('NOCHE',  TrapezoidalMF(0.0,  0.0,  8.5,  8.5)))
hora.add_set(FuzzySet('NOCHE2', TrapezoidalMF(20.5, 20.5, 24.0, 24.0)))

z = LinguisticVariable('Z', (-500.0, 500.0))
z.add_set(FuzzySet('POSITIVO', TrapezoidalMF(0.0,   50.0,  500.0, 500.0)))
z.add_set(FuzzySet('CERO',      TriangularMF(-10.0, 0.0,   10.0)))
z.add_set(FuzzySet('NEGATIVO',  TrapezoidalMF(-500.0, -500.0, -50.0, 0.0)))

ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  10.0, 40.0)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(35.0, 50.0,  65.0)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(60.0,  90.0, 100.0, 100.0)))

# --------------------------------------------------------------------------
# 2) Base de reglas (Sin cambios)
# --------------------------------------------------------------------------
rb = RuleBase() #
# Día
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'POSITIVO')], (ventana, 'CERRAR'))) #
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'CERO')],     (ventana, 'CENTRO'))) #
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'NEGATIVO')], (ventana, 'ABRIR'))) #
# Noche
for nh in ('NOCHE','NOCHE2'):
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'NEGATIVO')], (ventana, 'ABRIR'))) #
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'POSITIVO')],(ventana, 'CERRAR'))) #
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'CERO')], (ventana, 'CERRAR'))) #

# --------------------------------------------------------------------------
# 3) Sistema difuso y desborrosificador (Sin cambios)
# --------------------------------------------------------------------------
fis    = FuzzyInferenceSystem(inputs=[hora, z], output=ventana, rule_base=rb) #
defuzz = Defuzzifier(output_var=ventana, method='COG') #


# --------------------------------------------------------------------------
# 5) Series de temperatura exterior (Generación sin cambios)
# --------------------------------------------------------------------------
hours_in_day = list(range(24))

def generate_sine_series_randomized_interval(mean: float,
                                             base_amplitude: float,
                                             days: int,
                                             hourly_amplitude_variation: float = 0.4,
                                             variation_interval_hours: int = 3,
                                             phase_shift: float = 6.0
                                             ) -> list:
    total_series = []
    total_simulation_hours = days * 24
    last_random_variation = 0.0
    if variation_interval_hours < 1: variation_interval_hours = 1

    for hour_index in range(total_simulation_hours):
        if hour_index % variation_interval_hours == 0:
            last_random_variation = random.uniform(-hourly_amplitude_variation, hourly_amplitude_variation)
        h = hour_index % 24
        sin_component = base_amplitude * math.sin(2 * math.pi * (h - phase_shift) / 24.0)
        temp_hour = mean + sin_component + last_random_variation
        total_series.append(temp_hour)
    return total_series

# --- Parámetros de simulación ---
days = 3
variation_update_interval = 3
amplitude_variation_magnitude = 0.4
comfort_temp_day = 25.0
comfort_temp_night_cal = 50.0 #
comfort_temp_night_enf = 5.0  #
initial_temp_int = comfort_temp_day # Temperatura inicial común

# --- Parámetros físicos (Usados en ambas simulaciones) ---
Rv_max = 0.8
RC   = 24 * 720
dt   = 3600.0

# --- Escenarios de Temperatura Exterior ---
mean_low,  amp_low  = 15.0, 2.0
mean_mid,  amp_mid  = 24.0, 5.0
mean_high, amp_high = 30.0, 8.0

# --- Generar Series ---
ext_low  = generate_sine_series_randomized_interval(mean_low, amp_low, days, amplitude_variation_magnitude, variation_update_interval, 6)
ext_mid  = generate_sine_series_randomized_interval(mean_mid, amp_mid, days, amplitude_variation_magnitude, variation_update_interval, 6)
ext_high = generate_sine_series_randomized_interval(mean_high, amp_high, days, amplitude_variation_magnitude, variation_update_interval, 6)

# Definir 'hours' basado en la longitud de las series generadas
hours = list(range(len(ext_low)))

# --------------------------------------------------------------------------
# 6) Simulación Fuzzy (Función sin cambios significativos)
# --------------------------------------------------------------------------
def simulate_fuzzy(ext_series):
    env  = SeriesEnvironment(comfort_temp_day, comfort_temp_night_cal, comfort_temp_night_enf, ext_series)
    env.temp_int = initial_temp_int # Asegurar temp inicial
    ctrl = FuzzyController(fis, defuzz, env) #
    T_int_list, T_ext_list, acts = [], [], []

    # Pre-calcular predicción inicial si es necesario para el primer paso
    env.calculate_temperatura_predicha() #

    for hour in hours:
        if hour >= len(env.ext_series): break
        env.hour = hour

        # Obtener acción del controlador difuso
        act = ctrl.step()

        # Obtener temp exterior
        T_ext = env.ext_series[hour]

        # Calcular nueva temp interior
        denominator = RC*(1 + Rv_max*(1-act/100.0))
        if abs(denominator) < 1e-9: T_int_new = env.temp_int
        else: T_int_new = env.temp_int + dt * (T_ext - env.temp_int) / denominator

        # Registrar estado ANTES de actualizar
        T_int_list.append(env.temp_int)
        T_ext_list.append(T_ext)
        acts.append(act)

        # Actualizar estado
        env.update_state(T_int_new)

    avg_temp_int = np.mean(T_int_list) if T_int_list else initial_temp_int
    avg_temp_ext = np.mean(T_ext_list) if T_ext_list else initial_temp_int
    return T_int_list, T_ext_list, acts, avg_temp_int, avg_temp_ext

# --------------------------------------------------------------------------
# 7) Ejecutar AMBAS simulaciones
# --------------------------------------------------------------------------
results = {}
scenarios = {'Bajo': ext_low, 'Medio': ext_mid, 'Alto': ext_high}

for label, ext_series in scenarios.items():
    print(f"--- Simulando escenario: {label} ---")
    # Simulación Fuzzy
    print("Ejecutando Fuzzy...")
    T_int_f, T_ext_f, act_f, avg_T_int_f, avg_T_ext_f = simulate_fuzzy(ext_series)

    # Simulación ON-OFF ### NUEVO ###
    print("Ejecutando ON-OFF...")
    T_int_oo, T_ext_oo, act_oo, avg_T_int_oo, avg_T_ext_oo = simulate_on_off(
        ext_series=ext_series,
        hours=hours,
        target_temp=comfort_temp_day,
        initial_temp_int=initial_temp_int,
        comfort_night_cal=comfort_temp_night_cal, # Pasar params requeridos por SeriesEnvironment
        comfort_night_enf=comfort_temp_night_enf
    )

    # Guardar resultados de AMBOS controladores
    results[label] = {
        'fuzzy': (T_int_f, T_ext_f, act_f, avg_T_int_f, avg_T_ext_f),
        'on_off': (T_int_oo, T_ext_oo, act_oo, avg_T_int_oo, avg_T_ext_oo)
    }
    print(f"Resultados {label}: Fuzzy Avg T_int={avg_T_int_f:.1f}°C, ON-OFF Avg T_int={avg_T_int_oo:.1f}°C")


# --------------------------------------------------------------------------
# 8) Graficar Comparativas ### MODIFICADO ###
# --------------------------------------------------------------------------
for label, data in results.items():
    # Desempaquetar resultados de ambos controladores
    T_int_f, T_ext_f, act_f, avg_T_int_f, avg_T_ext_f = data['fuzzy']
    T_int_oo, T_ext_oo, act_oo, avg_T_int_oo, avg_T_ext_oo = data['on_off']
    # T_ext es la misma para ambos, podemos usar T_ext_f o T_ext_oo

    fig, ax1 = plt.subplots(figsize=(12, 6)) # Hacer figura un poco más ancha
    ax2 = ax1.twinx()

    # --- Graficar temperaturas ---
    # Exterior (una sola vez)
    ax1.plot(hours, T_ext_f, label='Exterior', linestyle='--', color='tab:orange', alpha=0.7)
    # Interior Fuzzy
    ax1.plot(hours, T_int_f, label=f'Interior Fuzzy (Prom: {avg_T_int_f:.1f}°C)', color='tab:blue', linewidth=2)
    # Interior ON-OFF
    ax1.plot(hours, T_int_oo, label=f'Interior ON-OFF (Prom: {avg_T_int_oo:.1f}°C)', color='tab:red', linestyle='-.', linewidth=1.5)

    # Línea de confort
    ax1.axhline(y=comfort_temp_day, color='black', linestyle=':', linewidth=1, label=f"Confort ({comfort_temp_day}°C)")

    # --- Graficar acciones ---
    # Acción Fuzzy (en verde)
    ax2.plot(hours, [a/100.0 for a in act_f], label='Apertura Fuzzy', color='tab:green', drawstyle='steps-post', alpha=0.8, linewidth=1.5)
    # Acción ON-OFF (en magenta)
    ax2.plot(hours, [a/100.0 for a in act_oo], label='Apertura ON-OFF', color='tab:purple', drawstyle='steps-post', alpha=0.6, linewidth=1.0)

    # Ajuste del límite del eje y para la apertura (0 a 1)
    ax2.set_ylim(-0.05, 1.05)

    # Colorear zonas día/noche
    for i in range(0, len(hours), 24):
        ax1.axvspan(i + 8.5, i + 20.5, color='yellow', alpha=0.15, lw=0)
        ax1.axvspan(i + 20.5, i + 24, color='blue', alpha=0.1, lw=0)
        ax1.axvspan(i + 0, i + 8.5, color='blue', alpha=0.1, lw=0)

    # Etiquetas y título
    ax1.set_xlabel('Hora (h)')
    ax1.set_ylabel('Temperatura (°C)')
    ax2.set_ylabel('Apertura ventana (fracción)')
    ax1.tick_params(axis='y')
    ax2.tick_params(axis='y')
    ax1.set_title(f'Comparativa Fuzzy vs ON-OFF: {days} días – Serie {label}')
    ax1.grid(True, axis='y', linestyle=':', alpha=0.6)

    # Unir leyendas
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3) # Ajustar ncol y posición

    plt.xlim(0, len(hours) - 1)
    plt.tight_layout(rect=[0, 0.1, 1, 0.95]) # Ajustar para leyenda y título

# --------------------------------------------------------------------------
# 9) Graficar Variables Lingüísticas (Sin cambios)
# --------------------------------------------------------------------------
def plot_fuzzy_variable(var):
    u_min, u_max = var.universe
    xs = np.linspace(u_min, u_max, 500)
    plt.figure(figsize=(8, 4)) # Tamaño ajustado
    for name, fs in var.sets.items(): #
        ys = [fs.membership(x) for x in xs] #
        plt.plot(xs, ys, label=name)
    plt.title(f"Variable Lingüística: '{var.name}'") #
    plt.xlabel("Universo de Discurso")
    plt.ylabel("Grado de pertenencia μ(x)")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()

# Graficar conjuntos difusos
plot_fuzzy_variable(hora) #
plot_fuzzy_variable(z) #
plot_fuzzy_variable(ventana) #

# Mostrar todas las figuras
plt.show()