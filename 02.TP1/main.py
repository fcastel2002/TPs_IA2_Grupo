import pygame
import sys

# Definir colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Definir tamaño de la ventana y de los casilleros
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 50

class Casillero:
    def __init__(self, x, y, caracter="", libre=True):
        self.x = x
        self.y = y
        self.caracter = caracter
        self.libre = libre

    def dibujar(self, screen):
        # Dibujar el borde del casillero
        if self.libre:
            pygame.draw.rect(screen, pygame.Color('gray70'), (self.x, self.y, CELL_SIZE, CELL_SIZE), 1)
        else:
            pygame.draw.rect(screen, pygame.Color('gray8'), (self.x, self.y, CELL_SIZE, CELL_SIZE), 2)

        # Dibujar el caracter centrado
        font = pygame.font.Font(None, 36)
        text = font.render(self.caracter, True, BLACK)
        text_rect = text.get_rect(center=(self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2))
        screen.blit(text, text_rect)

class Tablero:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.casilleros = []

    def agregar_casillero(self, casillero):
        self.casilleros.append(casillero)

    def dibujar(self, screen):
        screen.fill(WHITE)
        for casillero in self.casilleros:
            casillero.dibujar(screen)
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tablero con Pygame")

    # Crear un tablero de 11 filas y 13 columnas
    filas = 11
    columnas = 13
    tablero = Tablero(filas, columnas)

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
        tablero.agregar_casillero(casillero)
        
        num_casillero += 1
                
                
    # for i in range(filas):
    #     for j in range(columnas):
    #         x = j * CELL_SIZE
    #         y = i * CELL_SIZE
            
    #         if ((j > 1 and j < 4) or (j > 5 and j < 8) or (j > 9 and j < 12)) and (i%5 != 0):
    #             num_casillero += 1
    #             casillero = Casillero(x, y, f"{num_casillero}", libre=False)
    #         else:
    #             casillero = Casillero(x, y, "", libre=True)
                
    #         tablero.agregar_casillero(casillero)

    # Bucle principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        tablero.dibujar(screen)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()