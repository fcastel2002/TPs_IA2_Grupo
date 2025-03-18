# algoritmo_genetico.py
import sys
import random
import math
import time
import numpy as np
import pygame
import matplotlib.pyplot as plt
from constantes import *
from agente import Agente

class AlgoritmoGenetico:
    """
    Implementa un algoritmo genético para optimizar la disposición de estanterías.
    Utiliza recocido simulado como función de evaluación para determinar la calidad
    de cada disposición.
    """
    def __init__(self, tablero, ordenes, tam_poblacion=10, tasa_mutacion=0.2, 
                 tasa_cruce=0.8, num_generaciones=50, elitismo=2):
        """
        Inicializa el algoritmo genético.
        
        Args:
            tablero: Tablero con la disposición original de estanterías
            ordenes: Lista de órdenes desde el archivo CSV
            tam_poblacion: Tamaño de la población
            tasa_mutacion: Probabilidad de mutación de un gen
            tasa_cruce: Probabilidad de cruce entre individuos
            num_generaciones: Número de generaciones a evolucionar
            elitismo: Número de mejores individuos que pasan directamente
        """
        self.tablero = tablero
        self.ordenes = ordenes
        self.tam_poblacion = tam_poblacion
        self.tasa_mutacion = tasa_mutacion
        self.tasa_cruce = tasa_cruce
        self.num_generaciones = num_generaciones
        self.elitismo = elitismo
        
        # Obtener IDs de las estanterías
        self.estanterias = self._obtener_ids_estanterias()
        print(f"Estanterías identificadas: {len(self.estanterias)}")
        
        # Crear la población inicial
        self.poblacion = self._inicializar_poblacion()
        
        # Mejor individuo encontrado
        self.mejor_individuo = None
        self.mejor_fitness = float('inf')
        
        # Historial para visualización
        self.historial_fitness = []
        self.historial_promedio = []
        self.historial_diversidad = []
        
        # Cache para optimizar cálculos repetidos
        self._cache_fitness = {}
        
        # Crear agente para evaluación
        self.agente = Agente(self.tablero)
        
        # Guardar la disposición original de estanterías para restaurarla después
    def _desactivar_visualizacion(self):
        """
        Desactiva temporalmente la visualización del tablero para mejorar rendimiento.
        Evita problemas con Pygame deshabilitando las actualizaciones gráficas.
        """
        # Guardar estado original de dibujar del tablero
        if hasattr(self.tablero, 'dibujar_original'):
            return  # Ya está desactivada
        
        # Guardar referencia al método original
        self.tablero.dibujar_original = self.tablero.dibujar
        
        # Reemplazar con función vacía que no hace nada
        def dibujar_noop(*args, **kwargs):
            pass
        
        # Asignar la función vacía
        self.tablero.dibujar = dibujar_noop
        
        # También desactivar pygame.display.flip() para evitar actualizaciones de pantalla
        if 'pygame' in sys.modules:
            self.pygame_flip_original = pygame.display.flip
            pygame.display.flip = lambda: None
        
        print("Visualización desactivada para mejorar rendimiento.")
        
    def _restaurar_visualizacion(self):
        """
        Restaura la visualización del tablero y las funciones de Pygame.
        """
        if hasattr(self.tablero, 'dibujar_original'):
            self.tablero.dibujar = self.tablero.dibujar_original
            delattr(self.tablero, 'dibujar_original')
        
        # Restaurar pygame.display.flip() si fue desactivado
        if hasattr(self, 'pygame_flip_original'):
            pygame.display.flip = self.pygame_flip_original
            delattr(self, 'pygame_flip_original')
        
        print("Visualización restaurada.")
        
    def _obtener_ids_estanterias(self):
        """Obtiene los IDs de todas las estanterías del tablero."""
        ids = []
        for casillero in self.tablero.casilleros:
            if not casillero.libre and casillero.caracter != "C" and casillero.caracter.isdigit():
                ids.append(casillero.caracter)
        return sorted(ids)  # Ordenamos para consistencia
    
    def _inicializar_poblacion(self):
        """Crea la población inicial de individuos aleatorios."""
        poblacion = []
        print("Inicializando población inicial...")
        for i in range(self.tam_poblacion):
            # Crear una permutación aleatoria
            individuo = self.estanterias.copy()
            random.shuffle(individuo)
            poblacion.append(individuo)
            print(f"\rIndividuo {i+1}/{self.tam_poblacion} creado", end="")
        print("\nPoblación inicial creada correctamente.")
        return poblacion
    
    def _aplicar_mapeo_al_tablero(self, individuo):
        """
        Aplica temporalmente la disposición de estanterías del individuo al tablero.
        Evita la serialización que causa problemas con los objetos de Pygame.
        """
        # Guardar estado actual para restaurarlo después
        estado_original = {}
        for casillero in self.tablero.casilleros:
            if not casillero.libre and casillero.caracter in self.estanterias:
                estado_original[casillero.get_indice()] = casillero.caracter
        
        # Crear mapeo de ID original a nueva posición
        mapeo = {original: nuevo for original, nuevo in zip(self.estanterias, individuo)}
        
        # Aplicar mapeo al tablero
        for casillero in self.tablero.casilleros:
            if not casillero.libre and casillero.caracter in self.estanterias:
                casillero.caracter = mapeo[casillero.caracter]
        
        return estado_original
    
    def evaluar_fitness(self, individuo):
        """
        Evalúa la aptitud de un individuo usando recocido simulado para cada orden.
        Versión optimizada con mejor manejo de errores.
        """
        # Convertir a tupla para poder usarla como clave de diccionario
        individuo_tupla = tuple(individuo)
        
        # Verificar si ya calculamos este fitness
        if individuo_tupla in self._cache_fitness:
            return self._cache_fitness[individuo_tupla]
        
        try:
            # Aplicar la disposición del individuo al tablero y guardar estado original
            estado_original = self._aplicar_mapeo_al_tablero(individuo)
            
            # Calcular costo total para todas las órdenes usando recocido simulado
            costo_total = 0
            
            # Limitar el número de órdenes a evaluar para mejorar rendimiento en etapas tempranas
            ordenes_a_evaluar = self.ordenes[:min(len(self.ordenes), 10)]  # Evaluar solo las primeras 10 órdenes
            
            for orden in ordenes_a_evaluar:
                # Limpiar objetivos anteriores
                self.tablero.limpiar_tablero()
                
                # Establecer punto de inicio (celda C)
                celda_c = self.tablero.get_celda_c()
                self.tablero.set_inicio(celda_c.get_indice())
                
                # Configurar objetivos para esta orden
                objetivos_validos = 0
                for id_estanteria in orden:
                    # Buscar casillero correspondiente
                    indice = self.tablero.buscar_por_caracter(str(id_estanteria))
                    if indice is not None:
                        self.tablero.set_objetivo(indice)
                        objetivos_validos += 1
                
                # Si no hay objetivos válidos, continuar con la siguiente orden
                if objetivos_validos == 0:
                    continue
                
                # Usar recocido simulado para encontrar la mejor ruta
                agente_evaluador = Agente(self.tablero)
                
                # Parámetros más eficientes para recocido simulado
                mejor_ruta = agente_evaluador.temple_simulado_multi_objetivo(
                    max_iteraciones=50,  # Reducido para eficiencia
                    temp_inicial=30,
                    factor_enfriamiento=0.9
                )
                
                # Calcular el costo de esta ruta
                if mejor_ruta is not None:
                    costo_orden = len(mejor_ruta) - 1  # Longitud del camino menos 1
                else:
                    # Penalización alta pero no infinita si no se encuentra ruta
                    costo_orden = 1000 * len(orden)
                
                costo_total += costo_orden
            
            # Restaurar la disposición original del tablero
            for indice, caracter in estado_original.items():
                self.tablero.casilleros[indice].caracter = caracter
            
            # Guardar en caché
            self._cache_fitness[individuo_tupla] = costo_total
            
            return costo_total
        
        except Exception as e:
            # Log del error y retorno de un valor de fitness muy alto
            self._log(f"Error en evaluar_fitness: {str(e)}", "ERROR")
            import traceback
            self._log(traceback.format_exc(), "ERROR")
            
            # Restaurar tablero al estado original si es posible
            try:
                if 'estado_original' in locals():
                    for indice, caracter in estado_original.items():
                        self.tablero.casilleros[indice].caracter = caracter
            except:
                pass
            
            return float('inf')  # Fitness extremadamente malo para individuos que causan errores
    def generar_mapa_calor(self):
        """
        Genera un mapa de calor que muestra la frecuencia de visitas a cada casillero
        basado en las órdenes procesadas con la mejor disposición.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Aplicar la mejor solución al tablero
        self._aplicar_mapeo_al_tablero(self.mejor_individuo)
        
        # Crear matriz para mapa de calor
        mapa_calor = np.zeros((self.tablero.filas, self.tablero.columnas))
        
        # Contador de visitas para cada casillero
        for orden in self.ordenes:
            # Limpiar objetivos anteriores
            self.tablero.limpiar_tablero()
            
            # Establecer punto de inicio (celda C)
            celda_c = self.tablero.get_celda_c()
            self.tablero.set_inicio(celda_c.get_indice())
            
            # Configurar objetivos para esta orden
            for id_estanteria in orden:
                indice = self.tablero.buscar_por_caracter(str(id_estanteria))
                if indice is not None:
                    self.tablero.set_objetivo(indice)
            
            # Usar recocido simulado para encontrar la mejor ruta
            agente_evaluador = Agente(self.tablero)
            mejor_ruta = agente_evaluador.temple_simulado_multi_objetivo()
            
            # Incrementar contador de visitas para cada casillero en la ruta
            if mejor_ruta:
                for casillero in mejor_ruta:
                    fila = casillero.y // CELL_SIZE
                    columna = casillero.x // CELL_SIZE
                    mapa_calor[fila][columna] += 1
        
        # Crear visualización
        plt.figure(figsize=(12, 10))
        
        # Generar mapa de calor
        plt.imshow(mapa_calor, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Frecuencia de visitas')
        
        # Añadir etiquetas para estanterías
        for casillero in self.tablero.casilleros:
            if not casillero.libre:
                fila = casillero.y // CELL_SIZE
                columna = casillero.x // CELL_SIZE
                plt.text(columna, fila, casillero.caracter, 
                        ha='center', va='center', color='white',
                        fontweight='bold')
        
        plt.title('Mapa de calor de frecuencia de visitas con la disposición optimizada')
        plt.xlabel('Columna')
        plt.ylabel('Fila')
        plt.tight_layout()
        plt.savefig('mapa_calor_optimizacion.png')
        plt.show()
        
        # Restaurar estado original
        estado_original = {}
        for indice, casillero in enumerate(self.tablero.casilleros):
            if not casillero.libre and casillero.caracter in self.estanterias:
                estado_original[indice] = casillero.caracter
        
        for indice, caracter in estado_original.items():
            self.tablero.casilleros[indice].caracter = caracter
        
        print("\nMapa de calor generado y guardado como 'mapa_calor_optimizacion.png'")   
    def seleccion_torneo(self, k=3):
        """Selecciona un individuo mediante torneo."""
        # Seleccionar k individuos aleatorios
        candidatos = random.sample(range(self.tam_poblacion), k)
        
        # Encontrar el mejor individuo
        mejor_idx = candidatos[0]
        mejor_fitness = self.evaluar_fitness(self.poblacion[mejor_idx])
        
        for idx in candidatos[1:]:
            fitness = self.evaluar_fitness(self.poblacion[idx])
            if fitness < mejor_fitness:
                mejor_fitness = fitness
                mejor_idx = idx
        
        return self.poblacion[mejor_idx]
    
    def cruce_pmx(self, padre1, padre2):
        """
        Implementa el operador de cruce PMX (Partially Mapped Crossover) para problemas de permutación.
        Versión optimizada que evita bucles infinitos y garantiza permutaciones válidas.
        
        Args:
            padre1, padre2: Individuos (permutaciones) a cruzar
        
        Returns:
            Tupla con dos hijos resultantes del cruce
        """
        # Validar entrada
        if len(padre1) != len(padre2):
            raise ValueError("Los padres deben tener la misma longitud")
        
        # Copiar padres para no modificarlos
        hijo1 = padre1.copy()
        hijo2 = padre2.copy()
        
        # Si no se cumple la probabilidad, devolver copias de los padres
        if random.random() > self.tasa_cruce:
            return hijo1, hijo2
        
        # Obtener longitud
        longitud = len(padre1)
        
        # Elegir dos puntos de corte aleatorios (asegurar que punto1 < punto2)
        punto1 = random.randint(0, longitud - 2)
        punto2 = random.randint(punto1 + 1, longitud - 1)
        
        # Crear mapeos para resolver conflictos
        mapeo1 = {}  # Mapeo de padre2 a padre1 en la sección de cruce
        mapeo2 = {}  # Mapeo de padre1 a padre2 en la sección de cruce
        
        # Intercambiar segmentos entre los puntos de corte
        for i in range(punto1, punto2 + 1):
            # Guardar valores originales antes del intercambio
            valor1 = hijo1[i]
            valor2 = hijo2[i]
            
            # Realizar intercambio
            hijo1[i] = valor2
            hijo2[i] = valor1
            
            # Actualizar mapeos
            mapeo1[valor2] = valor1
            mapeo2[valor1] = valor2
        
        # Resolver conflictos en hijo1
        for i in range(longitud):
            # Solo procesar posiciones fuera de la sección de cruce
            if i < punto1 or i > punto2:
                # Mientras el valor en la posición i esté en el mapeo (es decir, causa conflicto)
                valor = hijo1[i]
                contador = 0  # Contador para evitar bucles infinitos
                max_iteraciones = longitud  # Límite máximo de iteraciones
                
                while valor in mapeo1 and contador < max_iteraciones:
                    valor = mapeo1[valor]  # Seguir la cadena de mapeo
                    contador += 1
                
                # Si salimos por contador, hay un problema en el mapeo
                if contador >= max_iteraciones:
                    # Solución alternativa: asignar un valor no utilizado
                    valores_usados = set(hijo1[punto1:punto2+1])
                    for posible_valor in padre1:
                        if posible_valor not in valores_usados:
                            valor = posible_valor
                            valores_usados.add(posible_valor)
                            break
                
                hijo1[i] = valor
        
        # Resolver conflictos en hijo2
        for i in range(longitud):
            # Solo procesar posiciones fuera de la sección de cruce
            if i < punto1 or i > punto2:
                # Mientras el valor en la posición i esté en el mapeo (es decir, causa conflicto)
                valor = hijo2[i]
                contador = 0  # Contador para evitar bucles infinitos
                max_iteraciones = longitud  # Límite máximo de iteraciones
                
                while valor in mapeo2 and contador < max_iteraciones:
                    valor = mapeo2[valor]  # Seguir la cadena de mapeo
                    contador += 1
                
                # Si salimos por contador, hay un problema en el mapeo
                if contador >= max_iteraciones:
                    # Solución alternativa: asignar un valor no utilizado
                    valores_usados = set(hijo2[punto1:punto2+1])
                    for posible_valor in padre2:
                        if posible_valor not in valores_usados:
                            valor = posible_valor
                            valores_usados.add(posible_valor)
                            break
                
                hijo2[i] = valor
        
        # Verificar que los hijos son permutaciones válidas
        self._verificar_permutacion(hijo1, "Hijo1 después de PMX")
        self._verificar_permutacion(hijo2, "Hijo2 después de PMX")
        
        return hijo1, hijo2

    def _verificar_permutacion(self, individuo, etiqueta=""):
        """
        Verifica que un individuo sea una permutación válida y lo repara si es necesario.
        
        Args:
            individuo: Individuo a verificar
            etiqueta: Etiqueta para mensajes de depuración
        
        Returns:
            True si es una permutación válida, False si requirió reparación
        """
        # Obtener conjunto de valores esperados (todos los IDs de estanterías)
        valores_esperados = set(self.estanterias)
        
        # Obtener conjunto de valores actuales
        valores_actuales = set(individuo)
        
        # Verificar si hay valores faltantes o duplicados
        valores_faltantes = valores_esperados - valores_actuales
        valores_duplicados = []
        
        # Contar ocurrencias para encontrar duplicados
        conteo = {}
        for valor in individuo:
            conteo[valor] = conteo.get(valor, 0) + 1
            if conteo[valor] > 1:
                valores_duplicados.append(valor)
        
        # Si no hay problemas, retornar True
        if not valores_faltantes and not valores_duplicados:
            return True
        
        # Si hay problemas, reparar la permutación
        if valores_faltantes and valores_duplicados:
            # Reemplazar duplicados con valores faltantes
            for i, valor in enumerate(individuo):
                if valor in valores_duplicados and conteo[valor] > 1:
                    # Tomar un valor faltante
                    valor_faltante = valores_faltantes.pop()
                    individuo[i] = valor_faltante
                    conteo[valor] -= 1
                    
                    # Si ya no hay más duplicados de este valor, removerlo de la lista
                    if conteo[valor] == 1:
                        valores_duplicados.remove(valor)
                    
                    # Si no hay más valores faltantes, salir
                    if not valores_faltantes:
                        break
        
        return False
    def mutacion(self, individuo):
        """Aplica mutación de intercambio a un individuo."""
        # Copiar individuo
        individuo_mutado = individuo.copy()
        
        # Para cada gen, aplicar mutación con probabilidad tasa_mutacion
        for i in range(len(individuo)):
            if random.random() < self.tasa_mutacion:
                # Elegir otro gen aleatorio para intercambiar
                j = random.randint(0, len(individuo) - 1)
                
                # Intercambiar genes
                individuo_mutado[i], individuo_mutado[j] = individuo_mutado[j], individuo_mutado[i]
        
        return individuo_mutado
    
    def calcular_diversidad(self):
        """Calcula la diversidad de la población como la desviación estándar de fitness."""
        fitness_valores = [self.evaluar_fitness(ind) for ind in self.poblacion]
        return np.std(fitness_valores) if len(fitness_valores) > 1 else 0
    
    def _mostrar_barra_progreso(self, generacion, fitness_actual, promedio_actual, tiempo_gen):
        """
        Muestra una barra de progreso con información detallada sobre la generación actual.
        
        Args:
            generacion: Número de generación actual
            fitness_actual: Mejor fitness en la generación actual
            promedio_actual: Fitness promedio en la generación actual
            tiempo_gen: Tiempo empleado en la generación actual
        """
        progreso = (generacion + 1) / self.num_generaciones
        ancho_barra = 30
        barra = '█' * int(ancho_barra * progreso) + '░' * (ancho_barra - int(ancho_barra * progreso))
        
        # Calcular tiempo total y estimado
        tiempo_transcurrido = time.time() - self._tiempo_inicio
        
        if generacion > 0:
            tiempo_promedio = tiempo_transcurrido / (generacion + 1)
            tiempo_restante = tiempo_promedio * (self.num_generaciones - generacion - 1)
            info_tiempo = f" | {tiempo_transcurrido:.1f}s/{tiempo_restante:.1f}s"
        else:
            info_tiempo = ""
        
        # Mostrar información de progreso
        print(f"\r[{barra}] {progreso*100:.1f}% | Gen: {generacion+1}/{self.num_generaciones}", end='')
        print(f" | Mejor: {fitness_actual:.1f}", end='')
        print(f" | Prom: {promedio_actual:.1f}", end='')
        print(f" | T.Gen: {tiempo_gen:.2f}s", end='')
        print(info_tiempo, end='')
    
    def ejecutar(self, tiempo_maximo=300):  # 5 minutos por defecto
        """
        Ejecuta el algoritmo genético con control de tiempo para evitar bloqueos.
        
        Args:
            tiempo_maximo: Tiempo máximo de ejecución en segundos
        
        Returns:
            Tupla con el mejor individuo encontrado y su fitness
        """
        print("\n" + "="*70)
        print(f"Iniciando algoritmo genético con {self.tam_poblacion} individuos y {self.num_generaciones} generaciones")
        print(f"Tasa de mutación: {self.tasa_mutacion}, Tasa de cruce: {self.tasa_cruce}, Elitismo: {self.elitismo}")
        print(f"Tiempo máximo de ejecución: {tiempo_maximo} segundos")
        print("="*70 + "\n")
        
        # Desactivar visualización durante el cálculo
        self._desactivar_visualizacion()
        
        self._tiempo_inicio = time.time()
        tiempo_limite = self._tiempo_inicio + tiempo_maximo
        
        try:
            # Evaluar población inicial
            print("Evaluando población inicial...")
            fitness_inicial = []
            for i, ind in enumerate(self.poblacion):
                fitness = self.evaluar_fitness(ind)
                fitness_inicial.append(fitness)
                print(f"\rEvaluando individuo {i+1}/{self.tam_poblacion}, fitness: {fitness:.2f}", end="")
                
                # Verificar tiempo límite
                if time.time() > tiempo_limite:
                    print("\nTiempo límite alcanzado durante evaluación inicial.")
                    raise TimeoutError("Tiempo máximo de ejecución excedido")
            
            print()  # Nueva línea después del progreso
            
            # Encontrar el mejor individuo inicial
            mejor_idx = fitness_inicial.index(min(fitness_inicial))
            self.mejor_individuo = self.poblacion[mejor_idx].copy()
            self.mejor_fitness = min(fitness_inicial)
            
            # Registrar métricas iniciales
            self.historial_fitness.append(self.mejor_fitness)
            self.historial_promedio.append(sum(fitness_inicial) / len(fitness_inicial))
            
            print(f"Fitness inicial - Mejor: {self.mejor_fitness:.2f}, Promedio: {self.historial_promedio[0]:.2f}")
            print("\nEvolucionando población...\n")
            
            # Iterar por generaciones
            for generacion in range(self.num_generaciones):
                tiempo_gen_inicio = time.time()
                
                # Verificar tiempo límite
                if tiempo_gen_inicio > tiempo_limite:
                    print(f"\nTiempo límite alcanzado después de {generacion} generaciones.")
                    break
                
                # Crear nueva población
                nueva_poblacion = []
                
                # Elitismo: pasar los mejores individuos directamente
                fitness_actual = [self.evaluar_fitness(ind) for ind in self.poblacion]
                indices_ordenados = sorted(range(len(fitness_actual)), key=lambda i: fitness_actual[i])
                
                for i in range(min(self.elitismo, len(indices_ordenados))):
                    nueva_poblacion.append(self.poblacion[indices_ordenados[i]].copy())
                
                # Generar el resto de la población mediante selección, cruce y mutación
                intentos_cruce = 0
                max_intentos = self.tam_poblacion * 10  # Límite de intentos para evitar bucles
                
                while len(nueva_poblacion) < self.tam_poblacion and intentos_cruce < max_intentos:
                    # Verificar tiempo límite
                    if time.time() > tiempo_limite:
                        print(f"\nTiempo límite alcanzado durante generación {generacion+1}.")
                        break
                    
                    # Seleccionar padres
                    padre1 = self.seleccion_torneo()
                    padre2 = self.seleccion_torneo()
                    
                    try:
                        # Cruzar con límite de tiempo
                        tiempo_inicio_cruce = time.time()
                        hijo1, hijo2 = self.cruce_pmx(padre1, padre2)
                        
                        # Si el cruce toma demasiado tiempo, usar copias de los padres
                        if time.time() - tiempo_inicio_cruce > 1.0:  # Más de 1 segundo
                            print(f"Advertencia: Cruce PMX tomó demasiado tiempo, usando copias.")
                            hijo1, hijo2 = padre1.copy(), padre2.copy()
                        
                        # Mutar
                        hijo1 = self.mutacion(hijo1)
                        hijo2 = self.mutacion(hijo2)
                        
                        # Agregar a nueva población
                        nueva_poblacion.append(hijo1)
                        if len(nueva_poblacion) < self.tam_poblacion:
                            nueva_poblacion.append(hijo2)
                        
                    except Exception as e:
                        print(f"Error en cruce/mutación: {str(e)}")
                        # En caso de error, usar copias de los padres
                        if len(nueva_poblacion) < self.tam_poblacion:
                            nueva_poblacion.append(padre1.copy())
                        if len(nueva_poblacion) < self.tam_poblacion:
                            nueva_poblacion.append(padre2.copy())
                    
                    intentos_cruce += 1
                
                # Si no se completó la población, llenarla con copias de individuos existentes
                if len(nueva_poblacion) < self.tam_poblacion:
                    print(f"Advertencia: Población incompleta ({len(nueva_poblacion)}/{self.tam_poblacion}). Completando...")
                    while len(nueva_poblacion) < self.tam_poblacion:
                        idx = random.randint(0, len(self.poblacion) - 1)
                        nueva_poblacion.append(self.poblacion[idx].copy())
                
                # Actualizar población
                self.poblacion = nueva_poblacion
                
                # Evaluar nueva población
                fitness_actual = [self.evaluar_fitness(ind) for ind in self.poblacion]
                promedio_actual = sum(fitness_actual) / len(fitness_actual)
                mejor_actual = min(fitness_actual)
                mejor_idx = fitness_actual.index(mejor_actual)
                
                # Actualizar mejor individuo si se encontró uno mejor
                if mejor_actual < self.mejor_fitness:
                    self.mejor_fitness = mejor_actual
                    self.mejor_individuo = self.poblacion[mejor_idx].copy()
                    print(f"\nNueva mejor solución en generación {generacion+1}: {self.mejor_fitness:.2f}")
                
                # Registrar métricas
                self.historial_fitness.append(self.mejor_fitness)
                self.historial_promedio.append(promedio_actual)
                
                # Calcular tiempo de generación
                tiempo_gen = time.time() - tiempo_gen_inicio
                
                # Mostrar progreso
                self._mostrar_barra_progreso(generacion, self.mejor_fitness, promedio_actual, tiempo_gen)
                
                # Verificar si se ha alcanzado convergencia
                if generacion > 10 and all(abs(self.historial_fitness[-i-1] - self.historial_fitness[-i-2]) < 0.001 for i in range(5)):
                    print(f"\nConvergencia alcanzada después de {generacion+1} generaciones.")
                    break
            
            # Mostrar tiempo total
            tiempo_total = time.time() - self._tiempo_inicio
            print(f"\nOptimización completada en {tiempo_total:.2f} segundos")
            print(f"Mejor fitness encontrado: {self.mejor_fitness:.2f}")
            
            # Verificar mejor solución
            if self.mejor_individuo is None:
                print("ADVERTENCIA: No se encontró solución. Usando mejor individuo de población final.")
                mejor_idx = fitness_actual.index(min(fitness_actual))
                self.mejor_individuo = self.poblacion[mejor_idx].copy()
                self.mejor_fitness = min(fitness_actual)
        
        except Exception as e:
            print(f"\nError durante la ejecución: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Intentar recuperar la mejor solución encontrada hasta ahora
            if not hasattr(self, 'mejor_individuo') or self.mejor_individuo is None:
                print("Recuperando mejor solución de la población actual...")
                try:
                    fitness_actual = [self.evaluar_fitness(ind) for ind in self.poblacion]
                    mejor_idx = fitness_actual.index(min(fitness_actual))
                    self.mejor_individuo = self.poblacion[mejor_idx].copy()
                    self.mejor_fitness = min(fitness_actual)
                except:
                    print("No se pudo recuperar una solución.")
                    # Crear una solución aleatoria como último recurso
                    self.mejor_individuo = self.estanterias.copy()
                    random.shuffle(self.mejor_individuo)
                    self.mejor_fitness = float('inf')
        
        finally:
            # Restaurar visualización
            self._restaurar_visualizacion()
        
        return self.mejor_individuo, self.mejor_fitness
    
    def aplicar_mejor_solucion(self, generar_mapa_calor=True):
        """
        Aplica la mejor solución encontrada al tablero y opcionalmente genera un mapa de calor.
        """
        if self.mejor_individuo is None:
            print("No hay solución para aplicar. Ejecute el algoritmo primero.")
            return
        
        print("\nAplicando la mejor solución al tablero...")
        
        # Crear mapeo de ID original a nueva posición
        mapeo = {original: nuevo for original, nuevo in zip(self.estanterias, self.mejor_individuo)}
        
        # Mostrar mapeo
        print("\nMapeo de estanterías (Original -> Nueva):")
        for i, (original, nuevo) in enumerate(mapeo.items()):
            print(f"{original} -> {nuevo}", end="\t")
            if (i + 1) % 5 == 0:  # 5 mapeos por línea
                print()
        print()
        
        # Aplicar mapeo al tablero
        for casillero in self.tablero.casilleros:
            if not casillero.libre and casillero.caracter in self.estanterias:
                casillero.caracter = mapeo[casillero.caracter]
        
        print("\nSolución aplicada al tablero correctamente.")
        
        # Generar mapa de calor si se solicita
        if generar_mapa_calor:
            self.generar_mapa_calor()
        
    def visualizar_resultados(self):
        """Visualiza la evolución de las métricas a lo largo de las generaciones."""
        try:
            # Crear figura con tres subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
            
            # Gráfico 1: Evolución del fitness
            ax1.plot(range(len(self.historial_fitness)), self.historial_fitness, 'b-', 
                     label='Mejor fitness', linewidth=2)
            ax1.plot(range(len(self.historial_promedio)), self.historial_promedio, 'r-', 
                     label='Fitness promedio', linewidth=2)
            
            ax1.set_title('Evolución del fitness durante las generaciones', fontsize=14)
            ax1.set_xlabel('Generación', fontsize=12)
            ax1.set_ylabel('Fitness (menor es mejor)', fontsize=12)
            ax1.grid(True)
            ax1.legend(fontsize=10)
            
            # Gráfico 2: Evolución de la diversidad
            ax2.plot(range(len(self.historial_diversidad)), self.historial_diversidad, 'g-', 
                     linewidth=2)
            
            ax2.set_title('Evolución de la diversidad de la población', fontsize=14)
            ax2.set_xlabel('Generación', fontsize=12)
            ax2.set_ylabel('Diversidad (desviación estándar)', fontsize=12)
            ax2.grid(True)
            
            # Gráfico 3: Diferencia entre mejor y promedio
            diferencia = [p - m for p, m in zip(self.historial_promedio, self.historial_fitness)]
            ax3.plot(range(len(diferencia)), diferencia, 'm-', linewidth=2)
            
            ax3.set_title('Diferencia entre fitness promedio y mejor fitness', fontsize=14)
            ax3.set_xlabel('Generación', fontsize=12)
            ax3.set_ylabel('Diferencia', fontsize=12)
            ax3.grid(True)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error al visualizar resultados: {e}")
            print("Asegúrese de tener matplotlib instalado: pip install matplotlib")