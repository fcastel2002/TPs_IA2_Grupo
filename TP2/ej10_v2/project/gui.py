# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

# Importaciones de tu proyecto
# Importar directamente las funciones de simulación existentes
from main import simulate_fuzzy, simulate_on_off
from simulation.data_generator import generate_sine_series_randomized_interval

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Control Difuso")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables para almacenar resultados
        self.results = {}
        self.current_scenario = None
        
        # Configuración por defecto
        self.config = {
            'comfort': {
                'day': 25.0,
                'night_cal': 50.0,
                'night_enf': 5.0
            },
            'physical': {
                'Rv_max': 0.8,
                'RC': 24 * 720,
                'dt': 3600.0
            },
            'simulation': {
                'days': 3,
                'initial_temp': 25.0,
                'variation_interval': 3,
                'amplitude_variation': 0.4
            },
            'scenarios': {
                'Bajo': {'mean': 15.0, 'amplitude': 2.0},
                'Medio': {'mean': 24.0, 'amplitude': 5.0},
                'Alto': {'mean': 30.0, 'amplitude': 8.0}
            }
        }
        
        # Crear variables Tkinter para los parámetros
        self.create_variables()
        
        # Crear la interfaz
        self.create_widgets()
        
        # Actualizar los valores iniciales en la interfaz
        self.update_gui_from_config()

    def create_variables(self):
        # Variables para parámetros de confort
        self.comfort_day_var = tk.DoubleVar(value=self.config['comfort']['day'])
        self.comfort_night_cal_var = tk.DoubleVar(value=self.config['comfort']['night_cal'])
        self.comfort_night_enf_var = tk.DoubleVar(value=self.config['comfort']['night_enf'])
        
        # Variables para parámetros físicos
        self.rv_max_var = tk.DoubleVar(value=self.config['physical']['Rv_max'])
        self.rc_var = tk.DoubleVar(value=self.config['physical']['RC'])
        self.dt_var = tk.DoubleVar(value=self.config['physical']['dt'])
        
        # Variables para parámetros de simulación
        self.days_var = tk.IntVar(value=self.config['simulation']['days'])
        self.initial_temp_var = tk.DoubleVar(value=self.config['simulation']['initial_temp'])
        
        # Variables para escenarios
        self.scenario_vars = {}
        for scenario, params in self.config['scenarios'].items():
            self.scenario_vars[scenario] = {
                'mean': tk.DoubleVar(value=params['mean']),
                'amplitude': tk.DoubleVar(value=params['amplitude'])
            }
        
        # Variable para selección de escenario
        self.selected_scenario = tk.StringVar(value="Medio")

    def create_widgets(self):
        # Crear un panel principal dividido en dos partes
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo para configuración
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Panel derecho para resultados
        right_frame = ttk.Frame(main_paned, width=800)
        main_paned.add(right_frame, weight=2)
        
        # Configurar el panel izquierdo (configuración)
        self.setup_config_panel(left_frame)
        
        # Configurar el panel derecho (resultados)
        self.setup_results_panel(right_frame)

    def setup_config_panel(self, parent):
        # Crear un canvas con scroll para la configuración
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        ttk.Label(scrollable_frame, text="Configuración", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Sección: Parámetros de Confort
        comfort_frame = ttk.LabelFrame(scrollable_frame, text="Parámetros de Confort")
        comfort_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(comfort_frame, text="Temperatura de confort (día):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_day_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(comfort_frame, text="Temperatura de confort (noche, calefacción):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_night_cal_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(comfort_frame, text="Temperatura de confort (noche, enfriamiento):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_night_enf_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        
        # Sección: Parámetros Físicos
        physical_frame = ttk.LabelFrame(scrollable_frame, text="Parámetros Físicos")
        physical_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(physical_frame, text="Resistencia máxima de ventilación (Rv_max):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.rv_max_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(physical_frame, text="Resistencia-Capacitancia (RC):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.rc_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(physical_frame, text="Paso de tiempo (dt):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.dt_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(physical_frame, text="segundos").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        
        # Sección: Parámetros de Simulación
        sim_frame = ttk.LabelFrame(scrollable_frame, text="Parámetros de Simulación")
        sim_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(sim_frame, text="Duración de la simulación:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(sim_frame, textvariable=self.days_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(sim_frame, text="días").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(sim_frame, text="Temperatura interior inicial:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(sim_frame, textvariable=self.initial_temp_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(sim_frame, text="°C").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        
        # Sección: Escenarios
        scenarios_frame = ttk.LabelFrame(scrollable_frame, text="Escenarios de Temperatura Exterior")
        scenarios_frame.pack(fill="x", padx=10, pady=5)
        
        row = 0
        for scenario in self.config['scenarios'].keys():
            ttk.Label(scenarios_frame, text=f"Escenario {scenario}:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
            
            ttk.Label(scenarios_frame, text="Temperatura media:").grid(row=row, column=0, sticky="w", padx=20, pady=2)
            ttk.Entry(scenarios_frame, textvariable=self.scenario_vars[scenario]['mean'], width=10).grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(scenarios_frame, text="°C").grid(row=row, column=2, sticky="w", padx=5, pady=2)
            row += 1
            
            ttk.Label(scenarios_frame, text="Amplitud:").grid(row=row, column=0, sticky="w", padx=20, pady=2)
            ttk.Entry(scenarios_frame, textvariable=self.scenario_vars[scenario]['amplitude'], width=10).grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(scenarios_frame, text="°C").grid(row=row, column=2, sticky="w", padx=5, pady=2)
            row += 1
        
        # Sección: Selección de escenario y botones
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Escenario a simular:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        scenario_combo = ttk.Combobox(control_frame, textvariable=self.selected_scenario, 
                                      values=list(self.config['scenarios'].keys()), state="readonly", width=15)
        scenario_combo.grid(row=0, column=1, padx=5, pady=2)
        
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Actualizar Configuración", command=self.update_config_from_gui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Ejecutar Simulación", command=self.run_simulation).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Restablecer Valores Predeterminados", command=self.reset_to_defaults).pack(side="left", padx=5)

    def setup_results_panel(self, parent):
        # Título
        ttk.Label(parent, text="Resultados", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame para selección de escenario (si hay múltiples resultados)
        self.results_control_frame = ttk.Frame(parent)
        self.results_control_frame.pack(fill="x", padx=10, pady=5)
        
        # Frame para gráficos
        self.plot_frame = ttk.Frame(parent)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Mensaje inicial
        ttk.Label(self.plot_frame, text="Ejecute una simulación para ver los resultados", font=("Arial", 10)).pack(pady=50)

    def update_gui_from_config(self):
        # Actualizar variables de confort
        self.comfort_day_var.set(self.config['comfort']['day'])
        self.comfort_night_cal_var.set(self.config['comfort']['night_cal'])
        self.comfort_night_enf_var.set(self.config['comfort']['night_enf'])
        
        # Actualizar variables físicas
        self.rv_max_var.set(self.config['physical']['Rv_max'])
        self.rc_var.set(self.config['physical']['RC'])
        self.dt_var.set(self.config['physical']['dt'])
        
        # Actualizar variables de simulación
        self.days_var.set(self.config['simulation']['days'])
        self.initial_temp_var.set(self.config['simulation']['initial_temp'])
        
        # Actualizar variables de escenarios
        for scenario, params in self.config['scenarios'].items():
            self.scenario_vars[scenario]['mean'].set(params['mean'])
            self.scenario_vars[scenario]['amplitude'].set(params['amplitude'])

    def update_config_from_gui(self):
        try:
            # Actualizar configuración de confort
            self.config['comfort']['day'] = self.comfort_day_var.get()
            self.config['comfort']['night_cal'] = self.comfort_night_cal_var.get()
            self.config['comfort']['night_enf'] = self.comfort_night_enf_var.get()
            
            # Actualizar configuración física
            self.config['physical']['Rv_max'] = self.rv_max_var.get()
            self.config['physical']['RC'] = self.rc_var.get()
            self.config['physical']['dt'] = self.dt_var.get()
            
            # Actualizar configuración de simulación
            self.config['simulation']['days'] = self.days_var.get()
            self.config['simulation']['initial_temp'] = self.initial_temp_var.get()
            
            # Actualizar configuración de escenarios
            for scenario in self.config['scenarios'].keys():
                self.config['scenarios'][scenario]['mean'] = self.scenario_vars[scenario]['mean'].get()
                self.config['scenarios'][scenario]['amplitude'] = self.scenario_vars[scenario]['amplitude'].get()
            
            messagebox.showinfo("Configuración", "Configuración actualizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la configuración: {str(e)}")

    def reset_to_defaults(self):
        # Restablecer a valores predeterminados
        self.config = {
            'comfort': {
                'day': 25.0,
                'night_cal': 50.0,
                'night_enf': 5.0
            },
            'physical': {
                'Rv_max': 0.8,
                'RC': 24 * 720,
                'dt': 3600.0
            },
            'simulation': {
                'days': 3,
                'initial_temp': 25.0,
                'variation_interval': 3,
                'amplitude_variation': 0.4
            },
            'scenarios': {
                'Bajo': {'mean': 15.0, 'amplitude': 2.0},
                'Medio': {'mean': 24.0, 'amplitude': 5.0},
                'Alto': {'mean': 30.0, 'amplitude': 8.0}
            }
        }
        self.update_gui_from_config()
        messagebox.showinfo("Configuración", "Valores restablecidos a los predeterminados")

    def run_simulation(self):
        # Actualizar configuración desde la GUI
        self.update_config_from_gui()
        
        # Obtener el escenario seleccionado
        scenario = self.selected_scenario.get()
        self.current_scenario = scenario
        
        # Mostrar mensaje de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Progreso")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Ejecutando simulación para escenario {scenario}...").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode="indeterminate")
        progress.pack(fill="x", padx=20, pady=10)
        progress.start()
        
        # Ejecutar simulación en un hilo separado
        def run_in_thread():
            try:
                # Guardar valores originales
                original_rv_max = globals().get('Rv_max', 0.8)
                original_rc = globals().get('RC', 24 * 720)
                original_dt = globals().get('dt', 3600.0)
                
                # Modificar valores globales para la simulación
                globals()['Rv_max'] = self.config['physical']['Rv_max']
                globals()['RC'] = self.config['physical']['RC']
                globals()['dt'] = self.config['physical']['dt']
                
                # Generar serie de temperatura
                ext_series = generate_sine_series_randomized_interval(
                    mean=self.config['scenarios'][scenario]['mean'],
                    base_amplitude=self.config['scenarios'][scenario]['amplitude'],
                    days=self.config['simulation']['days'],
                    hourly_amplitude_variation=self.config['simulation']['amplitude_variation'],
                    variation_interval_hours=self.config['simulation']['variation_interval'],
                    phase_shift=6.0
                )
                
                # Definir horas
                hours = list(range(len(ext_series)))
                
                # Ejecutar simulaciones usando las funciones existentes
                T_int_f, T_ext_f, act_f, avg_T_int_f, avg_T_ext_f = simulate_fuzzy(ext_series)
                
                T_int_oo, T_ext_oo, act_oo, avg_T_int_oo, avg_T_ext_oo = simulate_on_off(
                    ext_series=ext_series,
                    hours=hours,
                    target_temp=self.config['comfort']['day'],
                    initial_temp_int=self.config['simulation']['initial_temp'],
                    comfort_night_cal=self.config['comfort']['night_cal'],
                    comfort_night_enf=self.config['comfort']['night_enf']
                )
                
                # Restaurar valores originales
                globals()['Rv_max'] = original_rv_max
                globals()['RC'] = original_rc
                globals()['dt'] = original_dt
                
                # Guardar resultados
                self.results[scenario] = {
                    'hours': hours,
                    'fuzzy': {
                        'T_int': T_int_f,
                        'T_ext': T_ext_f,
                        'actions': act_f,
                        'avg_T_int': avg_T_int_f,
                        'avg_T_ext': avg_T_ext_f
                    },
                    'on_off': {
                        'T_int': T_int_oo,
                        'T_ext': T_ext_oo,
                        'actions': act_oo,
                        'avg_T_int': avg_T_int_oo,
                        'avg_T_ext': avg_T_ext_oo
                    }
                }
                
                # Actualizar la interfaz en el hilo principal
                self.root.after(0, lambda: self.update_results_display(scenario))
                self.root.after(0, lambda: progress_window.destroy())
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error en la simulación: {str(e)}"))
                self.root.after(0, lambda: progress_window.destroy())
        
        threading.Thread(target=run_in_thread).start()

    def update_results_display(self, scenario):
        # Limpiar el frame de gráficos
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Limpiar el frame de control de resultados
        for widget in self.results_control_frame.winfo_children():
            widget.destroy()
        
        # Si hay múltiples resultados, mostrar selector
        if len(self.results) > 1:
            ttk.Label(self.results_control_frame, text="Mostrar resultados para:").pack(side="left", padx=5)
            scenario_combo = ttk.Combobox(self.results_control_frame, 
                                         values=[s for s in self.results.keys()], 
                                         state="readonly", width=15)
            scenario_combo.pack(side="left", padx=5)
            scenario_combo.set(scenario)
            scenario_combo.bind("<<ComboboxSelected>>", 
                               lambda e: self.update_results_display(scenario_combo.get()))
        
        # Verificar si hay resultados para este escenario
        if scenario not in self.results:
            ttk.Label(self.plot_frame, text=f"No hay resultados para el escenario {scenario}. Ejecute una simulación primero.").pack(pady=50)
            return
        
        # Obtener datos
        data = self.results[scenario]
        hours = data['hours']
        fuzzy_data = data['fuzzy']
        onoff_data = data['on_off']
        
        # Crear figura
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        
        # Graficar temperaturas
        ax1.plot(hours, fuzzy_data['T_ext'], label='Exterior', linestyle='--', color='tab:orange', alpha=0.7)
        ax1.plot(hours, fuzzy_data['T_int'], label=f'Interior Fuzzy (Prom: {fuzzy_data["avg_T_int"]:.1f}°C)', color='tab:blue', linewidth=2)
        ax1.plot(hours, onoff_data['T_int'], label=f'Interior ON-OFF (Prom: {onoff_data["avg_T_int"]:.1f}°C)', color='tab:red', linestyle='-.', linewidth=1.5)
        
        # Línea de confort
        ax1.axhline(y=self.config['comfort']['day'], color='black', linestyle=':', linewidth=1, label=f"Confort ({self.config['comfort']['day']}°C)")
        
        # Graficar acciones
        ax2.plot(hours, [a/100.0 for a in fuzzy_data['actions']], label='Apertura Fuzzy', color='tab:green', drawstyle='steps-post', alpha=0.8, linewidth=1.5)
        ax2.plot(hours, [a/100.0 for a in onoff_data['actions']], label='Apertura ON-OFF', color='tab:purple', drawstyle='steps-post', alpha=0.6, linewidth=1.0)
        
        # Ajustes
        ax2.set_ylim(-0.05, 1.05)
        
        # Colorear zonas día/noche
        for i in range(0, len(hours), 24):
            if i + 20.5 < len(hours):
                ax1.axvspan(i + 8.5, i + 20.5, color='yellow', alpha=0.15, lw=0)
            if i + 24 < len(hours):
                ax1.axvspan(i + 20.5, i + 24, color='blue', alpha=0.1, lw=0)
            if i + 8.5 < len(hours):
                ax1.axvspan(i, i + 8.5, color='blue', alpha=0.1, lw=0)
        
        # Etiquetas
        ax1.set_xlabel('Hora (h)')
        ax1.set_ylabel('Temperatura (°C)')
        ax2.set_ylabel('Apertura ventana (fracción)')
        ax1.tick_params(axis='y')
        ax2.tick_params(axis='y')
        ax1.set_title(f'Comparativa Fuzzy vs ON-OFF: {self.config["simulation"]["days"]} días – Serie {scenario}')
        ax1.grid(True, axis='y', linestyle=':', alpha=0.6)
        
        # Unir leyendas
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        # Ajustar límites
        ax1.set_xlim(0, len(hours) - 1)
        
        # Mostrar gráfico en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Añadir información de resumen
        summary_frame = ttk.Frame(self.plot_frame)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(summary_frame, text=f"Escenario: {scenario}").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(summary_frame, text=f"Temperatura media exterior: {fuzzy_data['avg_T_ext']:.1f}°C").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(summary_frame, text=f"Temperatura media interior (Fuzzy): {fuzzy_data['avg_T_int']:.1f}°C").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(summary_frame, text=f"Temperatura media interior (ON-OFF): {onoff_data['avg_T_int']:.1f}°C").grid(row=1, column=1, sticky="w", padx=5)
        
        # Calcular diferencia con temperatura de confort
        diff_fuzzy = abs(fuzzy_data['avg_T_int'] - self.config['comfort']['day'])
        diff_onoff = abs(onoff_data['avg_T_int'] - self.config['comfort']['day'])
        
        ttk.Label(summary_frame, text=f"Desviación de confort (Fuzzy): {diff_fuzzy:.1f}°C").grid(row=2, column=0, sticky="w", padx=5)
        ttk.Label(summary_frame, text=f"Desviación de confort (ON-OFF): {diff_onoff:.1f}°C").grid(row=2, column=1, sticky="w", padx=5)
        
        # Determinar el mejor controlador
        if diff_fuzzy < diff_onoff:
            mejor = "Fuzzy"
            diferencia = diff_onoff - diff_fuzzy
        elif diff_onoff < diff_fuzzy:
            mejor = "ON-OFF"
            diferencia = diff_fuzzy - diff_onoff
        else:
            mejor = "Ambos iguales"
            diferencia = 0
        
        ttk.Label(summary_frame, text=f"Mejor controlador: {mejor} (diferencia de {diferencia:.1f}°C)").grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()