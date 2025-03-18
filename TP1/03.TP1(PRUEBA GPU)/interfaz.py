import pygame
import sys
from constantes import*
import csv
import os

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
        self.veces_visitado = 0
    
    def set_objetivo(self, color):
        self.color = color
        self.objetivo = True

    def set_inicio(self):
        self.color = GREEN
        self.inicio = True
        
    def get_estanteria(self):
        return "casillero libre" if self.libre else "estanteria"
    
    def get_indice(self):
        return (self.y // CELL_SIZE) * CANT_COLUMNAS + (self.x // CELL_SIZE)
    
    def dibujar(self, screen, visitas = False):
        
        rect = pygame.Rect(self.x,self.y,CELL_SIZE,CELL_SIZE)
        # Dibujar el fondo del casillero
        if self.color:
            if self.veces_visitado == 1: # Círculo
                pygame.draw.circle(screen, self.color, rect.center, CELL_SIZE//2 - 2)
            elif self.veces_visitado == 2: # Diamante
                pygame.draw.polygon(screen, self.color, [rect.midtop, rect.midright, rect.midbottom, rect.midleft])
            elif self.veces_visitado == 3:
                pygame.draw.circle(screen, self.color, rect.center, CELL_SIZE//4)
            else:
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
    
    def get_celda_c(self):
        """Devuelve la casilla que tiene caracter=='C', o None si no existe."""
        for cas in self.casilleros:
            if cas.caracter == "C":
                return cas
        return None

    
    def get_inicio(self):
        return self.inicio
    
    def set_inicio(self, indice):
        self.casilleros[indice].set_inicio()
        self.inicio = self.casilleros[indice]
    
    def set_objetivo(self, indice):
        self.objetivos.append(self.casilleros[indice])
        self.casilleros[indice].set_objetivo(COLORES_OBJETIVOS[(len(self.objetivos) - 1) % len(COLORES_OBJETIVOS)])
        
    def limpiar_tablero(self):
        self.inicio = None
        self.objetivos = []
        for casillero in self.casilleros:
            # Si es una estantería y NO es la casilla "C"
            if not casillero.libre and casillero.caracter != "C":
                casillero.caracter = ""   # quitar número anterior
            casillero.color = None
            casillero.inicio = False
            casillero.objetivo = False
            casillero.veces_visitado = 0

        
    def actualizar_tablero(self, casilleros):
        for casillero in casilleros:
            self.casilleros[casillero.get_indice()] = casillero
            
    def get_vecinos(self, indice):
        # Convertir el índice lineal a coordenadas (fila, columna)
        columna = indice % self.columnas
        fila = indice // self.columnas
        
        # Inicializar una lista para almacenar los vecinos
        vecinos = []

        # Verificar y agregar el vecino de arriba
        if fila > 0:
            if self.get_casillero_por_elemento(fila-1,columna).libre or (self.get_casillero_por_elemento(fila-1,columna).objetivo and not self.casilleros[indice].objetivo):
                vecinos.append(self.get_casillero_por_elemento(fila-1,columna))  # Arriba

        # Verificar y agregar el vecino de abajo
        if fila < self.filas - 1:
            if self.get_casillero_por_elemento(fila+1,columna).libre or (self.get_casillero_por_elemento(fila+1,columna).objetivo and not self.casilleros[indice].objetivo):
                vecinos.append(self.get_casillero_por_elemento(fila+1,columna))  # Abajo

        # Verificar y agregar el vecino de la izquierda
        if columna > 0:
            if self.get_casillero_por_elemento(fila,columna-1).libre or (self.get_casillero_por_elemento(fila,columna-1).objetivo and not self.casilleros[indice].objetivo):
                vecinos.append(self.get_casillero_por_elemento(fila,columna-1))  # Izquierda

        # Verificar y agregar el vecino de la derecha
        if columna < self.columnas - 1:
            if self.get_casillero_por_elemento(fila,columna+1).libre or (self.get_casillero_por_elemento(fila,columna+1).objetivo and not self.casilleros[indice].objetivo):
                vecinos.append(self.get_casillero_por_elemento(fila,columna+1))  # Derecha
        return vecinos
        
    def buscar_por_caracter(self,caracter):
        for casillero in self.casilleros:
            if casillero.caracter == caracter:
                return casillero.get_indice()

    def agregar_casillero(self, casillero):
        self.casilleros.append(casillero)
        
    def get_casillero_por_elemento(self, fila, columna):
        indice = fila*self.columnas + columna
        return self.casilleros[indice]

    def limpiar_objetivos_y_colores(self):
        """Borra únicamente los objetivos y los colores, conservando el caracter."""
        self.inicio = None
        self.objetivos = []
        for casillero in self.casilleros:
            casillero.color = None
            casillero.inicio = False
            casillero.objetivo = False
            casillero.veces_visitado = 0
        # Nota: NO reasignamos casillero.caracter = "" 
        # (así mantenemos la asignación del individuo)

    def dibujar(self, instrucciones, visitas = False):
        self.ventana.fill(WHITE)
        if instrucciones:
            font = pygame.font.SysFont('arial', 16)
            instructions = [
                "SHIFT + Clic: Colocar inicio",
                "CTRL + Clic: Colocar destino",
                "ESPACIO: Iniciar búsqueda",
                "C: Limpiar camino",
                "ESC: Salir",
                "M: Desplegar Menú archivo csv"
            ]
            
            y_offset = 10
            for instruction in instructions:
                text = font.render(instruction, True, (0, 0, 0))
                self.ventana.blit(text, (CELL_SIZE * self.columnas, y_offset))
                y_offset += 20
        
        for casillero in self.casilleros:
            casillero.dibujar(self.ventana, visitas)
        pygame.display.flip()

    # Dentro de la clase Tablero en interfaz.py
    def asignar_configuracion(self, configuracion):
        idx = 0
        count_shelves = 0
        for casillero in self.casilleros:
            # Supongamos que la condición es if not casillero.libre and casillero.caracter != "C":
            if not casillero.libre and casillero.caracter != "C":
                count_shelves += 1
                casillero.caracter = str(configuracion[idx])
                idx += 1
                if idx >= len(configuracion):
                    break
        #print("Se han asignado productos a", count_shelves, "estanterías.")

        
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
    
class MenuSelector:
    def __init__(self, archivo, ventana):
        self.archivo = archivo
        self.ventana = ventana
        self.font_size = 24
        self.font = pygame.font.SysFont(None, self.font_size)
        
        
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

    def draw_menu(self, data, selected_index):
        """Dibuja el menú con las opciones del CSV y resalta la opción seleccionada."""
        self.ventana.fill(WHITE)
        
        # Título
        title = self.font.render("Selecciona una línea del CSV", True, BLACK)
        self.ventana.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Calcular posición y tamaño del área de visualización
        menu_top = 80
        menu_height = WINDOW_HEIGHT - menu_top - 50
        
        # Determinar cuántas líneas caben en la pantalla
        lines_per_screen = menu_height // (self.font_size + 10)
        
        # Calcular el índice de inicio para desplazamiento
        start_index = max(0, selected_index - lines_per_screen // 2)
        end_index = min(len(data), start_index + lines_per_screen)
        
        # Dibujar indicador de desplazamiento
        if start_index > 0:
            pygame.draw.polygon(self.ventana, BLACK, [(WINDOW_WIDTH // 2, menu_top - 15), 
                                            (WINDOW_WIDTH // 2 - 10, menu_top - 5), 
                                            (WINDOW_WIDTH // 2 + 10, menu_top - 5)])
        
        if end_index < len(data):
            pygame.draw.polygon(self.ventana, BLACK, [(WINDOW_WIDTH // 2, menu_top + menu_height + 15), 
                                            (WINDOW_WIDTH // 2 - 10, menu_top + menu_height + 5), 
                                            (WINDOW_WIDTH // 2 + 10, menu_top + menu_height + 5)])
        
        # Dibujar cada línea
        y_pos = menu_top
        for i in range(start_index, end_index):
            # Convertir la línea a texto
            line_text = ", ".join(data[i])
            
            # Truncar el texto si es demasiado largo
            if self.font.size(line_text)[0] > WINDOW_WIDTH - 60:
                # Encontrar cuántos caracteres caben
                chars_fit = 0
                while chars_fit < len(line_text) and self.font.size(line_text[:chars_fit] + "...")[0] < WINDOW_WIDTH - 60:
                    chars_fit += 1
                line_text = line_text[:chars_fit-3] + "..."
            
            text = self.font.render(line_text, True, BLACK)
            
            # Dibujar rectángulo para la opción seleccionada
            text_rect = pygame.Rect(40, y_pos - 5, WINDOW_WIDTH - 80, self.font_size + 10)
            
            if i == selected_index:
                # Borde para la opción seleccionada
                pygame.draw.rect(self.ventana, BLUE, text_rect, 2)
                # Fondo más claro para la opción seleccionada
                pygame.draw.rect(self.ventana, (220, 220, 255), text_rect.inflate(-2, -2))
            
            self.ventana.blit(text, (50, y_pos))
            y_pos += self.font_size + 10
        
        # Instrucciones en la parte inferior
        instructions = self.font.render("↑/↓: Navegar | Enter: Seleccionar | Esc: Salir", True, BLACK)
        self.ventana.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, WINDOW_HEIGHT - 40))
        
        pygame.display.flip()

    def main(self):
        # Comprobar si el archivo existe
        if not os.path.exists(self.archivo):
            print(f"No existe el archivo '{self.archivo}'...")
            return
            
        
        # Cargar datos del CSV
        data = self.load_csv_data()
        
        if not data:
            print("No hay datos para mostrar. Saliendo...")
            pygame.quit()
            sys.exit()
        
        selected_index = 0
        running = True
        
        while running:
            self.draw_menu(data, selected_index)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if event.key == pygame.K_UP:
                        selected_index = max(0, selected_index - 1)
                    
                    if event.key == pygame.K_DOWN:
                        selected_index = min(len(data) - 1, selected_index + 1)
                    
                    if event.key == pygame.K_RETURN:
                        # Devolver la línea seleccionada y terminar
                        print("Línea seleccionada:", data[selected_index])
                        return data[selected_index]
        
        pygame.quit()
        return None