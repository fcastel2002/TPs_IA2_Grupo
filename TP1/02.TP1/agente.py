import random
import math
from constantes import *
from interfaz import Tablero, Casillero
import time
import math
from copy import deepcopy

class Agente:
    def __init__(self, tablero):
        self.__tablero: Tablero = tablero
        self.__actual: Casillero = self.__tablero.get_inicio()
        self.__objetivos = self.__tablero.get_objetivos()
        self.__camino = []
        self.__nodo_inicio = self.__tablero.get_inicio()

    def heuristica(self, casillero):
        return min(abs(casillero.x - objetivo.x) + abs(casillero.y - objetivo.y) for objetivo in self.__objetivos)

    def schedule(self, t):
        return 100 * 0.5 ** t  # Enfriamiento exponencial
    
    def distancia_manhattan(self, origen, destino):
        return (abs(destino.y - origen.y) + abs(destino.x - origen.x))/50
    
        
    def encontrar_ruta(self):
        self.__camino = self.temple_simulado_multi_objetivo()
        self.__tablero.actualizar_tablero(self.__camino)
    
    def temple_simulado_multi_objetivo(self, max_iteraciones=1000, temp_inicial=100, factor_enfriamiento=0.95):
        """
        Implementa Temple Simulado para encontrar el orden óptimo de visita de múltiples objetivos
        utilizando A* para calcular los costos de los caminos.
        """
        # Si no hay objetivos, devolver lista vacía
        if not self.__objetivos:
            return []
        
        # Si solo hay un objetivo, aplicar A* directamente
        if len(self.__objetivos) == 1:
            return self.a_star(self.__nodo_inicio, self.__objetivos[0])
        
        # Inicializar con un orden aleatorio de objetivos
        mejor_orden = self.__objetivos.copy()
        random.shuffle(mejor_orden)
        
        # Calcular costo inicial (usando A*)
        mejor_costo = self.calcular_costo_total(self.__nodo_inicio, mejor_orden)
        
        # Temperatura actual
        temp = temp_inicial
        
        for i in range(max_iteraciones):
            # Generar un orden vecino permutando dos elementos aleatorios
            orden_vecino = mejor_orden.copy()
            idx1, idx2 = random.sample(range(len(orden_vecino)), 2)
            orden_vecino[idx1], orden_vecino[idx2] = orden_vecino[idx2], orden_vecino[idx1]
            
            # Calcular costo del vecino
            costo_vecino = self.calcular_costo_total(self.__nodo_inicio, orden_vecino)
            
            # Calcular delta de energía
            delta_e = costo_vecino - mejor_costo
            
            # Decisión de aceptar o rechazar el nuevo orden
            if delta_e < 0:  # Si el vecino es mejor, aceptarlo
                mejor_orden = orden_vecino
                mejor_costo = costo_vecino
            else:
                # Si el vecino es peor, aceptarlo con cierta probabilidad
                probabilidad = math.exp(-delta_e / temp)
                if random.random() < probabilidad:
                    mejor_orden = orden_vecino
                    mejor_costo = costo_vecino
            
            # Enfriar la temperatura
            temp *= factor_enfriamiento
            
            # Si la temperatura es muy baja, terminar
            if temp < 0.01:
                break
        
        # Construir el camino completo siguiendo el mejor orden encontrado
        camino_completo = self.construir_camino_completo(self.__nodo_inicio, mejor_orden)
        return camino_completo

    def calcular_costo_total(self, nodo_inicio, orden_objetivos):
        """
        Calcula el costo total de visitar todos los objetivos en el orden dado,
        comenzando desde el nodo de inicio.
        """
        costo_total = 0
        nodo_actual = nodo_inicio
        
        for objetivo in orden_objetivos:
            camino = self.a_star(nodo_actual, objetivo)
            if camino is None:
                # Si no hay camino a algún objetivo, retornar costo infinito
                return float('inf')
            
            # El costo es la longitud del camino (menos 1 para no contar dos veces los nodos intermedios)
            costo_total += len(camino) - 1
            # El último nodo del camino es el nuevo nodo actual
            nodo_actual = objetivo
        
        return costo_total

    def construir_camino_completo(self, nodo_inicio, orden_objetivos):
        """
        Construye el camino completo a través de todos los objetivos en el orden dado.
        """
        camino_completo = []
        nodo_actual = nodo_inicio
        
        for i, objetivo in enumerate(orden_objetivos):
            # Obtener camino parcial usando A*
            # Usamos False para no visualizar cada segmento individual mientras calculamos
            camino_parcial = self.a_star(nodo_actual, objetivo, False)
            
            if camino_parcial is None:
                # Si no hay camino a algún objetivo, retornar None
                return None
            
            # Añadir camino parcial al camino completo (sin duplicar el nodo actual)
            if camino_completo:
                # Evitar duplicar el último nodo del camino completo
                camino_completo.extend(camino_parcial[1:])
            else:
                # En el primer tramo, incluir todo el camino
                camino_completo.extend(camino_parcial)
            
            # El último nodo del camino parcial es el nuevo nodo actual
            nodo_actual = objetivo
        
        # Visualizar el camino completo una vez que se ha calculado totalmente
        self.visualizar_camino_completo(camino_completo, orden_objetivos)
        
        return camino_completo
    
    def visualizar_camino_completo(self, camino, objetivos):
        """
        Visualiza el camino completo con colores correspondientes a cada segmento
        """
        # Limpiamos primero cualquier visualización anterior en el tablero
        # excepto los nodos de inicio y objetivos
        for casillero in self.__tablero.casilleros:
            if not casillero.inicio and not casillero.objetivo:
                casillero.color = None
        
        nodo_actual = self.__nodo_inicio
        inicio_idx = 0
        
        # Para cada segmento entre objetivos
        for i, objetivo in enumerate(objetivos):
            # Encontrar el índice del siguiente objetivo en el camino
            for j in range(inicio_idx, len(camino)):
                if camino[j] == objetivo:
                    fin_idx = j
                    break
            
            # Colorear el segmento actual con el color del objetivo
            for j in range(inicio_idx, fin_idx + 1):
                if not camino[j].inicio and not camino[j].objetivo:
                    camino[j].color = objetivo.color
                self.__tablero.dibujar(False)
                time.sleep(0.05)
            
            inicio_idx = fin_idx
            nodo_actual = objetivo
        
        # Mostramos el resultado final
        self.__tablero.dibujar(False)

    def a_star(self, inicio, objetivo, mostrar=False):
        """
        Implementa el algoritmo A* para encontrar el camino de menor costo
        entre el nodo de inicio y el nodo objetivo.
        """
        # Conjunto de nodos ya evaluados
        cerrados = set()
        
        # Conjunto de nodos descubiertos que necesitan ser evaluados
        # Inicialmente sólo contiene el nodo inicial
        abiertos = {inicio}
        
        # Para cada nodo, qué nodo viene antes en el camino óptimo
        vino_de = {}
        
        # Para cada nodo, el costo del camino más barato desde el inicio hasta el nodo
        g_score = {inicio: 0}
        
        # Para cada nodo, el costo total estimado del camino más barato desde inicio hasta objetivo pasando por el nodo
        f_score = {inicio: self.heuristica_distancia(inicio, objetivo)}
        
        while abiertos:
            # Encontrar el nodo en abiertos con el menor f_score
            actual = min(abiertos, key=lambda nodo: f_score.get(nodo, float('inf')))
            
            if actual == objetivo:
                return self.reconstruir_camino(vino_de, actual, mostrar)
            
            abiertos.remove(actual)
            cerrados.add(actual)
            
            for vecino in self.__tablero.get_vecinos(actual.get_indice()):
                # Ignorar los vecinos que ya fueron evaluados
                if vecino in cerrados:
                    continue
                
                # Calcular costo tentativo
                g_tentativo = g_score.get(actual, float('inf')) + self.distancia(actual, vecino)
                
                # Este no es un camino mejor
                if vecino in abiertos and g_tentativo >= g_score.get(vecino, float('inf')):
                    continue
                
                # Este es el mejor camino hasta ahora
                vino_de[vecino] = actual
                g_score[vecino] = g_tentativo
                f_score[vecino] = g_score[vecino] + self.heuristica_distancia(vecino, objetivo)
                
                if vecino not in abiertos:
                    abiertos.add(vecino)
        
        # No se encontró camino
        return None

    def distancia(self, nodo_a, nodo_b):
        """
        Calcula la distancia entre dos nodos.
        Utiliza la distancia euclidiana.
        """
        return ((nodo_a.x - nodo_b.x) ** 2 + (nodo_a.y - nodo_b.y) ** 2) ** 0.5

    def heuristica_distancia(self, nodo, objetivo):
        """
        Función heurística que estima el costo desde un nodo hasta el objetivo.
        Usa la distancia euclidiana como heurística admisible.
        """
        return self.distancia(nodo, objetivo)

    def reconstruir_camino(self, vino_de, actual, mostrar=False):
        """
        Reconstruye el camino desde el inicio hasta el nodo actual
        siguiendo los enlaces en el diccionario vino_de.
        """
        camino_total = [actual]
        while actual in vino_de:
            actual = vino_de[actual]
            camino_total.append(actual)
        
        # Invertir el camino para que vaya desde el inicio hasta el objetivo
        camino_total = camino_total[::-1]
        
        # Si se solicita mostrar el camino mientras se reconstruye
        if mostrar:
            color = camino_total[-1].color
            for casillero in camino_total:
                if not casillero.inicio and not casillero.objetivo:
                    self.__tablero.casilleros[casillero.get_indice()].color = color
                self.__tablero.dibujar(False)
                time.sleep(0.05)
        
        return camino_total