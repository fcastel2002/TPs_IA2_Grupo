import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

class FitnessTracker:
    """
    Clase responsable de rastrear la evolución del fitness durante la ejecución
    del algoritmo genético y generar gráficos de visualización.
    """
    
    def __init__(self):
        """Inicializa el rastreador de fitness con estructuras de datos vacías."""
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.generations = []
        
    def update(self, generation, population):
        """
        Actualiza el historial de fitness con los datos de la generación actual.
        
        Args:
            generation: Número de la generación actual
            population: Lista de individuos en la población actual
        """
        fitness_values = [ind.fitness for ind in population]
        best_fitness = min(fitness_values)  # Menor fitness es mejor
        avg_fitness = sum(fitness_values) / len(fitness_values)
        
        self.generations.append(generation)
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        
    def plot_fitness_evolution(self, save_path=None, show=True):
        """
        Genera y muestra un gráfico de la evolución del fitness.
        
        Args:
            save_path: Ruta donde guardar el gráfico (opcional)
            show: Si es True, muestra el gráfico en pantalla
            
        Returns:
            Ruta al archivo guardado o None si no se guardó
        """
        plt.figure(figsize=(12, 6))
        plt.plot(self.generations, self.best_fitness_history, 'b-', linewidth=2, label='Mejor Fitness')
        plt.plot(self.generations, self.avg_fitness_history, 'r--', linewidth=1.5, label='Fitness Promedio')
        
        # Añadir línea de tendencia para el mejor fitness
        if len(self.generations) > 1:
            z = np.polyfit(self.generations, self.best_fitness_history, 3)
            p = np.poly1d(z)
            plt.plot(self.generations, p(self.generations), "g-.", linewidth=1, label='Tendencia')
        
        plt.title('Evolución del Fitness a lo largo de las Generaciones', fontsize=14)
        plt.xlabel('Generación', fontsize=12)
        plt.ylabel('Fitness (menor es mejor)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right', fontsize=10)
        
        # Anotar el mejor fitness final
        if self.best_fitness_history:
            best_fitness = min(self.best_fitness_history)
            best_gen = self.generations[self.best_fitness_history.index(best_fitness)]
            plt.annotate(f'Mejor: {best_fitness:.2f}',
                         xy=(best_gen, best_fitness),
                         xytext=(best_gen, best_fitness * 1.1),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                         fontsize=10)
        
        plt.tight_layout()
        
        # Guardar el gráfico si se proporciona una ruta
        if save_path:
            # Si save_path es un directorio, crear un nombre de archivo basado en la fecha/hora
            if os.path.isdir(save_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_path, f"fitness_evolution_{timestamp}.png")
            else:
                filename = save_path
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado en: {filename}")
        
        if show:
            plt.show()
            
        return save_path if save_path else None