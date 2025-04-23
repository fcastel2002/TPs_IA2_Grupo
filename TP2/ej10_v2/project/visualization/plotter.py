import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any

def plot_comparison(label: str, 
                    hours: List[int], 
                    fuzzy_data: Dict[str, Any], 
                    onoff_data: Dict[str, Any], 
                    comfort_temp: float, 
                    days: int):
    """
    Genera un gráfico comparativo entre controlador difuso y ON-OFF.
    
    Args:
        label: Etiqueta del escenario
        hours: Lista de horas
        fuzzy_data: Datos del controlador difuso
        onoff_data: Datos del controlador ON-OFF
        comfort_temp: Temperatura de confort
        days: Número de días simulados
    """
    # Desempaquetar resultados
    T_int_f = fuzzy_data['T_int']
    T_ext_f = fuzzy_data['T_ext']
    act_f = fuzzy_data['actions']
    avg_T_int_f = fuzzy_data['avg_T_int']
    avg_T_ext_f = fuzzy_data['avg_T_ext']
    
    T_int_oo = onoff_data['T_int']
    T_ext_oo = onoff_data['T_ext']
    act_oo = onoff_data['actions']
    avg_T_int_oo = onoff_data['avg_T_int']
    avg_T_ext_oo = onoff_data['avg_T_ext']

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # --- Graficar temperaturas ---
    # Exterior (una sola vez)
    ax1.plot(hours, T_ext_f, label='Exterior', linestyle='--', color='tab:orange', alpha=0.7)
    # Interior Fuzzy
    ax1.plot(hours, T_int_f, label=f'Interior Fuzzy (Prom: {avg_T_int_f:.1f}°C)', color='tab:blue', linewidth=2)
    # Interior ON-OFF
    ax1.plot(hours, T_int_oo, label=f'Interior ON-OFF (Prom: {avg_T_int_oo:.1f}°C)', color='tab:red', linestyle='-.', linewidth=1.5)

    # Línea de confort
    ax1.axhline(y=comfort_temp, color='black', linestyle=':', linewidth=1, label=f"Confort ({comfort_temp}°C)")

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
    ax1.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    plt.xlim(0, len(hours) - 1)
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])

def plot_fuzzy_variable(var):
    """
    Genera un gráfico de los conjuntos difusos de una variable lingüística.
    
    Args:
        var: Variable lingüística a graficar
    """
    u_min, u_max = var.universe
    xs = np.linspace(u_min, u_max, 500)
    plt.figure(figsize=(8, 4))
    for name, fs in var.sets.items():
        ys = [fs.membership(x) for x in xs]
        plt.plot(xs, ys, label=name)
    plt.title(f"Variable Lingüística: '{var.name}'")
    plt.xlabel("Universo de Discurso")
    plt.ylabel("Grado de pertenencia μ(x)")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()