import pygame
import sys
from grilla import Grid
from a_estrella import AStar

class Game:
    """Controla el flujo del juego y la visualización."""
    
    def __init__(self, cell_size: int = 50):
        # Inicializar pygame
        pygame.init()
        
        # Definir dimensiones de la cuadrícula
        self.rows = 11
        self.cols = 13
        self.cell_size = cell_size
        
        # Crear la cuadrícula
        self.grid = Grid(self.rows, self.cols, self.cell_size)
        
        # Crear la ventana con el tamaño exacto de la cuadrícula
        self.width = self.grid.width
        self.height = self.grid.height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulador de Montacargas - Algoritmo A*")
        
        # Algoritmo A*
        self.a_star = AStar(self.grid)
        
        # Estado del juego
        self.is_running = True
        self.algorithm_running = False
        
        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()
        self.fps = 60
    
    def handle_events(self) -> None:
        """Maneja los eventos de entrada del usuario."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            # Eventos de teclado
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                # Iniciar algoritmo con la tecla ESPACIO
                elif event.key == pygame.K_SPACE and not self.algorithm_running:
                    self.algorithm_running = True
                    self.a_star.run(self.draw)
                    self.algorithm_running = False
                
                # Limpiar camino con la tecla C
                elif event.key == pygame.K_c:
                    self.grid.reset_path()
            
            # Eventos de ratón
            if not self.algorithm_running:
                # Colocar inicio/fin con el ratón
                if pygame.mouse.get_pressed()[0]:  # Botón izquierdo
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // self.cell_size, pos[0] // self.cell_size
                    
                    # Shift + clic izquierdo para colocar punto de inicio
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.grid.set_start(row, col)
                    # Ctrl + clic izquierdo para colocar punto de destino
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.grid.set_end(row, col)
    
    def run(self) -> None:
        """Ejecuta el bucle principal del juego."""
        while self.is_running:
            self.clock.tick(self.fps)
            self.handle_events()
            self.draw()
        
        pygame.quit()
        sys.exit()
    
    def draw(self) -> None:
        """Actualiza la pantalla."""
        self.grid.draw(self.window)
        
        # Mostrar instrucciones en la pantalla
        if not self.algorithm_running:
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
                self.window.blit(text, (10, y_offset))
                y_offset += 20
        
        pygame.display.update()


# Ejecutar el juego
if __name__ == "__main__":
    # Puedes ajustar el tamaño de las celdas según necesites
    CELL_SIZE = 50
    game = Game(cell_size=CELL_SIZE)
    game.run()