import pygame
import sys
from grilla import Grid
from a_estrella import AStar

class Game:
    def __init__(self, cell_size: int = 50):
        pygame.init()
        self.rows = 11
        self.cols = 13
        self.cell_size = cell_size
        self.grid = Grid(self.rows, self.cols, self.cell_size)
        self.width = self.grid.width
        self.height = self.grid.height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulador de Montacargas - A* con 2 agentes")
        
        # Instancias separadas del A*
        self.a_star1 = AStar(self.grid)
        self.a_star2 = AStar(self.grid)

        self.is_running = True
        self.algorithm_running = False
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Montacargas
        self.montacargas1 = {'pos': None, 'dest': None, 'color': (255, 0, 0)}
        self.montacargas2 = {'pos': None, 'dest': None, 'color': (0, 0, 255)}

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_SPACE and not self.algorithm_running:
                    self.start_simulation()
                elif event.key == pygame.K_c:
                    self.grid.reset_path()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // self.cell_size, pos[0] // self.cell_size
                keys = pygame.key.get_mods()
                cell = self.grid.get_cell(row, col)
                
                if cell:
                    if event.button == 1:  # Clic izquierdo
                        if keys & pygame.KMOD_SHIFT:
                            self.montacargas1['pos'] = (row, col)
                            cell.color = (255, 0, 0)  # Rojo
                        elif keys & pygame.KMOD_CTRL:
                            self.montacargas1['dest'] = (row, col)
                            cell.color = (255, 255, 0)  # Amarillo
                    elif event.button == 3:  # Clic derecho
                        if keys & pygame.KMOD_SHIFT:
                            self.montacargas2['pos'] = (row, col)
                            cell.color = (0, 255, 255)  # Cian
                        elif keys & pygame.KMOD_CTRL:
                            self.montacargas2['dest'] = (row, col)
                            cell.color = (255, 105, 180)  # Rosa para diferenciar M2

    def start_simulation(self):
        if not self.montacargas1['pos'] or not self.montacargas1['dest']:
            print("Error: Montacargas 1 no tiene inicio o destino")
            return
        if not self.montacargas2['pos'] or not self.montacargas2['dest']:
            print("Error: Montacargas 2 no tiene inicio o destino")
            return

        self.algorithm_running = True
        
        # Configurar inicio y destino en la grilla
        self.grid.set_start(*self.montacargas1['pos'])
        self.grid.set_end(*self.montacargas1['dest'])
        self.a_star1.occupied_positions = set()

        success1, path1 = self.a_star1.run(self.draw)
        if not success1:
            print("No se encontró ruta para Montacargas 1")
            self.algorithm_running = False
            return

        # Mostrar la ruta de M1 en azul
        for pos in path1:
            self.grid.get_cell(*pos).color = (0, 0, 255)
            self.draw()
            pygame.time.delay(300)

        self.grid.set_start(*self.montacargas2['pos'])
        self.grid.set_end(*self.montacargas2['dest'])
        self.a_star2.occupied_positions = set(path1)  # M2 evita la ruta de M1

        success2, path2 = self.a_star2.run(self.draw)
        if not success2:
            print("No se encontró ruta para Montacargas 2")
            self.algorithm_running = False
            return

        # Mostrar la ruta de M2 en rosa
        for pos in path2:
            self.grid.get_cell(*pos).color = (255, 105, 180)
            self.draw()
            pygame.time.delay(300)

        self.algorithm_running = False
    
    def draw(self):
        self.grid.draw(self.window)
        
        # Mostrar instrucciones en la pantalla
        font = pygame.font.SysFont('arial', 16)
        instructions = [
            "SHIFT + Clic izquierdo: Inicio Montacargas 1",
            "CTRL + Clic izquierdo: Destino Montacargas 1",
            "SHIFT + Clic derecho: Inicio Montacargas 2",
            "CTRL + Clic derecho: Destino Montacargas 2",
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

    def run(self):
        while self.is_running:
            self.clock.tick(self.fps)
            self.handle_events()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
