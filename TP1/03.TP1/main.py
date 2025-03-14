# main.py
import os
from fitness_evaluator import FitnessEvaluator
from constantes import CANT_FILAS, CANT_COLUMNAS

def main():
    # Definir el tamaño de la población directamente aquí
    population_size = 10  # Puedes modificar este valor según lo necesites

    config_app = {'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS}
    # Se asume que 'ordenes.csv' está en la misma carpeta que main.py
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv = os.path.join(script_dir, "ordenes.csv")
    
    evaluator = FitnessEvaluator(population_size, orders_csv, config_app)
    fitness_results, total_time = evaluator.evaluate_population()
    
    print("Resultados de fitness:")
    for config, (fit, tiempo) in fitness_results.items():
        print(f"Configuración {config} => Fitness: {fit} (Tiempo: {tiempo:.3f} seg)")
    print(f"Tiempo total de evaluación: {total_time:.3f} seg")

if __name__ == "__main__":
    main()
