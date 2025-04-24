import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any

def plot_comparison(label: str,
                    time_hours: List[float], # Corregido tipo a List[float]
                    fuzzy_data: Dict[str, Any],
                    onoff_data: Dict[str, Any],
                    comfort_temp: float,
                    fig=None, ax1=None, ax2=None # ax2 es el eje secundario
                    ):
    """
    Genera un gráfico comparativo entre controlador difuso y ON-OFF.
    Si se pasan fig, ax1, ax2, los utiliza; si no, los crea.
    Restaura la cuadrícula completa y las etiquetas de hora en el eje X.

    Args:
        label: Etiqueta del escenario
        time_hours: Lista de horas (como floats)
        fuzzy_data: Datos del controlador difuso
        onoff_data: Datos del controlador ON-OFF
        comfort_temp: Temperatura de confort
        fig: Figura Matplotlib existente (opcional).
        ax1: Ejes principales existentes (opcional).
        ax2: Ejes secundarios existentes (twinx de ax1) (opcional).
    """
    # Desempaquetar resultados
    T_int_f = fuzzy_data['T_int']
    T_ext_f = fuzzy_data['T_ext']
    act_f = fuzzy_data['actions']
    avg_T_int_f = fuzzy_data['avg_T_int']
    z_f = fuzzy_data.get('Z', None) # Aún se maneja por si acaso

    T_int_oo = onoff_data['T_int']
    act_oo = onoff_data['actions']
    avg_T_int_oo = onoff_data['avg_T_int']

    # Determinar si se necesita crear figura y ejes
    create_figure = (fig is None or ax1 is None)

    # --- Lógica principal del gráfico (sin Z) ---
    if z_f is None:
        if create_figure:
            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()
        elif ax2 is None:
             print("Advertencia (plotter): ax2 no fue proporcionado, creando uno nuevo.")
             ax2 = ax1.twinx()
        # else: Usar fig, ax1, ax2 pasados

        # --- Graficar temperaturas (ax1) ---
        ax1.plot(time_hours, T_ext_f, label='Exterior', linestyle='--', color='tab:orange', alpha=0.7)
        ax1.plot(time_hours, T_int_f, label=f'Interior Fuzzy (Prom: {avg_T_int_f:.1f}°C)', color='tab:blue', linewidth=2)
        ax1.plot(time_hours, T_int_oo, label=f'Interior ON-OFF (Prom: {avg_T_int_oo:.1f}°C)', color='tab:red', linestyle='-.', linewidth=1.5)
        ax1.axhline(y=comfort_temp, color='black', linestyle=':', linewidth=1, label=f"Confort ({comfort_temp}°C)")

        # --- Graficar acciones (ax2) ---
        ax2.plot(time_hours, [a/100.0 for a in act_f], label='Apertura Fuzzy', color='tab:green', drawstyle='steps-post', alpha=0.8, linewidth=1.5)
        ax2.plot(time_hours, [a/100.0 for a in act_oo], label='Apertura ON-OFF', color='tab:purple', drawstyle='steps-post', alpha=0.6, linewidth=1.0)
        ax2.set_ylim(-0.05, 1.05)

        # --- Colorear zonas día/noche (ax1) ---
        min_hour, max_hour = min(time_hours), max(time_hours)
        start_day = int(min_hour // 24)
        end_day = int(max_hour // 24)
        for day_num in range(start_day, end_day + 1):
            day_start_hour = day_num * 24
            # Noche AM
            start = max(min_hour, day_start_hour + 0)
            end = min(max_hour, day_start_hour + 8.5)
            if end > start: ax1.axvspan(start, end, color='blue', alpha=0.1, lw=0)
            # Día
            start = max(min_hour, day_start_hour + 8.5)
            end = min(max_hour, day_start_hour + 20.5)
            if end > start: ax1.axvspan(start, end, color='yellow', alpha=0.15, lw=0)
            # Noche PM
            start = max(min_hour, day_start_hour + 20.5)
            end = min(max_hour, day_start_hour + 24)
            if end > start: ax1.axvspan(start, end, color='blue', alpha=0.1, lw=0)

        # --- Etiquetas y Título ---
        ax1.set_xlabel('Hora (h)')
        ax1.set_ylabel('Temperatura (°C)')
        ax2.set_ylabel('Apertura ventana (fracción)')
        ax1.set_title(f'Comparativa: {int(max(time_hours))}h – Esc. {label}')

        # --- Cuadrícula Completa (Restaurado) ---
        ax1.grid(True, which='both', axis='both', linestyle=':', alpha=0.6)
        # También aplicar al eje secundario si se desea (puede ser mucho)
        # ax2.grid(True, which='both', axis='y', linestyle=':', alpha=0.6) # Grid Y para ax2 opcional

        # --- Ticks y Etiquetas Eje X (solo horas enteras) ---
        if time_hours is not None and len(time_hours) > 0:
            ax1.set_xlim(min(time_hours), max(time_hours))
            # Mostrar solo ticks en horas enteras
            min_hour = int(np.floor(min(time_hours)))
            max_hour = int(np.ceil(max(time_hours)))
            hour_ticks = np.arange(min_hour, max_hour + 1, 1)
            ax1.set_xticks(hour_ticks)
            ax1.set_xticklabels([str(h) for h in hour_ticks], rotation=90, fontsize=8)

        # --- Leyenda Combinada ---
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        if fig is not None:
             # Colocar leyenda debajo, ajustando bbox_to_anchor
            fig.legend(h1 + h2, l1 + l2, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0))
        else:
             ax1.legend(h1 + h2, l1 + l2, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.2)) # Ajustar si no hay fig

        # --- Ajustes finales ---
        if create_figure:
            try:
                 # Intenta ajustar el layout para evitar solapamientos
                 fig.tight_layout(rect=[0, 0.05, 1, 0.95]) # Ajustar rect para leyenda inferior
            except Exception:
                 print("Advertencia: No se pudo aplicar tight_layout.")
                 pass

    # --- Lógica para gráfico con Z (si se llegara a usar, también necesita restaurar grid/ticks) ---
    elif z_f is not None:
        if create_figure:
            fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
            ax2 = ax1.twinx()
        elif ax2 is None or not hasattr(fig.axes, '__len__') or len(fig.axes) < 2: # Verificar si existe ax3 implicitamente
             print("Error (plotter): Se requiere fig, ax1, ax2, y ax3 para el gráfico con Z.")
             return
        else:
             ax3 = fig.axes[1] # Asumir que ax3 es el segundo eje creado

        # --- Temperaturas y aperturas (ax1, ax2) ---
        # (Mismo código de ploteo que antes para ax1 y ax2)
        ax1.plot(time_hours, T_ext_f, label='Exterior', linestyle='--', color='tab:orange', alpha=0.7)
        ax1.plot(time_hours, T_int_f, label=f'Interior Fuzzy (Prom: {avg_T_int_f:.1f}°C)', color='tab:blue', linewidth=2)
        ax1.plot(time_hours, T_int_oo, label=f'Interior ON-OFF (Prom: {avg_T_int_oo:.1f}°C)', color='tab:red', linestyle='-.', linewidth=1.5)
        ax1.axhline(y=comfort_temp, color='black', linestyle=':', linewidth=1, label=f"Confort ({comfort_temp}°C)")
        ax1.set_ylabel('Temperatura (°C)')
        ax1.set_title(f'Comparativa (con Z): {int(max(time_hours))}h – Esc. {label}')

        ax2.plot(time_hours, [a/100.0 for a in act_f], label='Apertura Fuzzy', color='tab:green', alpha=0.8, linewidth=1.5)
        ax2.plot(time_hours, [a/100.0 for a in act_oo], label='Apertura ON-OFF', color='tab:purple', alpha=0.6, linewidth=1.0)
        ax2.set_ylim(-0.05, 1.05)
        ax2.set_ylabel('Apertura ventana (fracción)')

        # --- Variable Z (ax3) ---
        ax3.plot(time_hours, z_f, label='Z (Error Control)', color='tab:brown')
        ax3.set_ylabel('Z')
        ax3.set_xlabel('Hora (h)')

        # --- Cuadrícula Completa (Restaurado) ---
        ax1.grid(True, which='both', axis='both', linestyle=':', alpha=0.6)
        # ax2.grid(True, which='both', axis='y', linestyle=':', alpha=0.6) # Opcional para ax2
        ax3.grid(True, which='both', axis='both', linestyle=':', alpha=0.6)

        # --- Ticks y Etiquetas Eje X (solo horas enteras) ---
        if time_hours is not None and len(time_hours) > 0:
            ax1.set_xlim(min(time_hours), max(time_hours))
            min_hour = int(np.floor(min(time_hours)))
            max_hour = int(np.ceil(max(time_hours)))
            hour_ticks = np.arange(min_hour, max_hour + 1, 1)
            ax1.set_xticks(hour_ticks)
            tick_labels = [str(h) for h in hour_ticks]
            ax1.set_xticklabels(tick_labels, rotation=90, fontsize=8)
            plt.setp(ax1.get_xticklabels(), visible=False)
            ax3.set_xticks(hour_ticks)
            ax3.set_xticklabels(tick_labels, rotation=90, fontsize=8)
            plt.setp(ax3.get_xticklabels(), visible=True)

        # --- Leyenda Combinada ---
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        if fig is not None:
             # Colocar leyenda ARRIBA, centrada, justo debajo del título posible
             # Ajustar bbox_to_anchor y rect en tight_layout para espacio
             fig.legend(h1 + h2, l1 + l2, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 0.90)) # <--- MODIFICADO (posición y Y en bbox)
        else:
             # Fallback si no hay figura (poco probable desde GUI)
             ax1.legend(h1 + h2, l1 + l2, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.1)) # Moverla arriba del eje

        # --- Ajustes finales ---
        if create_figure:
            try:
                 # Intenta ajustar el layout para evitar solapamientos
                 # Dejar un poco más de espacio arriba (disminuir top en rect) para la leyenda
                 fig.tight_layout(rect=[0, 0, 1, 0.94]) # <--- MODIFICADO (ajustar top)
            except Exception as e: # Capturar excepción específica si es posible
                 print(f"Advertencia: No se pudo aplicar tight_layout. Error: {e}")
                 pass

# (La función plot_fuzzy_variable permanece igual)
def plot_fuzzy_variable(var):
    """
    Genera un gráfico de los conjuntos difusos de una variable lingüística.

    Args:
        var: Variable lingüística a graficar
    """
    u_min, u_max = var.universe
    xs = np.linspace(u_min, u_max, 500)
    fig, ax = plt.subplots(figsize=(8, 4)) # Usar fig, ax
    for name, fs in var.sets.items():
        ys = [fs.membership(x) for x in xs]
        ax.plot(xs, ys, label=name)
    ax.set_title(f"Variable Lingüística: '{var.name}'")
    ax.set_xlabel("Universo de Discurso")
    ax.set_ylabel("Grado de pertenencia μ(x)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)
    fig.tight_layout()