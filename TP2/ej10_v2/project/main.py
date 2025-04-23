# main.py - Versión refactorizada

import matplotlib.pyplot as plt
import numpy as np

# Importaciones de módulos refactorizados
from fuzzy.membership_functions import TriangularMF, TrapezoidalMF
from fuzzy.fuzzy_set import FuzzySet
from fuzzy.linguistic_variable import LinguisticVariable
from fuzzy.rule import FuzzyRule
from fuzzy.rule_base import RuleBase
from fuzzy.inference import FuzzyInferenceSystem
from fuzzy.defuzzifier import Defuzzifier

from control.fuzzy_controller import FuzzyController
from control.on_off_controller import simulate_on_off  # Mantener compatibilidad

from environment.series_environment import SeriesEnvironment
from simulation.data_generator import generate_sine_series_randomized_interval
from visualization.plotter import plot_comparison, plot_fuzzy_variable

# --------------------------------------------------------------------------
# 1) Variables lingüísticas (Sin cambios)
# --------------------------------------------------------------------------
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(8.5, 8.5, 20.5, 20.5)))
hora.add_set(FuzzySet('NOCHE',  TrapezoidalMF(0.0,  0.0,  8.5,  8.5)))
hora.add_set(FuzzySet('NOCHE2', TrapezoidalMF(20.5, 20.5, 24.0, 24.0)))

z = LinguisticVariable('Z', (-500.0, 500.0))
z.add_set(FuzzySet('POSITIVO', TrapezoidalMF(1.5,   450.0,  500.0, 500.0)))
z.add_set(FuzzySet('CERO',      TriangularMF(-2.35, 0.0,  2.35)))
z.add_set(FuzzySet('NEGATIVO',  TrapezoidalMF(-500.0, -500.0, -450.0, -1.5)))

ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  5.0, 25.0)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(35.0, 50.0,  65.0)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(75.0,  95.0, 100.0, 100.0)))

# --------------------------------------------------------------------------
# 2) Base de reglas (Sin cambios)
# --------------------------------------------------------------------------
rb = RuleBase()
# Día
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'POSITIVO')], (ventana, 'CERRAR')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'CERO')],     (ventana, 'CENTRO')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'NEGATIVO')], (ventana, 'ABRIR')))
# Noche
for nh in ('NOCHE','NOCHE2'):
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'NEGATIVO')], (ventana, 'ABRIR')))
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'POSITIVO')],(ventana, 'CERRAR')))
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'CERO')], (ventana, 'CERRAR')))

# --------------------------------------------------------------------------
# 3) Sistema difuso y desborrosificador (Sin cambios)
# --------------------------------------------------------------------------
fis    = FuzzyInferenceSystem(inputs=[hora, z], output=ventana, rule_base=rb)
defuzz = Defuzzifier(output_var=ventana, method='COG')

# --------------------------------------------------------------------------
# 4) Parámetros de simulación (Centralizado)
# --------------------------------------------------------------------------
# --- Parámetros de simulación ---
days = 3
variation_update_interval = 3 # En horas
amplitude_variation_magnitude = 0.4
comfort_temp_day = 25.0
comfort_temp_night_cal = 50.0
comfort_temp_night_enf = 5.0
initial_temp_int = comfort_temp_day

# --- Parámetros físicos ---
Rv_max = 0.8
RC   = 24 * 720
# dt = 3600.0 # Paso de tiempo en segundos (ej: 1 hora)
dt = 1800.0  # <- ¡NUEVO VALOR DE EJEMPLO! (0.5 horas)

# --- Calcular parámetros dependientes de dt ---
total_time_seconds = days * 24 * 3600
num_steps = int(total_time_seconds / dt)
# Crear un array de tiempo en horas para visualización y lógica basada en hora
time_hours = np.linspace(0, days * 24 - dt / 3600, num_steps)
# Crear un array de índices para los bucles
time_steps = list(range(num_steps))


# --- Escenarios de Temperatura Exterior ---
scenarios = {
    'Bajo': {'mean': 15.0, 'amplitude': 2.0},
    'Medio': {'mean': 24.0, 'amplitude': 5.0},
    'Alto': {'mean': 30.0, 'amplitude': 8.0}
}
# --------------------------------------------------------------------------
# 5) Generación de series temporales
# --------------------------------------------------------------------------
# Generar series de temperatura para cada escenario
ext_series = {}
for label, params in scenarios.items():
    # NOTA: Asumimos que generate_sine_series_randomized_interval
    # ahora puede usar num_steps y dt (o time_hours) para generar la serie correctamente.
    # Se pasa time_hours para que pueda generar la onda sinusoidal en base a la hora.
    ext_series[label] = generate_sine_series_randomized_interval(
        mean=params['mean'],
        base_amplitude=params['amplitude'],
        num_steps=num_steps, # <- Pasar número de pasos
        dt_seconds=dt,       # <- Pasar dt
        time_in_hours=time_hours, # <- Pasar el array de tiempo en horas
        hourly_amplitude_variation=amplitude_variation_magnitude, # Esto puede necesitar ajuste si dt != 3600
        variation_interval_hours=variation_update_interval, # Esto puede necesitar ajuste si dt != 3600
        phase_shift=6.0
    )
    # Asegurarse que la longitud coincida
    if len(ext_series[label]) != num_steps:
        print(f"Advertencia: La longitud de la serie generada ({len(ext_series[label])}) no coincide con num_steps ({num_steps}) para {label}. Ajustando...")
        # Podría ser necesario ajustar la serie (truncar o rellenar) o revisar la función generadora
        ext_series[label] = ext_series[label][:num_steps] # Ejemplo de truncado


