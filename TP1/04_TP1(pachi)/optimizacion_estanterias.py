# optimizacion_estanterias.py
import pygame
import csv
import sys
import time
import os
from aplicacion import Aplicacion
from algoritmo_genetico import AlgoritmoGenetico
from constantes import *

class OptimizacionEstanterias(Aplicacion):
    """
    Extiende la clase Aplicacion para implementar la optimización de estanterías
    mediante algoritmos genéticos con evaluación de fitness mediante recocido simulado.
    """
    def __init__(self, tablero, archivo_csv):
        super().__init__(tablero)
        self.archivo_csv = archivo_csv
        # Reutilizamos la funcionalidad del menú selector para leer el CSV
        self.ordenes = self._leer_ordenes_csv()
    
    def _leer_ordenes_csv(self):
        """Lee todas las líneas de ordenes.csv con manejo robusto de errores."""
        ordenes = []
        try:
            # Primero intentamos usar el menú selector
            datos_csv = self.menu.load_csv_data()
            
            # Convertir a enteros con validación
            for fila in datos_csv:
                if len(ordenes) <= 2:        
                    try:
                        orden = [int(item) for item in fila]
                        ordenes.append(orden)
                    except ValueError:
                        print(f"Advertencia: Se ignoró una línea con formato incorrecto: {fila}")
                
            print(f"Se cargaron {len(ordenes)} órdenes correctamente.")
        except Exception as e:
            print(f"Error al leer órdenes con el menú selector: {e}")
            print("Intentando lectura directa del archivo...")
            
            try:
                # Lectura directa como fallback
                with open(self.archivo_csv, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        try:
                            orden = [int(item) for item in row]
                            ordenes.append(orden)
                        except ValueError:
                            print(f"Advertencia: Se ignoró una línea con formato incorrecto: {row}")
                
                print(f"Se cargaron {len(ordenes)} órdenes directamente.")
            except Exception as e2:
                print(f"Error en lectura directa: {e2}")
        
        return ordenes
    
    def ejecutar_optimizacion(self, config=None, modo_silencioso=True):
        """
        Ejecuta el algoritmo genético para optimizar la disposición de estanterías.
        
        Args:
            config: Configuración del algoritmo genético
            modo_silencioso: Si es True, ejecuta sin visualización para mejorar rendimiento
        """
        # Configuración por defecto
        if config is None:
            config = {
                'tam_poblacion': 10,
                'tasa_mutacion': 0.2,
                'tasa_cruce': 0.8,
                'num_generaciones': 50,
                'elitismo': 2
            }
        
        # Verificar que tenemos órdenes para procesar
        if not self.ordenes:
            print("No hay órdenes para procesar. Verifique el archivo CSV.")
            return
        
        # Mostrar información sobre las órdenes
        print(f"Total de órdenes: {len(self.ordenes)}")
        print("Ejemplos de órdenes:")
        for i in range(min(3, len(self.ordenes))):
            print(f"  Orden {i+1}: {self.ordenes[i]}")
        
        # Crear instancia del algoritmo genético
        ag = AlgoritmoGenetico(
            tablero=self.tablero,
            ordenes=self.ordenes,
            tam_poblacion=config['tam_poblacion'],
            tasa_mutacion=config['tasa_mutacion'],
            tasa_cruce=config['tasa_cruce'],
            num_generaciones=config['num_generaciones'],
            elitismo=config['elitismo']
        )
        
        # Ejecutar el algoritmo
        mejor_solucion, mejor_fitness = ag.ejecutar()
        
        # Aplicar la solución al tablero y generar mapa de calor
        ag.aplicar_mejor_solucion(generar_mapa_calor=True)
        
        # Visualizar resultados
        ag.visualizar_resultados()
        
        # Si no estamos en modo silencioso, mantener ventana abierta
        if not modo_silencioso:
            self._mantener_ventana_abierta()
        else:
            pygame.quit()
            print("\nPrograma finalizado. Revise los gráficos generados.")
        
    def _mantener_ventana_abierta(self):
        """Mantiene la ventana de Pygame abierta hasta que el usuario la cierre."""
        print("\nMostrando resultado final en ventana gráfica.")
        print("Presione ESC para salir.")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Redibujar el tablero
            self.tablero.dibujar(True)
            
            # Mostrar mensaje
            font = pygame.font.SysFont('arial', 20)
            mensaje = "Optimización completada. Presione ESC para salir."
            self._Aplicacion__screen.blit(font.render(mensaje, True, (0, 0, 0)), (10, WINDOW_HEIGHT - 30))
            
            pygame.display.flip()
            pygame.time.delay(100)
        
        pygame.quit()
        sys.exit()

def main():
    # Configuración personalizable
    config = {
        'tam_poblacion': 10,       # Tamaño de la población
        'tasa_mutacion': 0.2,      # Probabilidad de mutación
        'tasa_cruce': 0.8,         # Probabilidad de cruce
        'num_generaciones': 50,    # Número de generaciones
        'elitismo': 2              # Número de mejores individuos que pasan directamente
    }
    
    tablero_info = {'filas': 11, 'columnas': 13}
    app = OptimizacionEstanterias(tablero_info, "ordenes.csv")
    
    # Configurar tablero inicial (reutilizando el código existente)
    app.llenar_tablero()
    
    # Ejecutar la optimización en modo silencioso (sin visualización)
    app.ejecutar_optimizacion(config, modo_silencioso=True)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()