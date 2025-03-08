import pygame
import sys
from constantes import*

class Casillero:
    def __init__(self, x, y, caracter="", libre=True):
        self.x = x
        self.y = y
        self.caracter = caracter
        self.libre = libre
        self.color = None
        self.objetivo = False
        self.inicio = False
        self.recorrido = False
    
    def set_objetivo(self, color):
        self.color = color
        self.objetivo = True

    def set_inicio(self):
        self.color = GREEN
        self.inicio = True
    
    def get_indice(self):
        return (self.y // CELL_SIZE) * CANT_COLUMNAS + (self.x // CELL_SIZE)
    
    def dibujar(self, screen):
        
        # Dibujar el fondo del casillero
        if self.color:
            pygame.draw.rect(screen, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
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
    
    def __str__(self):
        return f"Soy el casillero: {self.get_indice()}"
        
    

class Tablero:
    def __init__(self, ventana, filas, columnas):
        self.ventana = ventana
        self.filas = filas
        self.columnas = columnas
        self.casilleros = []
        self.inicio : Casillero = None
        self.objetivos = []
        
    def get_objetivos(self):
        return self.objetivos
    
    def get_inicio(self):
        return self.inicio
    
    def set_inicio(self, indice):
        self.casilleros[indice].set_inicio()
        self.inicio = self.casilleros[indice]
    
    def set_objetivo(self, indice):
        self.objetivos.append(self.casilleros[indice])
        self.casilleros[indice].set_objetivo(COLORES_OBJETIVOS[len(self.objetivos) % len(COLORES_OBJETIVOS)])
        
    def limpiar_tablero(self):
        self.inicio = None
        self.objetivos = []
        for casillero in self.casilleros:
            self.casilleros[casillero.get_indice()].color = None
            self.casilleros[casillero.get_indice()].inicio = False
            self.casilleros[casillero.get_indice()].objetivo = False

    def agregar_casillero(self, casillero):
        self.casilleros.append(casillero)
        
    def get_casillero_por_elemento(self, fila, columna):
        indice = fila + columna * self.filas
        return self.casilleros[indice]

    def dibujar(self, instrucciones):
        self.ventana.fill(WHITE)
        if instrucciones:
            font = pygame.font.SysFont('arial', 16)
            instructions = [
                "SHIFT + Clic: Colocar inicio",
                "CTRL + Clic: Colocar destino",
                "ESPACIO: Iniciar búsqueda",
                "C: Limpiar camino",
                "ESC: Salir"
            ]
            
            y_offset = 10
            for instruction in instructions:
                text = font.render(instruction, True, (0, 0, 0))
                self.ventana.blit(text, (CELL_SIZE * self.columnas, y_offset))
                y_offset += 20
        
        for casillero in self.casilleros:
            casillero.dibujar(self.ventana)
        pygame.display.flip()
        
    def __str__(self):
        text = ""
        if self.inicio is not None:
            text += f"Mi casillero indice es: {self.inicio.get_indice()} \n y los casilleros objetivos son:\n "
        else:
            text += "No ha marcado el casillero indice\n"
        if len(self.objetivos) != 0:
            for casillero in self.objetivos:
                text += f"--- {casillero.get_indice()}\n"
        else:
            text+= "No ha marcado casilleros objetivos"
        return text