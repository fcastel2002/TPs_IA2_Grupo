# mostrar_poblacion.py
import pygame
import sys
import time
import os
import csv

from constantes import WINDOW_WIDTH, WINDOW_HEIGHT, CANT_FILAS, CANT_COLUMNAS, CELL_SIZE
from aplicacion import Aplicacion
from agente import Agente
from algoritmo_genetico import generar_poblacion

def mostrar_poblacion():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Población + Fitness de Órdenes")
    font = pygame.font.SysFont("arial", 18)
    
    # 1) Crear la aplicación y el tablero
    app = Aplicacion({'filas': CANT_FILAS, 'columnas': CANT_COLUMNAS})
    app.llenar_tablero()  # Crea el tablero con la celda "C" y las estanterías (sin valores fijos)
    tablero = app.tablero
    
    # 2) Generar la población (10 individuos aleatorios)
    poblacion = generar_poblacion(10)
    
    # 3) Leer el archivo ordenes.csv
    script_dir = os.path.dirname(os.path.realpath(__file__))
    orders_csv = os.path.join(script_dir, "ordenes.csv")
    orders = []
    try:
        with open(orders_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                orders.append(row)
    except Exception as e:
        print("Error al leer ordenes.csv:", e)
        pygame.quit()
        sys.exit()
    
    # --- Función auxiliar para limpiar solo objetivos y colores ---
    def limpiar_objetivos_y_colores():
        """
        Se limpian únicamente los flags de inicio y objetivo, y se borran los colores 
        y contadores de visitas, dejando intacto el 'caracter' de las estanterías.
        """
        tablero.inicio = None
        tablero.objetivos = []
        for cas in tablero.casilleros:
            cas.color = None
            cas.inicio = False
            cas.objetivo = False
            cas.veces_visitado = 0
    
    # 4) Procesar cada individuo
    for idx, individuo in enumerate(poblacion, start=1):
        # A) Limpiar el tablero por completo para el nuevo individuo
        tablero.limpiar_tablero()
        
        # B) Asignar la configuración de este individuo a las estanterías
        tablero.asignar_configuracion(individuo.configuracion)
        
        # C) Dibujar la distribución actual
        tablero.dibujar(True)
        info_text = font.render(f"Individuo {idx}: {individuo.configuracion}", True, (0,0,0))
        screen.blit(info_text, (10, WINDOW_HEIGHT - 30))
        pygame.display.flip()
        print(f"Mostrando Individuo {idx}: {individuo.configuracion}")
        
        fitness_total = 0
        
        # D) Procesar todas las órdenes para este individuo
        for order_idx, order in enumerate(orders, start=1):
            # Limpiar solo objetivos y colores (no la distribución)
            limpiar_objetivos_y_colores()
            
            # Fijar "C" como inicio (fila 5, col 0)
            indice_c = 5 * tablero.columnas + 0
            tablero.set_inicio(indice_c)
            
            # Marcar cada producto de la orden como objetivo (usando buscar_por_caracter)
            for prod in order:
                idx_prod = tablero.buscar_por_caracter(prod)
                if idx_prod is not None:
                    tablero.set_objetivo(idx_prod)
                else:
                    print(f"No se encontró casillero para el producto {prod}")
            
            # Solo para la primera orden de cada individuo se mostrará el recorrido
            if order_idx == 1:
                mostrar_ruta = True
            else:
                mostrar_ruta = False
            
            if mostrar_ruta:
                tablero.dibujar(True)
                pygame.display.flip()
                print(f"Individuo {idx}, Orden #{order_idx} => Mostrando recorrido en Pygame.")
            
            # Crear agente y ejecutar la ruta (Temple Simulado + A*)
            agente = Agente(tablero)
            # En este ejemplo, 'encontrar_ruta()' se encarga de animar el recorrido.
            # Si 'mostrar_ruta' es False, se ejecuta sin pausa.
            agente.encontrar_ruta()
            
            # Calcular el costo de picking (incluyendo regreso a "C")
            costo_orden = agente.calcular_costo_total(tablero.get_inicio(), tablero.get_objetivos())
            fitness_total += costo_orden
            
            if mostrar_ruta:
                print(f"Orden #{order_idx} => Costo: {costo_orden}")
                # Esperar a que el usuario presione "N" para continuar a la siguiente orden
                msg = font.render("Presione N para continuar a la siguiente orden...", True, (0,0,0))
                screen.blit(msg, (10, WINDOW_HEIGHT - 30))
                pygame.display.flip()
                esperando = True
                while esperando:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                            esperando = False
                    pygame.time.delay(100)
            # Para órdenes posteriores (order_idx > 1), no se muestra la animación
            # y se continúa sin pausa.
        
        print(f"Fitness total del Individuo {idx}: {fitness_total}")
        
        # Esperar a que el usuario presione "N" para pasar al siguiente individuo
        msg2 = font.render("Presione N para pasar al siguiente individuo...", True, (0,0,0))
        screen.blit(msg2, (10, WINDOW_HEIGHT - 30))
        pygame.display.flip()
        esperando_ind = True
        while esperando_ind:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    esperando_ind = False
            pygame.time.delay(100)
    
    # Mantener la ventana abierta al finalizar
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(100)

if __name__ == "__main__":
    mostrar_poblacion()
