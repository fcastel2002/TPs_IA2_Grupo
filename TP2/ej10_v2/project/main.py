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
# Importar OnOffController para usar con Simulator
from control.on_off_controller import OnOffController
# simulate_on_off ya no se usa directamente si usamos Simulator para ambos
# from control.on_off_controller import simulate_on_off

from environment.series_environment import SeriesEnvironment
from simulation.data_generator import generate_sine_series_randomized_interval
from simulation.simulator import Simulator # <--- Importar Simulator
from visualization.plotter import plot_comparison, plot_fuzzy_variable

# --------------------------------------------------------------------------
# 1) Variables lingüísticas (Sin cambios)
# --------------------------------------------------------------------------
hora = LinguisticVariable('Hora', (0.0, 24.0))
hora.add_set(FuzzySet('DIA',    TrapezoidalMF(8.5, 8.5, 20.5, 20.5)))
# Corregir solapamiento y asegurar cobertura completa: Noche de 20:30 a 8:30
hora.add_set(FuzzySet('NOCHE',  TrapezoidalMF(20.5, 20.5, 24.0, 24.0))) # Hasta medianoche
hora.add_set(FuzzySet('NOCHE_AM', TrapezoidalMF(0.0, 0.0, 8.5, 8.5))) # Desde medianoche

z_limit = 500
z = LinguisticVariable('Z', (-z_limit, z_limit))
z.add_set(FuzzySet('POSITIVO', TrapezoidalMF(1.5,  200.0,  z_limit, z_limit)))
z.add_set(FuzzySet('CERO',      TriangularMF(-3.6, 0.0,  3.6)))
z.add_set(FuzzySet('NEGATIVO',  TrapezoidalMF(-z_limit, -z_limit, -200.0, -1.5)))

ventana = LinguisticVariable('Ventana', (0.0, 100.0))
ventana.add_set(FuzzySet('CERRAR', TrapezoidalMF(0.0,   0.0,  5.0, 49.0)))
ventana.add_set(FuzzySet('CENTRO', TriangularMF(48.0, 50.0,  53.0)))
ventana.add_set(FuzzySet('ABRIR',  TrapezoidalMF(52.0,  95.0, 100.0, 100.0)))

# --------------------------------------------------------------------------
# 2) Base de reglas (Adaptada a nuevos nombres de sets de Hora)
# --------------------------------------------------------------------------
rb = RuleBase()
# Día
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'POSITIVO')], (ventana, 'CERRAR')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'CERO')],     (ventana, 'CENTRO')))
rb.add_rule(FuzzyRule([(hora, 'DIA'),    (z, 'NEGATIVO')], (ventana, 'ABRIR')))
# Noche (usando ambos sets nocturnos)
for nh in ('NOCHE', 'NOCHE_AM'):
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'NEGATIVO')], (ventana, 'ABRIR'))) # Z<0 (enfriamiento pasivo o calor exterior) -> Abrir
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'POSITIVO')],(ventana, 'CERRAR'))) # Z>0 (calentamiento pasivo o frío exterior) -> Cerrar
    rb.add_rule(FuzzyRule([(hora, nh),    (z, 'CERO')], (ventana, 'CERRAR'))) # Z~0 -> Cerrar por defecto en la noche

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
comfort_temp_night_cal = 50.0 # Objetivo si noche es fría (predicción BAJA)
comfort_temp_night_enf = 5.0  # Objetivo si noche es cálida (predicción ALTA)
initial_temp_int = comfort_temp_day

# --- Parámetros físicos ---
physical_params = {
    'Rv_max': 0.8,
    'RC': 24 * 720,
    'dt': 3600.0 # Paso de tiempo en segundos (1 hora)
}
dt = physical_params['dt'] # Para acceso rápido

