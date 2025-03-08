# import random
# import math
# from constantes import*
# from interfaz import Tablero, Casillero

# class Agente:
#     def __init__(self, tablero):
#         self.__tablero : Tablero = tablero
#         self.__actual : Casillero = self.__tablero.get_inicio()
    
#     def heuristica(self, casillero, objetivos):
#         return min(abs(casillero.x  - objetivo.x ) +
#                 abs(casillero.y - objetivo.y ) for objetivo in objetivos)
    
#     def schedule(self, t):
#         # return 100 / (1 + t)
#         return 100 * 0.5 **t
    
#     def obtener_vecinos(self, casillero):
#         vecinos = []
#         fila = casillero.x // CELL_SIZE
#         columna = casillero.y // CELL_SIZE
#         print(f"fila:{fila}, columna:{columna}")
#         # Arriba
#         if fila > 0:
#             vecinos.append(self.__tablero.get_casillero_por_elemento(fila - 1, columna))
        
#         # Abajo
#         if fila < self.__tablero.filas - 1:
#             vecinos.append(self.__tablero.get_casillero_por_elemento(fila + 1, columna))
        
#         # Izquierda
#         if columna > 0:
#             vecinos.append(self.__tablero.get_casillero_por_elemento(fila, columna - 1))
        
#         # Derecha
#         if columna < self.__tablero.columnas - 1:
#             vecinos.append(self.__tablero.get_casillero_por_elemento(fila, columna + 1))
        
#         print("vecinos:")
#         for vecino in vecinos:
#             print(f"--- {casillero.get_indice()}")
#         return vecinos
        
    
#     def seleccionar_vecino(self, inicio, objetivos):
#         actual = self.__inicio
#         vecinos = self.obtener_vecinos(actual)
#         for t in range(1, 10000):
#             T = self.schedule(t)
#             if T < 1:
#                 return actual
            
#             if not vecinos:
#                 continue
#             proximo_estado = self.__tablero.casilleros[random.choice(vecinos).get_indice()]
            
#             delta_E = self.heuristica(proximo_estado,objetivos) - self.heuristica(actual,objetivos)
            
#             if delta_E < 0:
#                 actual = proximo_estado
#                 return actual
#             elif random.random() < 1/math.exp(delta_E / T):
#                 actual = proximo_estado
#                 return actual
            
#     def resolver_busqueda(self):
#         metodo_terminado = False
#         color = 0
#         while not metodo_terminado:
#             if self.__tablero.objetivo.objetivo:
#                 print("Es objetivo")
#                 self.__tablero.casilleros[self.__inicio.get_indice()].objetivo = False
#                 color += 1
#             if len(self.__tablero.get_objetivos()) == 0:
                
#                 print("Metodo terminado")
#                 metodo_terminado = True
#             else:
#                 self.__tablero.casilleros[self.__inicio.get_indice()].inicio = False
#                 self.__inicio = self.seleccionar_vecino(self.__tablero.casilleros[self.__inicio.get_indice()],self.__objetivos)
#                 self.__inicio.inicio = True
#                 self.__tablero.casilleros[self.__inicio.get_indice()].color = COLORES_OBJETIVOS[color % len(COLORES_OBJETIVOS)]
#             self.__tablero.dibujar(False)

import random
import math
from constantes import *
from interfaz import Tablero, Casillero

class Agente:
    def __init__(self, tablero):
        self.__tablero: Tablero = tablero
        self.__actual: Casillero = self.__tablero.get_inicio()
        self.__objetivos = self.__tablero.get_objetivos()
        self.__camino = []

    def heuristica(self, casillero):
        return min(abs(casillero.x - objetivo.x) + abs(casillero.y - objetivo.y) for objetivo in self.__objetivos)

    def schedule(self, t):
        return 100 * 0.5 ** t  # Enfriamiento exponencial

    def obtener_vecinos(self, casillero):
        vecinos = []
        i = casillero.get_indice()
        derecha = i+1 if i+1 > 0 and i+1 < 143 else False
        izquierda = i-1 if i-1 > 0 and i-1 < 143 else False
        arriba = i-13 if i-13 > 0 and i-13 < 143 else False
        abajo = i+13 if i+13 > 0 and i+13 < 143 else False
        if i % 13 != 0 and i % 13 != 12:
            if izquierda is not False:
                vecinos.append(self.__tablero.casilleros[izquierda])
            if derecha is not False :
                vecinos.append(self.__tablero.casilleros[derecha])
            if arriba is not False:
                vecinos.append(self.__tablero.casilleros[arriba])
            if abajo is not False:
                vecinos.append(self.__tablero.casilleros[abajo])
        elif i % 13 == 0:
            if derecha is not False :
                vecinos.append(self.__tablero.casilleros[derecha])
            if arriba is not False:
                vecinos.append(self.__tablero.casilleros[arriba])
            if abajo is not False:
                vecinos.append(self.__tablero.casilleros[abajo])
        elif i % 12 == 0:
            if izquierda is not False:
                vecinos.append(self.__tablero.casilleros[izquierda])
            if arriba is not False:
                vecinos.append(self.__tablero.casilleros[arriba])
            if abajo is not False:
                vecinos.append(self.__tablero.casilleros[abajo])
        for vecino in vecinos:
            if vecino.libre is not True and vecino.objetivo is False:
                vecinos.remove(vecino)
        print("inicio:")
        print(casillero)
        print("vecinos:")
        for vecino in vecinos:
            print(vecino)
        return vecinos

    def resolver_busqueda(self):
        temperatura = 100
        t = 1

        for _ in range(100000):
            temperatura = self.schedule(t)
            
            vecinos = self.obtener_vecinos(self.__actual)
            if temperatura < 1:
                self.__actual = vecino_aleatorio
            if not vecinos:
                print("No hay mas movimientos posibles")
                break  # No hay más movimientos posibles
            
            vecino_aleatorio = random.choice(vecinos)
            delta_E = self.heuristica(vecino_aleatorio) - self.heuristica(self.__actual)

            if delta_E < 0 or random.random() < 1 / math.exp(delta_E / temperatura):
                self.__actual = vecino_aleatorio
                self.__actual.recorrido = True
                self.__actual.color = GREEN

                # Si llegamos a un objetivo, lo eliminamos de la lista
                if self.__actual in self.__objetivos:
                    self.__objetivos.remove(self.__actual)
            
            t += 1
            self.__tablero.dibujar(False)  # Actualizar visualización del tablero
        
        print("Búsqueda completada")