# --------------------------------------------------------------------------
# 6) Simulación y visualización
# --------------------------------------------------------------------------
def simulate_fuzzy(
    ext_series_scenario,
    current_time_hours,
    time_steps,
    RC,
    Rv_max,
    dt,
    comfort_temp_day,
    comfort_temp_night_cal,
    comfort_temp_night_enf,
    initial_temp_int
):
    """Función de simulación Fuzzy adaptada para dt y parámetros explícitos."""
    env  = SeriesEnvironment(comfort_temp_day, comfort_temp_night_cal, comfort_temp_night_enf, ext_series_scenario)
    env.temp_int = initial_temp_int
    ctrl = FuzzyController(fis, defuzz, env)
    T_int_list, T_ext_list, acts = [], [], []

    for step_index in time_steps:
        if step_index >= len(env.ext_series): break # Seguridad
        current_hour_of_day = current_time_hours[step_index] % 24
        env.hour = current_hour_of_day
        act = ctrl.step()
        T_ext = env.ext_series[step_index]
        denominator = RC*(1 + Rv_max*(1-act/100.0))
        if abs(denominator) < 1e-9:
            T_int_new = env.temp_int
        else:
            T_int_new = env.temp_int + dt * (T_ext - env.temp_int) / denominator
        T_int_list.append(env.temp_int)
        T_ext_list.append(T_ext)
        acts.append(act)
        env.update_state(T_int_new)

    avg_temp_int = np.mean(T_int_list) if T_int_list else initial_temp_int
    avg_temp_ext = np.mean(T_ext_list) if T_ext_list else np.mean(ext_series_scenario) if ext_series_scenario else initial_temp_int
    return T_int_list, T_ext_list, acts, avg_temp_int, avg_temp_ext

# Ejecutar simulaciones para cada escenario
results = {}

for label, series in ext_series.items():
    print(f"--- Simulando escenario: {label} (dt={dt}s, steps={num_steps}) ---")

    # Simulación Fuzzy
    print("Ejecutando Fuzzy...")
    # Pasar el array de tiempo en horas a la simulación
    T_int_f, T_ext_f, act_f, avg_T_int_f, avg_T_ext_f = simulate_fuzzy(
        series,
        time_hours,
        time_steps,
        RC,
        Rv_max,
        dt,
        comfort_temp_day,
        comfort_temp_night_cal,
        comfort_temp_night_enf,
        initial_temp_int
    )

    # Simulación ON-OFF
    print("Ejecutando ON-OFF...")
    # NOTA: simulate_on_off también necesitaría ser adaptada para usar
    # num_steps, dt, y time_hours en lugar de la lista 'hours' original.
    # Aquí se asume que la función ha sido modificada correspondientemente.
    T_int_oo, T_ext_oo, act_oo, avg_T_int_oo, avg_T_ext_oo = simulate_on_off(
        ext_series=series,
        # hours=hours, <-- Reemplazado
        time_steps=time_steps, # Pasar índices o número de pasos
        time_hours=time_hours, # Pasar tiempo en horas para lógica día/noche
        dt_seconds=dt,       # Pasar dt
        target_temp=comfort_temp_day,
        initial_temp_int=initial_temp_int,
        comfort_night_cal=comfort_temp_night_cal,
        comfort_night_enf=comfort_temp_night_enf,
        RC=RC, # Pasar RC si es necesario para el cálculo interno
        Rv_max=Rv_max # Pasar Rv_max si es necesario para el cálculo interno
    )

    # Guardar resultados (sin cambios en la estructura)
    results[label] = {
        'fuzzy': {
            'T_int': T_int_f, 'T_ext': T_ext_f, 'actions': act_f,
            'avg_T_int': avg_T_int_f, 'avg_T_ext': avg_T_ext_f
        },
        'on_off': {
            'T_int': T_int_oo, 'T_ext': T_ext_oo, 'actions': act_oo,
            'avg_T_int': avg_T_int_oo, 'avg_T_ext': avg_T_ext_oo
        }
    }

    print(f"Resultados {label}: Fuzzy Avg T_int={avg_T_int_f:.1f}°C, ON-OFF Avg T_int={avg_T_int_oo:.1f}°C")

# Visualizar resultados
for label, data in results.items():
    # Pasar el array de tiempo en horas a la función de ploteo
    plot_comparison(
        label=label,
        time_hours=time_hours, # Usar el array de tiempo en horas para el eje X
        fuzzy_data=data['fuzzy'],
        onoff_data=data['on_off'],
        comfort_temp=comfort_temp_day,
        # days=days <-- No necesita 'days' si usa time_hours
    )

# Visualizar variables lingüísticas
plot_fuzzy_variable(hora)
plot_fuzzy_variable(z)
plot_fuzzy_variable(ventana)

# Mostrar todas las figuras
plt.show()