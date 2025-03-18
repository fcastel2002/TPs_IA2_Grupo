# batch_ordenes.py (modificado)
import pygame
import csv
import time
import os
from aplicacion import Aplicacion
from agente import Agente
from interfaz import Tablero, Casillero
from constantes import *

class BatchAplicacion(Aplicacion):
    """
    Hereda de Aplicacion para procesar todas las líneas del CSV.
    """
    def __init__(self, tablero, archivo_csv):
        super().__init__(tablero)
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.archivo_csv = os.path.join(script_dir, archivo_csv)
        self.lineas_ordenes = []
    
    def leer_csv(self):
        """Lee todas las líneas de ordenes.csv y las guarda en self.lineas_ordenes."""
        try:
            with open(self.archivo_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.lineas_ordenes.append(row)
        except FileNotFoundError:
            print(f"No se encontró el archivo {self.archivo_csv}")
            return

    def set_inicio_en_C(self):
        """
        Establece la celda 'C' (fila=5, col=0) como nodo de inicio.
        """
        indice_c = 5 * self.tablero.columnas + 0
        self.tablero.set_inicio(indice_c)
    
    def esperar_para_continuar(self):
        esperando = True
        font = pygame.font.SysFont('arial', 20)
        mensaje = "Presione N para continuar al siguiente pedido o cierre la ventana para salir."
        while esperando and self.__running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    esperando = False
                    self.__running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        esperando = False
                        break
            # Redibujar el tablero (con la ruta actual)
            self.tablero.dibujar(True)
            # Dibujar el mensaje en la parte inferior de la pantalla usando el atributo de la clase base
            self._Aplicacion__screen.blit(font.render(mensaje, True, (0, 0, 0)), (10, WINDOW_HEIGHT - 30))
            pygame.display.flip()
            pygame.time.delay(100)

    
    def ejecutar_batch(self):
        """
        Procesa cada línea de ordenes.csv:
          - Limpia el tablero.
          - Fija la celda "C" como inicio.
          - Asigna los objetivos de la línea.
          - Ejecuta el Agente para hallar la ruta.
          - Imprime el costo total.
          - Espera a que el usuario presione "N" para continuar.
        """
        self.leer_csv()
        
        # Iterar sobre cada línea de órdenes
        for i, fila in enumerate(self.lineas_ordenes, start=1):
            # Convertir a int (si en CSV vienen como strings)
            objetivos = [int(x) for x in fila]
            
            # Limpiar tablero y fijar "C" como inicio de nuevo
            self.tablero.limpiar_tablero()
            self.set_inicio_en_C()
            
            # Marcar cada producto como objetivo.
            for objetivo_str in fila:  # fila es la lista de strings p.e. ['40','26','13'...]
                # Buscar el casillero con caracter == objetivo_str
                indice = self.tablero.buscar_por_caracter(objetivo_str)
                if indice is not None:
                    self.tablero.set_objetivo(indice)
                else:
                    print(f"No se encontró casillero con caracter '{objetivo_str}'")
            
            # Crear agente y ejecutar la ruta
            agente = Agente(self.tablero)
            agente.encontrar_ruta()
            
            # Calcular el costo total usando el mismo método de Temple Simulado
            costo = agente.calcular_costo_total(
                self.tablero.get_inicio(),
                self.tablero.get_objetivos()
            )
            print(f"Orden #{i} => Objetivos: {fila} => Costo total: {costo}")
            
            # Esperar a que el usuario indique continuar
            self.esperar_para_continuar()
    
    def run(self):
        """
        Sobrescribe el run original para procesar el batch y mantener la ventana abierta.
        """
        self.__running = True
        
        # Fijar la celda "C" como inicio
        self.set_inicio_en_C()
        # Procesar todas las órdenes
        self.ejecutar_batch()
        
        # Bucle principal: mantener la ventana abierta hasta que se cierre
        while self.__running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
            self.tablero.dibujar(True)
        
        pygame.quit()

def main():
    tablero_info = {'filas': 11, 'columnas': 13}
    app = BatchAplicacion(tablero_info, "ordenes.csv")
    app.run()

if __name__ == "__main__":
    main()
