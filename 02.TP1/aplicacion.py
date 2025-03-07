from interfaz import Tablero, Casillero, pygame, sys
from constantes import*
import sys

class Aplicacion:
    def __init__(self, tablero):
        self.__filas = tablero['filas']
        self.__columnas = tablero['columnas']
        self.__tablero : Tablero = Tablero(tablero['filas'],tablero['columnas'])
        self.__running = False
        self.__algorithm_running = False
        self.__inicio = False
        self.__cantidad_objetivos = 0
        # Inicialización 
        self.llenar_tablero()
        pygame.init()
        self.__screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tablero con Pygame")
        
    def run(self):
        # Bucle principal
        self.__running = True
        while self.__running:
            self.manejar_eventos()
            self.__tablero.dibujar(self.__screen, not self.__algorithm_running)
        pygame.quit()
        sys.exit()
        
    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            
            # Eventos de teclado
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                # Iniciar algoritmo con la tecla ESPACIO
                elif event.key == pygame.K_SPACE and not self.algorithm_running:
                    self.algorithm_running = True
                    self.a_star.run(self.draw)
                    self.__algorithm_running = False
                
                # Limpiar camino con la tecla C
                elif event.key == pygame.K_c:
                    for casillero in self.__tablero.casilleros:
                        casillero.color = None
                        self.__inicio = False
                        self.__cantidad_objetivos = 0
            
            # Eventos de ratón
            if not self.__algorithm_running:
                # Colocar inicio/fin con el ratón
                if pygame.mouse.get_pressed()[0]:  # Botón izquierdo
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // CELL_SIZE, pos[0] // CELL_SIZE
                    indice = col + row * self.__columnas
                    # Shift + clic izquierdo para colocar punto de inicio
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if not self.__inicio:
                            self.__tablero.casilleros[indice].color = GREEN
                            self.__inicio = True
                        
                    # Ctrl + clic izquierdo para colocar punto de destino
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.__tablero.casilleros[indice].color = COLORES_OBJETIVOS[self.__cantidad_objetivos % len(COLORES_OBJETIVOS)]
                        self.__cantidad_objetivos += 1
        
            
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
            self.__tablero.agregar_casillero(casillero)
            
            num_casillero += 1