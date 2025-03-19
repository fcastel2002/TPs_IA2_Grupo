import random
import math
from constantes import *
from interfaz import Tablero, Casillero
import time
import math
from copy import deepcopy
import csv
import matplotlib.pyplot as plt
import threading

class Agente:
    def __init__(self, tablero):
        self.tablero: Tablero = tablero
        self.objetivos = self.tablero.get_objetivos()
        self.__camino = []
        self.nodo_inicio = self.tablero.get_inicio()
        
    def encontrar_ruta(self):
        self.__camino = self.temple_simulado_multi_objetivo()
        #self.__camino = self.construir_camino_completo(self.nodo_inicio, self.objetivos, True)
        print(f"La cantidad de casilleros visitados es: {len(self.__camino)-1}")
        self.tablero.actualizar_tablero(self.__camino)
    
    def temple_simulado_multi_objetivo(self, max_iteraciones=1000, temp_inicial=100, factor_enfriamiento=0.95, graficar=True):
        """
        Implementa Temple Simulado para encontrar el orden óptimo de visita de múltiples objetivos
        utilizando A* para calcular los costos de los caminos.
        """
        if not self.objetivos:
            return []

        if len(self.objetivos) == 1:
            return self.construir_camino_completo(self.nodo_inicio, self.objetivos)

        mejor_orden = self.objetivos.copy()
        random.shuffle(mejor_orden)

        mejor_costo = self.calcular_costo_total(self.nodo_inicio, mejor_orden)

        temp = temp_inicial
        temperaturas = []
        costos = []

        for i in range(max_iteraciones):
            orden_vecino = mejor_orden.copy()
            idx1, idx2 = random.sample(range(len(orden_vecino)), 2)
            orden_vecino[idx1], orden_vecino[idx2] = orden_vecino[idx2], orden_vecino[idx1]

            costo_vecino = self.calcular_costo_total(self.nodo_inicio, orden_vecino)
            delta_e = costo_vecino - mejor_costo

            if delta_e < 0:
                mejor_orden = orden_vecino
                mejor_costo = costo_vecino
            else:
                probabilidad = math.exp(-delta_e / temp)
                if random.random() < probabilidad:
                    mejor_orden = orden_vecino
                    mejor_costo = costo_vecino

            # Guardar valores de temperatura y costo
            temperaturas.append(temp)
            costos.append(mejor_costo)

            temp *= factor_enfriamiento

            if temp < 0.01:
                break

        # Graficar temperatura y costo en un hilo separado
        if graficar:
            threading.Thread(target=self.graficar_temperatura_costos, args=(temperaturas, costos)).start()

        camino_completo = self.construir_camino_completo(self.nodo_inicio, mejor_orden, graficar)
        return camino_completo

    def graficar_temperatura_costos(self, temperaturas, costos):
        """
        Grafica la temperatura y el costo a lo largo de las iteraciones del algoritmo de Temple Simulado,
        cada uno en una ventana separada.
        """
        # Crear una ventana para la temperatura
        fig1 = plt.figure(figsize=(10, 6))
        ax1 = fig1.add_subplot(111)
        ax1.plot(temperaturas, color='blue')
        ax1.set_title('Evolución de la Temperatura')
        ax1.set_xlabel('Iteración')
        ax1.set_ylabel('Temperatura')
        fig1.tight_layout()
        plt.show(block=False)  # No bloquear la ejecución para la siguiente ventana

        # Crear una ventana para el costo
        fig2 = plt.figure(figsize=(10, 6))
        ax2 = fig2.add_subplot(111)
        ax2.plot(costos, color='red')
        ax2.set_title('Evolución del Costo (Camino)')
        ax2.set_xlabel('Iteración')
        ax2.set_ylabel('Costo')
        fig2.tight_layout()
        plt.show(block=False)  # No bloquear la ejecución

        # Para asegurar que las gráficas no bloqueen el flujo de ejecución
        plt.show()

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

    def construir_camino_completo(self, nodo_inicio, orden_objetivos, graficar = True):
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
            nodo_actual = camino_parcial[len(camino_parcial)-1]
        
        # Visualizar el camino completo una vez que se ha calculado totalmente
        if graficar:
            self.visualizar_camino_completo(camino_completo, orden_objetivos)
        
        return camino_completo
    
    def visualizar_camino_completo(self, camino, objetivos):
        """
        Visualiza el camino completo con colores correspondientes a cada segmento
        """
        # Limpiamos primero cualquier visualización anterior en el tablero
        # excepto los nodos de inicio y objetivos
        for casillero in self.tablero.casilleros:
            if not casillero.inicio and not casillero.objetivo:
                casillero.color = None
        
        nodo_actual = self.nodo_inicio
        inicio_idx = 0
        
        # Para cada segmento entre objetivos
        for i, objetivo in enumerate(objetivos):
            # Encontrar el índice del siguiente objetivo en el camino
            for j in range(inicio_idx, len(camino)):
                if objetivo in self.tablero.get_vecinos(camino[j].get_indice()):
                #if camino[j] == objetivo:
                    fin_idx = j
                    break
            
            # Colorear el segmento actual con el color del objetivo
            for j in range(inicio_idx, fin_idx + 1):
                if not camino[j].inicio and not camino[j].objetivo:
                    camino[j].color = objetivo.color
                self.tablero.dibujar(False)
                time.sleep(0.05)
            
            inicio_idx = fin_idx
            nodo_actual = objetivo
        
        # Mostramos el resultado final
        self.tablero.dibujar(False)

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
            
            for vecino in self.tablero.get_vecinos(actual.get_indice()):
                # Ignorar los vecinos que ya fueron evaluados
                if vecino == objetivo:
                    return self.reconstruir_camino(vino_de, actual, mostrar)
                if vecino in cerrados:
                    continue
                if vecino.objetivo:
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
                    self.tablero.casilleros[casillero.get_indice()].color = color
                self.tablero.dibujar(False)
        
        return camino_total
    
    
