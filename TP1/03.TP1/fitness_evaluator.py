# fitness_evaluator.py
import os
import csv
import time
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import pygame
from constantes import WINDOW_WIDTH, WINDOW_HEIGHT, CANT_FILAS, CANT_COLUMNAS, CELL_SIZE
from aplicacion import Aplicacion
from agente import Agente

class FitnessEvaluator:
    def __init__(self, population_size, orders_csv_path, config_app):
        """
        population_size: Número de individuos a evaluar.
        orders_csv_path: Ruta al archivo de órdenes.
        config_app: Diccionario de configuración para Aplicacion (ej: {'filas': ..., 'columnas': ...})
        """
        self.population_size = population_size
        self.orders_csv_path = orders_csv_path
        self.config_app = config_app
        self.orders = self._leer_ordenes()

    def _leer_ordenes(self):
        orders = []
        try:
            with open(self.orders_csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    orders.append(row)
        except Exception as e:
            print("Error al leer ordenes.csv:", e)
            sys.exit(1)
        return orders

    @staticmethod
    def _limpiar_objetivos_y_colores(tablero):
        """
        Limpia únicamente los flags de inicio y objetivo, y restablece colores y contadores,
        dejando intacta la configuración de productos (el atributo 'caracter') de las estanterías.
        """
        tablero.inicio = None
        tablero.objetivos = []
        for cas in tablero.casilleros:
            cas.color = None
            cas.inicio = False
            cas.objetivo = False
            cas.veces_visitado = 0

    @staticmethod
    def evaluar_individuo(ind_config, orders, config_app):
        """
        Evalúa el fitness de un individuo.
        Se crea una nueva instancia de Aplicacion (y Tablero) para evitar compartir estado.
        Retorna el fitness total (suma de costos de picking de todas las órdenes).
        Se miden y retornan también los tiempos de ejecución.
        """
        start_time = time.perf_counter()
        # Usar el driver dummy para que no se abra ventana:
        import os
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        import pygame
        pygame.init()
        
        # Crear la aplicación y el tablero
        app = Aplicacion(config_app)
        app.llenar_tablero()
        tablero = app.tablero
        
        # Asignar la configuración del individuo a las estanterías
        tablero.asignar_configuracion(ind_config)
        
        fitness_total = 0
        # Procesar cada orden
        for order in orders:
            FitnessEvaluator._limpiar_objetivos_y_colores(tablero)
            indice_c = 5 * tablero.columnas + 0
            tablero.set_inicio(indice_c)
            for prod in order:
                idx_prod = tablero.buscar_por_caracter(prod)
                if idx_prod is not None:
                    tablero.set_objetivo(idx_prod)
                else:
                    print(f"No se encontró casillero para el producto {prod}")
            # Sobrescribir temporalmente el método de dibujo para evitar animación
            original_dibujar = tablero.dibujar
            tablero.dibujar = lambda *args, **kwargs: None
            
            agente = Agente(tablero)
            agente.encontrar_ruta()  # Calcula la ruta sin mostrar animación
            tablero.dibujar = original_dibujar  # Restaurar el método
            
            costo_orden = agente.calcular_costo_total(tablero.get_inicio(), tablero.get_objetivos())
            fitness_total += costo_orden
        
        pygame.quit()
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        return fitness_total, elapsed

    def evaluate_population(self):
        """
        Genera la población (usando la función generar_poblacion) y evalúa en paralelo cada individuo.
        Retorna un diccionario con la configuración de cada individuo y su fitness, junto con el tiempo total de evaluación.
        """
        from algoritmo_genetico import generar_poblacion
        poblacion = generar_poblacion(self.population_size)
        fitness_results = {}
        total_start = time.perf_counter()
        with ProcessPoolExecutor() as executor:
            futuros = {executor.submit(FitnessEvaluator.evaluar_individuo, ind.configuracion, self.orders, self.config_app): ind 
                        for ind in poblacion}
            for future in as_completed(futuros):
                try:
                    fitness, tiempo = future.result()
                    ind = futuros[future]
                    fitness_results[str(ind.configuracion)] = (fitness, tiempo)
                except Exception as exc:
                    print(f"Individuo generó una excepción: {exc}")
        total_end = time.perf_counter()
        total_elapsed = total_end - total_start
        return fitness_results, total_elapsed
