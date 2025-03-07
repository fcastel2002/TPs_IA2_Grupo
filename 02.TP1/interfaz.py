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

class Tablero:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.casilleros = []

    def agregar_casillero(self, casillero):
        self.casilleros.append(casillero)

    def dibujar(self, screen, instrucciones):
        screen.fill(WHITE)
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
                screen.blit(text, (CELL_SIZE * self.columnas, y_offset))
                y_offset += 20
        
        for casillero in self.casilleros:
            casillero.dibujar(screen)
        pygame.display.flip()