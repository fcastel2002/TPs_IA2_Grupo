from interfaz import Tablero, MenuSelector, Casillero, pygame, sys
from constantes import*
from agente import Agente, SuperAgente
import sys
import time
import os
import psutil

class Aplicacion:
    def __init__(self, tablero, archivo):
        self.__filas = tablero['filas']
        self.__columnas = tablero['columnas']
        self.__running = False
        self.__algorithm_running = False
        self.__inicio = None
        self.__objetivos = []
        # Inicialización 
        pygame.init()
        self.__screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tablero : Tablero = Tablero(self.__screen,tablero['filas'],tablero['columnas'])
        self.llenar_tablero()
        pygame.display.set_caption("Tablero con Pygame")
        self.archivo = archivo
        self.menu : MenuSelector = MenuSelector(self.archivo,self.__screen)
        self.__duracion_algoritmo = 0
        
    def medir_memoria(self):
        proceso = psutil.Process(os.getpid())
        memoria_mb = proceso.memory_info().rss / 1024 / 1024
        return memoria_mb
    
    def run(self):
        # Bucle principal
        self.__running = True
        while self.__running:
            self.manejar_eventos()
            self.tablero.dibujar(not self.__algorithm_running)
        pygame.quit()
        sys.exit()
        
    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            
            # Eventos de teclado
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__running = False
                
                # Iniciar algoritmo con la tecla ESPACIO
                elif event.key == pygame.K_SPACE and not self.__algorithm_running:
                    self.ejecutar_algoritmo()
                    
                
                # Limpiar camino con la tecla C
                elif event.key == pygame.K_c:
                    self.tablero.limpiar_tablero()
                # Desplegar manú interactivo con tecla M
                elif event.key == pygame.K_m:
                    objetivos = self.menu.main()
                    for objetivo in objetivos:
                        indice = self.tablero.buscar_por_caracter(objetivo)
                        self.tablero.set_objetivo(int(indice))
                
                # Ejecutar algoritmo genetico con tecla G
                elif event.key == pygame.K_g:
                    self.algoritmo_genetico()
                # Cambiar de lugar estanterías con tecla E
                elif event.key == pygame.K_e:
                    
                    self.mapa_de_calor()
                    # nuevas_estanterias = []
                    # for i in range(48):
                    #     nuevas_estanterias.append(48-i)
                    # self.tablero.cambiar_estanterias(nuevas_estanterias)
                    
                    # estanterias = self.tablero.obtener_estanterias()
                    # for estanteria in estanterias:
                    #     print(estanteria)
            
            # Eventos de ratón
            if not self.__algorithm_running:
                # Colocar inicio/fin con el ratón
                if pygame.mouse.get_pressed()[0]:  # Botón izquierdo
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // CELL_SIZE, pos[0] // CELL_SIZE
                    indice = col + row * self.__columnas
                    # Shift + clic izquierdo para colocar punto de inicio
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.tablero.set_inicio(indice)
                        
                    # Ctrl + clic izquierdo para colocar punto de destino
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.tablero.set_objetivo(indice)
                        
                        
                        
    def ejecutar_algoritmo(self):
        self.__algorithm_running = True
        self.__agente : Agente = Agente(self.tablero)
        
        # Medimos memoria e inicializamos contador de tiempo antes de ejecutar algoritmo
        memoria_antes = self.medir_memoria()
        tiempo_inicio = time.time()
        
        #Ejecutamos algoritmo
        self.__agente.encontrar_ruta() 
        
        
        # Medimos consumo de memoria y tiempo de ejecución del algoritmo
        tiempo_fin = time.time()
        self.__duracion_algoritmo = tiempo_fin - tiempo_inicio
        memoria_despues = self.medir_memoria()
        print(f"El algoritmo tardó {self.__duracion_algoritmo:.7f} segundos en ejecutarse")
        print(f"Consumo de memoria: {memoria_despues - memoria_antes:.2f} MB")
        self.__algorithm_running = False
        
    def algoritmo_genetico(self):
        self.__algorithm_running = True
        self.__agente : SuperAgente = SuperAgente(self.tablero,self.archivo)
        
        # Medimos memoria e inicializamos contador de tiempo antes de ejecutar algoritmo
        memoria_antes = self.medir_memoria()
        tiempo_inicio = time.time()
        
        #Ejecutamos algoritmo
        mejor_ubicacion = self.__agente.algoritmo_genetico() 
        self.tablero.cambiar_estanterias(mejor_ubicacion)
        self.mapa_de_calor()
        # Medimos consumo de memoria y tiempo de ejecución del algoritmo
        tiempo_fin = time.time()
        self.__duracion_algoritmo = tiempo_fin - tiempo_inicio
        memoria_despues = self.medir_memoria()
        print(f"El algoritmo tardó {self.__duracion_algoritmo:.7f} segundos en ejecutarse")
        print(f"Consumo de memoria: {memoria_despues - memoria_antes:.2f} MB")
        self.__algorithm_running = False
            
    def mapa_de_calor(self):
        frecuencias = {}
        # Paso 2: Abrir y procesar el archivo CSV
        with open('ordenes.csv', 'r') as archivo:
            # Paso 3: Iterar sobre cada línea del archivo
            for linea in archivo:
                # Paso 4: Dividir la línea por comas para obtener las estanterías
                estanterias = linea.strip().split(',')
                
                # Paso 5: Iterar sobre cada estantería en la línea
                for estanteria in estanterias:
                    # Verificar que el elemento no esté vacío
                    if estanteria.strip():
                        # Paso 6: Incrementar el contador para esta estantería
                        if estanteria in frecuencias:
                            frecuencias[estanteria] += 1
                        else:
                            frecuencias[estanteria] = 1
        for clave, valor in frecuencias.items():
            indice = self.tablero.buscar_por_caracter(clave)
            self.tablero.casilleros[indice].veces_visitado = valor
    
    def llenar_tablero(self):
        # Crear un tablero de 11 filas y 13 columnas
        filas = 11
        columnas = 13

        num_casillero = 0
        # Crear casilleros y agregarlos al tablero
        set1 = 1
        set2 = 9
        set3 = 17
        for _ in range(143):
            i = num_casillero // columnas
            j = num_casillero % columnas
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            if ((j > 1 and j < 4) or (j > 5 and j < 8) or (j > 9 and j < 12)) and (i%5 != 0):
                if (j > 1 and j < 4) and (i<5):
                    casillero = Casillero(x, y, f"{set1}", libre=False)
                    set1 += 1
                elif (j > 5 and j < 8) and (i<5):
                    casillero = Casillero(x, y, f"{set2}", libre=False)
                    set2 += 1
                elif (j > 9 and j < 12) and (i<5):
                    casillero = Casillero(x, y, f"{set3}", libre=False)
                    set3 += 1
                elif (j > 1 and j < 4) and (i>5):
                    casillero = Casillero(x, y, f"{set1+16}", libre=False)
                    set1 += 1
                elif (j > 5 and j < 8) and (i>5):
                    casillero = Casillero(x, y, f"{set2+16}", libre=False)
                    set2 += 1
                elif (j > 9 and j < 12) and (i>5):
                    casillero = Casillero(x, y, f"{set3+16}", libre=False)
                    set3 += 1
            else:
                casillero = Casillero(x, y, "", libre=True)
            self.tablero.agregar_casillero(casillero)
            
            num_casillero += 1