# --- Calcular parámetros dependientes de dt ---
total_time_seconds = days * 24 * 3600
num_steps = int(total_time_seconds / dt)
# Crear un array de tiempo acumulado en horas
time_hours = np.linspace(0, days * 24, num_steps, endpoint=False) # Tiempo total acumulado
# Crear un array de índices para los bucles (si es necesario, aunque run_simulation usa num_steps)
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
ext_series = {}
for label, params in scenarios.items():
    ext_series[label] = generate_sine_series_randomized_interval(
        mean=params['mean'],
        base_amplitude=params['amplitude'],
        num_steps=num_steps,
        dt_seconds=dt,
        time_in_hours=time_hours, # Pasar el tiempo acumulado en horas
        hourly_amplitude_variation=amplitude_variation_magnitude,
        variation_interval_hours=variation_update_interval,
        phase_shift=6.0
    )
    # Asegurarse que la longitud coincida
    if len(ext_series[label]) != num_steps:
        print(f"Advertencia: La longitud de la serie generada ({len(ext_series[label])}) no coincide con num_steps ({num_steps}) para {label}. Ajustando...")
        ext_series[label] = ext_series[label][:num_steps] # Truncar si es más larga
        while len(ext_series[label]) < num_steps: # Rellenar si es más corta (poco probable)
             ext_series[label].append(ext_series[label][-1])


# --------------------------------------------------------------------------
# 6) Simulación y visualización usando Simulator
# --------------------------------------------------------------------------
results = {}

for label, series in ext_series.items():
    print(f"--- Simulando escenario: {label} (dt={dt}s, steps={num_steps}) ---")

    # --- Simulación Fuzzy ---
    print("Ejecutando Fuzzy...")
    # Crear entorno específico para esta simulación
    env_fuzzy = SeriesEnvironment(
        comfort_day=comfort_temp_day,
        comfort_night_cal=comfort_temp_night_cal,
        comfort_night_enf=comfort_temp_night_enf,
        ext_series=series,
        initial_temp_int=initial_temp_int
    )
    # Crear controlador Fuzzy
    ctrl_fuzzy = FuzzyController(fis, defuzz, env_fuzzy)
    # Crear simulador Fuzzy
    simulator_fuzzy = Simulator(env_fuzzy, ctrl_fuzzy, physical_params)
    # Ejecutar simulación
    results_fuzzy = simulator_fuzzy.run_simulation(num_steps, time_hours)


    # --- Simulación ON-OFF ---
    print("Ejecutando ON-OFF...")
    # Crear entorno específico para esta simulación
    # Nota: OnOffController ahora usa target_temp como confort diurno
    # y la lógica interna de OnOffController determina si abrir/cerrar.
    # La predicción diaria del entorno NO es usada por OnOffController.
    env_onoff = SeriesEnvironment(
        comfort_day=comfort_temp_day,
        comfort_night_cal=comfort_temp_night_cal, # No usado por OnOffController
        comfort_night_enf=comfort_temp_night_enf, # No usado por OnOffController
        ext_series=series,
        initial_temp_int=initial_temp_int
    )
     # Crear controlador ON-OFF (pasarle el target de confort diurno)
    ctrl_onoff = OnOffController(env_onoff, comfort_temp_day) # Usa comfort_day como target
    # Crear simulador ON-OFF
    simulator_onoff = Simulator(env_onoff, ctrl_onoff, physical_params)
    # Ejecutar simulación
    results_onoff = simulator_onoff.run_simulation(num_steps, time_hours)


    # Guardar resultados
    results[label] = {
        'fuzzy': results_fuzzy, # Guardar dict completo devuelto por run_simulation
        'on_off': results_onoff # Guardar dict completo devuelto por run_simulation
    }

    # Imprimir promedios directamente desde los resultados
    avg_T_int_f = results_fuzzy['avg_T_int']
    avg_T_int_oo = results_onoff['avg_T_int']
    print(f"Resultados {label}: Fuzzy Avg T_int={avg_T_int_f:.1f}°C, ON-OFF Avg T_int={avg_T_int_oo:.1f}°C")


# --- Visualizar resultados ---
# El plotter espera los datos desempaquetados, así que accedemos a las claves internas

visualizar = True
if(visualizar):
    for label, data in results.items():
        plot_comparison(
            label=label,
            time_hours=time_hours, # Usar el array de tiempo acumulado en horas
            fuzzy_data=data['fuzzy'], # Pasar el diccionario completo
            onoff_data=data['on_off'], # Pasar el diccionario completo
            comfort_temp=comfort_temp_day
        )

    # Visualizar variables lingüísticas
    plot_fuzzy_variable(hora)
    plot_fuzzy_variable(z)
    plot_fuzzy_variable(ventana)

    # Mostrar todas las figuras
    plt.show()