class SuperAgente(Agente):
    def __init__(self,tablero,archivo):
        super().__init__(tablero)
        self.archivo = archivo
        self.inicio = self.tablero.casilleros[65]
        self.data = self.load_csv_data()
    
    def load_csv_data(self):
            """Carga los datos desde un archivo CSV."""
            try:
                with open(self.archivo, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    return list(reader)
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo '{self.archivo}'")
                return []
            except Exception as e:
                print(f"Error al leer el archivo CSV: {e}")
                return []
            
    # def algoritmo_genetico(self):
    #     if len(self.data) != 0:
            
            
    def algoritmo_genetico(self, tam_poblacion=10, max_generaciones=50, prob_cruce=0.8, prob_mutacion=0.2):
        """
        Implementa un algoritmo genético para optimizar la ubicación de productos en estanterías.
        
        Args:
            tam_poblacion: Tamaño de la población (número de individuos)
            max_generaciones: Número máximo de generaciones
            prob_cruce: Probabilidad de cruce entre individuos
            prob_mutacion: Probabilidad de mutación de un gen
            
        Returns:
            La mejor distribución de estanterías encontrada
        """
        print("Iniciando algoritmo genético para optimización de ubicación de productos...")
        
        # Paso 1: Obtener todas las estanterías/productos que pueden ser reubicados
        productos_disponibles = self.tablero.obtener_estanterias()
        n_productos = len(productos_disponibles)
        
        if n_productos == 0:
            print("No hay productos disponibles para reubicar.")
            return None
        
        # Paso 2: Crear la población inicial (cada individuo es una permutación de ubicaciones)
        poblacion = self._inicializar_poblacion(productos_disponibles, tam_poblacion)
        
        # Almacenar el mejor individuo global encontrado
        mejor_individuo_global = None
        mejor_fitness_global = 0
        
        # Paso 3: Evolución de la población a través de generaciones
        for generacion in range(max_generaciones):
            print(f"Generación {generacion+1}/{max_generaciones}")
            
            # Paso 3.1: Evaluar cada individuo en la población actual
            fitness_valores = self._evaluar_poblacion(poblacion)
            
            # Encontrar el mejor individuo de esta generación
            idx_mejor = fitness_valores.index(max(fitness_valores))
            mejor_individuo = poblacion[idx_mejor]
            mejor_fitness = fitness_valores[idx_mejor]
            
            # Actualizar el mejor global si corresponde
            if mejor_individuo_global is None or mejor_fitness > mejor_fitness_global:
                mejor_individuo_global = mejor_individuo.copy()
                mejor_fitness_global = mejor_fitness
                print(f"Nuevo mejor fitness encontrado: {mejor_fitness_global}")
            
            # Paso 3.2: Crear la nueva generación
            nueva_poblacion = []
            
            # Elitismo: conservar al mejor individuo
            nueva_poblacion.append(mejor_individuo)
            
            # Generar el resto de la nueva población mediante selección, cruce y mutación
            while len(nueva_poblacion) < tam_poblacion:
                # Seleccionar padres usando selección por ruleta
                padre1 = self._seleccion_ruleta(poblacion, fitness_valores)
                padre2 = self._seleccion_ruleta(poblacion, fitness_valores)
                
                # Realizar cruce con cierta probabilidad
                if random.random() < prob_cruce:
                    hijo1, hijo2 = self._cruce_ordenado(padre1, padre2)
                else:
                    hijo1, hijo2 = padre1.copy(), padre2.copy()
                
                # Aplicar mutación con cierta probabilidad
                if random.random() < prob_mutacion:
                    self._mutacion(hijo1)
                if random.random() < prob_mutacion:
                    self._mutacion(hijo2)
                
                # Añadir hijos a la nueva población
                nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < tam_poblacion:
                    nueva_poblacion.append(hijo2)
            
            # La nueva población reemplaza a la antigua
            poblacion = nueva_poblacion
        
        # Paso 4: Retornar el mejor individuo encontrado
        print(f"Algoritmo genético completado. Mejor fitness: {mejor_fitness_global}")
        
        # Aplicar la mejor solución encontrada al tablero
        #self.tablero.cambiar_estanterias(mejor_individuo_global)
        #self._aplicar_solucion(mejor_individuo_global, productos_disponibles)
        
        return mejor_individuo_global

    def _inicializar_poblacion(self, productos_disponibles, tam_poblacion):
        """
        Crea una población inicial de individuos, donde cada individuo es una permutación
        de los productos disponibles.
        """
        poblacion = []
        for _ in range(tam_poblacion):
            # Cada individuo es una permutación diferente de los productos
            individuo = productos_disponibles.copy()
            random.shuffle(individuo)
            poblacion.append(individuo)
        return poblacion

    def _evaluar_poblacion(self, poblacion):
        """
        Evalúa cada individuo en la población calculando su fitness.
        El fitness es (1 - fi/ftotal), donde fi es la suma de costos para todas las órdenes.
        """
        # Primero calculamos el costo para cada individuo
        costos = []
        for individuo in poblacion:
            costo = self._calcular_costo_individuo(individuo)
            costos.append(costo)
        
        # Calculamos el costo total
        costo_total = sum(costos)
        
        # Calculamos el fitness para cada individuo
        fitness_valores = []
        for costo in costos:
            if costo_total == 0:  # Evitar división por cero
                fitness = 0
            else:
                fitness = 1 - (costo / costo_total)
            fitness_valores.append(fitness)
        #print(costos)
        return fitness_valores

    def _calcular_costo_individuo(self, individuo):
        """
        Calcula el costo total de un individuo sumando los costos de todas las órdenes.
        """
        
        # Modificamos la ubicación de las estanterías
        self.tablero.cambiar_estanterias(individuo)

        
        self.tablero.dibujar(False)
        
        # Calculamos el costo total para todas las órdenes
        costo_total = 0
        for orden in self.data:
            # Configuramos los objetivos para esta orden
            self._configurar_objetivos_orden(orden)
            
            # Calculamos el camino usando temple simulado
            camino = self.temple_simulado_multi_objetivo(max_iteraciones=1000, temp_inicial=100, factor_enfriamiento=0.95, graficar = False)
            #print(camino)
            # Sumamos el costo de este camino
            if camino:
                costo_total += len(camino) - 1
        
        return costo_total

    def _guardar_configuracion_tablero(self):
        """
        Guarda la configuración actual del tablero para poder restaurarla después.
        """
        return {
            'objetivos': deepcopy(self.tablero.get_objetivos()),
            'productos': deepcopy(self.tablero.get_objetivos_disponibles())
        }

    def _restaurar_configuracion_tablero(self, configuracion):
        """
        Restaura la configuración guardada del tablero.
        """
        # Limpiamos los objetivos actuales
        self.tablero.limpiar_objetivos()
        
        # Restauramos los objetivos
        for objetivo in configuracion['objetivos']:
            self.tablero.set_objetivo(objetivo.get_indice())
        
        # Restauramos las posiciones de los productos
        productos_disponibles = self.tablero.get_objetivos_disponibles()
        for i, producto in enumerate(configuracion['productos']):
            if i < len(productos_disponibles):
                # Restaurar el producto a su posición original
                self.tablero.mover_producto(productos_disponibles[i], producto.get_indice())

    def _configurar_objetivos_orden(self, orden):
        """
        Configura los objetivos en el tablero según la orden dada.
        """
        # Limpiamos los objetivos actuales
        self.tablero.limpiar_tablero()
        self.tablero.set_inicio(self.inicio.get_indice())
        # Configuramos los nuevos objetivos
        # print(orden)
        for objetivo in orden:
            indice = self.tablero.buscar_por_caracter(objetivo)
            self.tablero.set_objetivo(int(indice))
        
        self.objetivos = self.tablero.get_objetivos()
        self.nodo_inicio = self.tablero.get_inicio()

    def _seleccion_ruleta(self, poblacion, fitness_valores):
        """
        Implementa la selección por ruleta donde los individuos con mayor fitness
        tienen mayor probabilidad de ser seleccionados.
        """
        # Calculamos la suma total de fitness
        suma_fitness = sum(fitness_valores)
        
        if suma_fitness == 0:  # Evitar división por cero
            # Si todos tienen fitness 0, selección aleatoria
            return random.choice(poblacion)
        
        # Generamos un número aleatorio entre 0 y la suma total
        valor = random.uniform(0, suma_fitness)
        
        # Seleccionamos el individuo correspondiente
        acumulado = 0
        for i, fitness in enumerate(fitness_valores):
            acumulado += fitness
            if acumulado >= valor:
                return poblacion[i].copy()
        
        # Por si acaso, retornamos el último
        return poblacion[-1].copy()

    def _cruce_ordenado(self, padre1, padre2):
        """
        Implementa el operador de cruce para permutaciones (Order Crossover - OX).
        Este operador mantiene el orden relativo de los elementos.
        """
        n = len(padre1)
        
        # Elegimos dos puntos de corte aleatorios
        punto1 = random.randint(0, n-1)
        punto2 = random.randint(0, n-1)
        
        # Aseguramos que punto1 <= punto2
        if punto1 > punto2:
            punto1, punto2 = punto2, punto1
        
        # Creamos los hijos inicializándolos con valores None
        hijo1 = [None] * n
        hijo2 = [None] * n
        
        # Copiamos el segmento entre los puntos de corte
        for i in range(punto1, punto2+1):
            hijo1[i] = padre1[i]
            hijo2[i] = padre2[i]
        
        # Completamos el resto de los hijos
        self._completar_hijo(hijo1, padre2, punto1, punto2)
        self._completar_hijo(hijo2, padre1, punto1, punto2)
        
        return hijo1, hijo2

    def _completar_hijo(self, hijo, padre, punto1, punto2):
        """
        Completa un hijo parcial usando genes del padre en el orden correcto.
        """
        n = len(hijo)
        # Conjunto de elementos ya presentes en el hijo
        elementos_hijo = set(gene for gene in hijo if gene is not None)
        
        # Índice para insertar en el hijo
        idx_hijo = (punto2 + 1) % n
        
        # Recorremos el padre desde punto2+1 hasta punto2 (dando la vuelta)
        for i in range(n):
            idx_padre = (punto2 + 1 + i) % n
            # Si el elemento del padre no está en el hijo, lo añadimos
            if padre[idx_padre] not in elementos_hijo:
                hijo[idx_hijo] = padre[idx_padre]
                elementos_hijo.add(padre[idx_padre])
                idx_hijo = (idx_hijo + 1) % n
                # Si llegamos al inicio del segmento copiado, saltamos al final
                if idx_hijo == punto1:
                    idx_hijo = (punto2 + 1) % n

    def _mutacion(self, individuo):
        """
        Implementa la mutación por intercambio (swap mutation).
        Intercambia dos posiciones aleatorias en el individuo.
        """
        n = len(individuo)
        if n <= 1:
            return  # No hay suficientes elementos para intercambiar
        
        # Seleccionamos dos posiciones aleatorias diferentes
        pos1 = random.randint(0, n-1)
        pos2 = random.randint(0, n-1)
        while pos1 == pos2:
            pos2 = random.randint(0, n-1)
        
        # Intercambiamos los elementos
        individuo[pos1], individuo[pos2] = individuo[pos2], individuo[pos1]

    def _aplicar_solucion(self, individuo, productos_originales):
        """
        Aplica la solución encontrada al tablero, reubicando los productos.
        """
        # Por cada producto en el individuo, lo movemos a la posición correspondiente
        for i, producto in enumerate(individuo):
            if i < len(productos_originales):
                # Mover el producto a su nueva posición
                self.tablero.mover_producto(productos_originales[i], producto.get_indice())