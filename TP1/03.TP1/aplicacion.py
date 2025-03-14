from interfaz import Tablero, MenuSelector, Casillero, pygame, sys
from constantes import*
from agente import Agente
import sys

class Aplicacion:
    def __init__(self, tablero):
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
        self.menu : MenuSelector = MenuSelector('ordenes.csv',self.__screen)
        
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
                    self.__algorithm_running = True
                    self.__agente : Agente = Agente(self.tablero)
                    self.__agente.encontrar_ruta() 
                    self.__algorithm_running = False
                
                # Limpiar camino con la tecla C
                elif event.key == pygame.K_c:
                    self.tablero.limpiar_tablero()
                elif event.key == pygame.K_b:
                    print(self.tablero)
                elif event.key == pygame.K_m:
                    objetivos = self.menu.main()
                    for objetivo in objetivos:
                        indice = self.tablero.buscar_por_caracter(objetivo)
                        self.tablero.set_objetivo(int(indice))
            
            # Eventos de ratón
            if not self.__algorithm_running:
                # Colocar inicio/fin con el ratón
                if pygame.mouse.get_pressed()[0]:  # Botón izquierdo
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // CELL_SIZE, pos[0] // CELL_SIZE
                    indice = col + row * self.__columnas
                    print(f"Los vecinos son:")
                    for vecino in self.tablero.get_vecinos(self.tablero.casilleros[indice].get_indice()):
                        print(vecino)
                    # Shift + clic izquierdo para colocar punto de inicio
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.tablero.set_inicio(indice)
                        
                    # Ctrl + clic izquierdo para colocar punto de destino
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.tablero.set_objetivo(indice)
        
            
    def llenar_tablero(self):
        # Crear un tablero de 11 filas y 13 columnas
        filas = 11
        columnas = 13

        num_casillero = 0
        
        # Iterar sobre las 143 celdas (11 * 13)
        for _ in range(143):
            i = num_casillero // columnas
            j = num_casillero % columnas
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            
            # 1) Si es la celda "C" (punto de carga)
            if i == 5 and j == 0:
                casillero = Casillero(x, y, "C", libre=True)
            
            # 2) Si corresponde a una estantería
            elif ((j > 1 and j < 4) or (j > 5 and j < 8) or (j > 9 and j < 12)) and (i % 5 != 0):
                # En lugar de asignar un número por defecto, ponemos "" y libre=False
                casillero = Casillero(x, y, "", libre=False)
            
            # 3) Si es un pasillo o celda libre
            else:
                casillero = Casillero(x, y, "", libre=True)
            
            self.tablero.agregar_casillero(casillero)
            num_casillero += 1
