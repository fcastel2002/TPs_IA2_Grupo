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

    def show_message(self, message):
        font = pygame.font.SysFont('arial', 24)
        text = font.render(message, True, (0, 0, 0))
        self.window.blit(text, (10, 10))
        pygame.display.update()
        pygame.time.delay(2000)

    def start_simulation(self):
        if not self.montacargas1['pos'] or not self.montacargas1['dest']:
            print("Error: Montacargas 1 no tiene inicio o destino")
            return
        if not self.montacargas2['pos'] or not self.montacargas2['dest']:
            print("Error: Montacargas 2 no tiene inicio o destino")
            return

        self.algorithm_running = True
        
        self.grid.set_start(*self.montacargas1['pos'])
        self.grid.set_end(*self.montacargas1['dest'])
        self.a_star1.occupied_positions = {self.montacargas2['pos']}

        success1, path1 = self.a_star1.run(self.draw)
        if success1:
            print("Ruta M1 encontrada")
            self.show_message("Ruta M1 encontrada")
        else:
            print("No se encontró ruta para Montacargas 1")
            self.algorithm_running = False
            return

        self.grid.set_start(*self.montacargas2['pos'])
        self.grid.set_end(*self.montacargas2['dest'])
        self.a_star2.occupied_positions = set(path1) | {self.montacargas1['dest']}

        success2, path2 = self.a_star2.run(self.draw)
        if success2:
            print("Ruta M2 encontrada")
            self.show_message("Ruta M2 encontrada")
        else:
            print("M2 no encontró ruta, intentando recalcular...")
            self.a_star2.occupied_positions = set(path1)
            success2, path2 = self.a_star2.run(self.draw)
            if success2:
                print("Ruta M2 encontrada después de recalcular")
                self.show_message("Ruta M2 encontrada después de recalcular")
            else:
                print("No se encontró ruta para Montacargas 2")
                self.algorithm_running = False
                return

        occupied_positions = {self.montacargas2['pos']}
        for step in range(max(len(path1), len(path2))):
            if step < len(path1):
                self.montacargas1['pos'] = path1[step]
                occupied_positions.add(path1[step])
                self.grid.get_cell(*path1[step]).color = (0, 0, 255)
                self.draw()
                pygame.time.delay(300)

            if step < len(path2):
                if path2[step] in occupied_positions:
                    print(f"Colisión detectada en {path2[step]}, recalculando ruta de M2")
                    self.a_star2.occupied_positions = occupied_positions
                    for _ in range(3):
                        success2, path2 = self.a_star2.run(self.draw)
                        if success2:
                            print("Ruta M2 encontrada tras colisión")
                            self.show_message("Ruta M2 encontrada tras colisión")
                            break
                    if not success2:
                        print("M2 no puede encontrar nueva ruta")
                        return
                self.montacargas2['pos'] = path2[step]
                occupied_positions.add(path2[step])
                self.grid.get_cell(*path2[step]).color = (255, 105, 180)
                self.draw()
                pygame.time.delay(300)

        self.show_message("Montacargas 1 y 2 han llegado a su destino")
        self.algorithm_running = False

    def draw(self):
        self.grid.draw(self.window)
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
