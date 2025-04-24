import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

# Importaciones de tu proyecto
# Importar Clases necesarias
from environment.series_environment import SeriesEnvironment
from control.fuzzy_controller import FuzzyController
from control.on_off_controller import OnOffController
from simulation.simulator import Simulator # <--- Importar Simulator
from simulation.data_generator import generate_sine_series_smooth
# Importar elementos para Fuzzy (FIS, Defuzzifier) - Asumiendo que están accesibles
# Necesitamos la configuración de FIS y Defuzzifier como en main.py
# Podríamos importarlos desde main o definirlos/cargarlos aquí.
# Por simplicidad, importaremos desde main (requiere que main.py no ejecute plt.show() automáticamente si se importa)
# Alternativamente, mover la definición de FIS/Defuzzifier a un archivo de configuración.
try:
    # Intentar importar las instancias configuradas desde main
    from main import fis, defuzz, comfort_temp_day as default_comfort_day
except ImportError:
    # Fallback o error si main.py no se puede importar limpiamente
    messagebox.showerror("Error de Importación", "No se pudo importar la configuración FIS/Defuzz desde main.py")
    exit()
# Importar función de ploteo
from visualization.plotter import plot_comparison


class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Control Difuso")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Variables para almacenar resultados
        self.results = {}
        self.current_scenario = None
        self.time_hours_current_sim = None # Para guardar el eje de tiempo

        # Configuración por defecto inicial
        self.config = {
            'comfort': {
                'day': 25.0,
                'night_cal': 50.0,
                'night_enf': 5.0
            },
            'physical': {
                'Rv_max': 0.1,
                'RC': 24 * 720,
                'dt': 3600.0
            },
            'simulation': {
                'days': 3,
                'initial_temp': 23.0,
                'variation_interval': 3,
                'amplitude_variation': 0.4
            },
            'scenarios': {
                'Bajo': {'mean': 15.0, 'amplitude': 2.0},
                'Medio': {'mean': 22.0, 'amplitude': 4.0},
                'Alto': {'mean': 30.0, 'amplitude': 8.0}
            }
        }
        self.config_init = self.config

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

        ttk.Label(comfort_frame, text="T. confort día:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_day_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=0, column=2, sticky="w", padx=5, pady=2)

        ttk.Label(comfort_frame, text="T. confort noche (calor):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_night_cal_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=1, column=2, sticky="w", padx=5, pady=2)

        ttk.Label(comfort_frame, text="T. confort noche (frío):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(comfort_frame, textvariable=self.comfort_night_enf_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(comfort_frame, text="°C").grid(row=2, column=2, sticky="w", padx=5, pady=2)

        # Sección: Parámetros Físicos
        physical_frame = ttk.LabelFrame(scrollable_frame, text="Parámetros Físicos")
        physical_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(physical_frame, text="Rv_max:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.rv_max_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(physical_frame, text="RC:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.rc_var, width=10).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(physical_frame, text="dt (paso tiempo):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(physical_frame, textvariable=self.dt_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(physical_frame, text="s").grid(row=2, column=2, sticky="w", padx=5, pady=2)

        # Sección: Parámetros de Simulación
        sim_frame = ttk.LabelFrame(scrollable_frame, text="Parámetros de Simulación")
        sim_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(sim_frame, text="Duración:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(sim_frame, textvariable=self.days_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(sim_frame, text="días").grid(row=0, column=2, sticky="w", padx=5, pady=2)

        ttk.Label(sim_frame, text="T. interior inicial:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(sim_frame, textvariable=self.initial_temp_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(sim_frame, text="°C").grid(row=1, column=2, sticky="w", padx=5, pady=2)

        # Sección: Escenarios
        scenarios_frame = ttk.LabelFrame(scrollable_frame, text="Escenarios T. Exterior")
        scenarios_frame.pack(fill="x", padx=10, pady=5)

        row = 0
        for scenario in self.config['scenarios'].keys():
            ttk.Label(scenarios_frame, text=f"{scenario}:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1

            ttk.Label(scenarios_frame, text="  Media:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Entry(scenarios_frame, textvariable=self.scenario_vars[scenario]['mean'], width=8).grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(scenarios_frame, text="°C").grid(row=row, column=2, sticky="w", padx=2, pady=2)
            row += 1

            ttk.Label(scenarios_frame, text="  Amplitud:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Entry(scenarios_frame, textvariable=self.scenario_vars[scenario]['amplitude'], width=8).grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(scenarios_frame, text="°C").grid(row=row, column=2, sticky="w", padx=2, pady=2)
            row += 1

        # Sección: Selección de escenario y botones
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(control_frame, text="Simular Escenario:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        scenario_combo = ttk.Combobox(control_frame, textvariable=self.selected_scenario,
                                      values=list(self.config['scenarios'].keys()), state="readonly", width=15)
        scenario_combo.grid(row=0, column=1, padx=5, pady=2)

        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=10, pady=10, side=tk.BOTTOM) # Colocar botones abajo

        ttk.Button(button_frame, text="Actualizar Config.", command=self.update_config_from_gui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Ejecutar Simulación", command=self.run_simulation_thread).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_to_defaults).pack(side="left", padx=5)


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
        self.plot_label = ttk.Label(self.plot_frame, text="Configure y ejecute una simulación.", font=("Arial", 10))
        self.plot_label.pack(pady=50)
        self.plot_canvas = None # Para mantener referencia al canvas del gráfico


    def update_gui_from_config(self):
        # Actualizar variables de confort, físicas, simulación y escenarios
        self.comfort_day_var.set(self.config['comfort']['day'])
        self.comfort_night_cal_var.set(self.config['comfort']['night_cal'])
        self.comfort_night_enf_var.set(self.config['comfort']['night_enf'])
        self.rv_max_var.set(self.config['physical']['Rv_max'])
        self.rc_var.set(self.config['physical']['RC'])
        self.dt_var.set(self.config['physical']['dt'])
        self.days_var.set(self.config['simulation']['days'])
        self.initial_temp_var.set(self.config['simulation']['initial_temp'])
        for scenario, params in self.config['scenarios'].items():
            self.scenario_vars[scenario]['mean'].set(params['mean'])
            self.scenario_vars[scenario]['amplitude'].set(params['amplitude'])

    def update_config_from_gui(self):
        try:
            # Leer valores de las variables Tk y actualizar self.config
            self.config['comfort']['day'] = self.comfort_day_var.get()
            self.config['comfort']['night_cal'] = self.comfort_night_cal_var.get()
            self.config['comfort']['night_enf'] = self.comfort_night_enf_var.get()
            self.config['physical']['Rv_max'] = self.rv_max_var.get()
            self.config['physical']['RC'] = self.rc_var.get()
            self.config['physical']['dt'] = self.dt_var.get()
            if self.config['physical']['dt'] <= 0:
                 raise ValueError("dt debe ser positivo")
            self.config['simulation']['days'] = self.days_var.get()
            self.config['simulation']['initial_temp'] = self.initial_temp_var.get()
            for scenario in self.config['scenarios'].keys():
                self.config['scenarios'][scenario]['mean'] = self.scenario_vars[scenario]['mean'].get()
                self.config['scenarios'][scenario]['amplitude'] = self.scenario_vars[scenario]['amplitude'].get()

            print("Configuración actualizada desde GUI.") # Para depuración
            return True # Indicar éxito
        except Exception as e:
            messagebox.showerror("Error de Configuración", f"Error al leer los parámetros: {str(e)}\nAsegúrese de que todos los valores sean numéricos.")
            return False # Indicar fallo

    def reset_to_defaults(self):
        # Restablecer self.config a los valores originales y actualizar GUI
        self.config = self.config_init.copy() # Copia profunda de la configuración inicial
        self.update_gui_from_config()
        messagebox.showinfo("Configuración", "Valores restablecidos a los predeterminados.")

    def run_simulation_thread(self):
         # Primero, intentar actualizar la configuración desde la GUI
        if not self.update_config_from_gui():
            return # No continuar si hay error en la configuración

        # Mostrar ventana de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Progreso")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set() # Bloquear interacción con ventana principal
        ttk.Label(progress_window, text=f"Ejecutando simulación...").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode="indeterminate")
        progress.pack(fill="x", padx=20, pady=10)
        progress.start()

        # Crear y empezar hilo
        sim_thread = threading.Thread(target=self._execute_simulation, args=(progress_window,))
        sim_thread.start()

    def _execute_simulation(self, progress_window):
        """Función ejecutada en el hilo para no bloquear la GUI."""
        try:
            scenario = self.selected_scenario.get()
            print(f"Iniciando simulación para escenario: {scenario}") # Debug

            # --- Preparación Común ---
            cfg_phys = self.config['physical']
            cfg_sim = self.config['simulation']
            cfg_comfort = self.config['comfort']
            cfg_scenario = self.config['scenarios'][scenario]

            dt = cfg_phys['dt']
            total_time_seconds = cfg_sim['days'] * 24 * 3600
            num_steps = int(total_time_seconds / dt)
            time_hours = np.linspace(0, cfg_sim['days'] * 24, num_steps, endpoint=False)
            self.time_hours_current_sim = time_hours # Guardar para el plot

            print(f"Parámetros: dt={dt}, days={cfg_sim['days']}, num_steps={num_steps}") # Debug

            # Generar serie de temperatura exterior
            ext_series = generate_sine_series_smooth(
                mean=cfg_scenario['mean'],
                base_amplitude=cfg_scenario['amplitude'],
                num_steps=num_steps,
                dt_seconds=dt,
                time_in_hours=time_hours,
                hourly_amplitude_variation=cfg_sim['amplitude_variation'],
                variation_interval_hours=cfg_sim['variation_interval'],
                phase_shift=6.0
            )
            # Asegurar longitud correcta
            if len(ext_series) != num_steps:
                 ext_series = ext_series[:num_steps]
                 while len(ext_series) < num_steps: ext_series.append(ext_series[-1])

            initial_temp = cfg_sim['initial_temp']

            # --- Simulación Fuzzy ---
            print("Ejecutando Fuzzy...")
            env_fuzzy = SeriesEnvironment(
                cfg_comfort['day'], cfg_comfort['night_cal'], cfg_comfort['night_enf'],
                ext_series, initial_temp
            )
            ctrl_fuzzy = FuzzyController(fis, defuzz, env_fuzzy) # Usa fis, defuzz importados/globales
            simulator_fuzzy = Simulator(env_fuzzy, ctrl_fuzzy, cfg_phys)
            results_fuzzy = simulator_fuzzy.run_simulation(num_steps, time_hours)
            print("Fuzzy terminado.") # Debug

            # --- Simulación ON-OFF ---
            print("Ejecutando ON-OFF...")
            env_onoff = SeriesEnvironment(
                cfg_comfort['day'], cfg_comfort['night_cal'], cfg_comfort['night_enf'],
                ext_series, initial_temp
            )
            # OnOffController usa comfort_day como target_temp
            ctrl_onoff = OnOffController(env_onoff, cfg_comfort['day'])
            simulator_onoff = Simulator(env_onoff, ctrl_onoff, cfg_phys)
            results_onoff = simulator_onoff.run_simulation(num_steps, time_hours)
            print("ON-OFF terminado.") # Debug

            # Guardar resultados
            self.results[scenario] = {
                'fuzzy': results_fuzzy,
                'on_off': results_onoff
            }

            # En el hilo principal, actualizar la GUI
            self.root.after(0, self._simulation_complete, scenario, progress_window)

        except Exception as e:
             # En caso de error, mostrar mensaje en hilo principal y cerrar progreso
            print(f"Error durante la simulación: {e}") # Debug
            self.root.after(0, messagebox.showerror, "Error de Simulación", f"Ocurrió un error: {str(e)}")
            self.root.after(0, progress_window.destroy)

    def _simulation_complete(self, scenario, progress_window):
        """Llamado en el hilo principal cuando la simulación termina."""
        progress_window.destroy() # Cerrar ventana de progreso
        self.update_results_display(scenario) # Actualizar el gráfico/resultados
        messagebox.showinfo("Simulación Completa", f"Simulación para '{scenario}' finalizada.")


    def update_results_display(self, scenario):
        # Limpiar área de resultados anteriores
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None
        for widget in self.plot_frame.winfo_children():
             # No destruir el label inicial si existe y no hay canvas
            if widget != self.plot_label or self.plot_canvas:
                 widget.destroy()
        if self.plot_label:
             self.plot_label.pack_forget() # Ocultar mensaje inicial


        # Limpiar frame de control de resultados
        for widget in self.results_control_frame.winfo_children():
            widget.destroy()

        # Mostrar selector si hay múltiples resultados
        if len(self.results) > 1:
            ttk.Label(self.results_control_frame, text="Mostrar resultados para:").pack(side="left", padx=5)
            scenario_combo = ttk.Combobox(self.results_control_frame,
                                         values=list(self.results.keys()),
                                         state="readonly", width=15)
            scenario_combo.pack(side="left", padx=5)
            scenario_combo.set(scenario)
            scenario_combo.bind("<<ComboboxSelected>>",
                               lambda e: self.update_results_display(scenario_combo.get()))


        # Verificar si hay resultados y eje de tiempo para este escenario
        if scenario not in self.results or self.time_hours_current_sim is None:
            self.plot_label = ttk.Label(self.plot_frame, text=f"No hay resultados para el escenario '{scenario}'.\nEjecute una simulación primero.")
            self.plot_label.pack(pady=50)
            return

        # Obtener datos y eje de tiempo
        data = self.results[scenario]
        hours = self.time_hours_current_sim # Usar el eje de tiempo guardado
        fuzzy_data = data['fuzzy']
        onoff_data = data['on_off']
        comfort_temp = self.config['comfort']['day'] # Usar valor actual de config

        # --- Crear el gráfico usando plot_comparison ---
        fig = plt.Figure(figsize=(10, 4), dpi=100, constrained_layout=False)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        # Usar plot_comparison para graficar en estos ejes
        plot_comparison(
            label=scenario,
            time_hours=hours,
            fuzzy_data=fuzzy_data,
            onoff_data=onoff_data,
            comfort_temp=comfort_temp,
            fig=fig, ax1=ax1, ax2=ax2
        )

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Añadir información de resumen debajo del gráfico ---
        summary_frame = ttk.Frame(self.plot_frame)
        summary_frame.pack(fill="x", padx=10, pady=(5,0)) # Añadir padding superior

        try:
            diff_fuzzy = abs(fuzzy_data['avg_T_int'] - comfort_temp)
            diff_onoff = abs(onoff_data['avg_T_int'] - comfort_temp)
            if diff_fuzzy < diff_onoff:
                mejor = f"Fuzzy (dif: {diff_fuzzy:.1f}°C)"
            elif diff_onoff < diff_fuzzy:
                 mejor = f"ON-OFF (dif: {diff_onoff:.1f}°C)"
            else:
                 mejor = f"Ambos (dif: {diff_fuzzy:.1f}°C)"

            summary_text = (f"Escenario: {scenario} | T. Ext. Prom: {fuzzy_data['avg_T_ext']:.1f}°C\n"
                            f"T. Int. Prom: Fuzzy {fuzzy_data['avg_T_int']:.1f}°C | ON-OFF {onoff_data['avg_T_int']:.1f}°C\n"
                            f"Mejor control (cercanía a confort {comfort_temp}°C): {mejor}")
            ttk.Label(summary_frame, text=summary_text, justify=tk.LEFT).pack(anchor=tk.W)
        except Exception as e:
             print(f"Error al generar resumen: {e}") # Debug
             ttk.Label(summary_frame, text="No se pudo generar el resumen.").pack(anchor=tk.W)


if __name__ == "__main__":
    # Para evitar que main.py ejecute plt.show() si se importa aquí,
    # main.py debería tener su código ejecutable dentro de un bloque
    # if __name__ == "__main__":
    # Si no es así, la importación de fis/defuzz podría fallar o tener efectos secundarios.

    # Asumiendo que main.py está bien estructurado para ser importado:
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()