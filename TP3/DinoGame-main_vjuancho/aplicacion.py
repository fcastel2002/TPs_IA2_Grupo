import random
import pygame
import subprocess
import os
from Dinosaur import Dinosaur
from Cloud import Cloud
from Bird import Bird
from SmallCactus import SmallCactus
from LargeCactus import LargeCactus
from Genetic import updateNetwork
from ImageCapture import ImageCapture
from Genetic import updateNetwork, initialize_population_with_saved_genomes
from constantes import *
from GenomeManager import GenomeManager
from interfaz import InterfazInteractiva as Interfaz
from interfaz import MenuSelector

class Videojuego:
    def __init__(self):

        pygame.init()
        self.SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Game")
        self.SCREEN.fill(FONDO_BLANCO)
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        
        self.interfaz = Interfaz(self.SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, font_size=30)
        self.generaciones = 0
        self.bestScore = 0
        self.playMode = "X"
        
        self.imageCapture = ImageCapture(SCREEN_SPAWN_POSITION)
        self.BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))
        
        self.population_number = 1000
        
        self.population = self.generar_poblacion(self.population_number)
        
            # Colores personalizados (opcional)
        custom_colors = {
            'background': (25, 25, 35),
            'text': (255, 255, 255),
            'selected': (100, 200, 100),
            'selected_bg': (40, 80, 40),
            'border': (120, 120, 120)
        }
        
        # Crear el selector de menú
        menu = MenuSelector(
            window_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            colors=custom_colors,  # Opcional, usa colores por defecto si no se especifica
            folder_name="datos_buenas_poblaciones"
        )
        
        # Ejecutar el selector
        selected_file = menu.select_file()
        
        
        if self.playMode != 'm' and self.playMode != 'c' and self.playMode != 'a':
            self.generaciones = initialize_population_with_saved_genomes(self.population, selected_file)
        self.player = Dinosaur(0)
        self.callUpdateNetwork = False
        self.run = True
        
        
        self.genome_manger = GenomeManager()
        self.interfaz.mostrar_stats_manager(self.genome_manger.get_stats())
        
        

    def generar_poblacion(self, population_number):
        population = []
        for i in range(population_number):
            while True:
                R = random.randint(0, 255)
                G = random.randint(0, 255)
                B = random.randint(0, 255)
                brightness = 0.299 * R + 0.587 * G + 0.114 * B
                if brightness < 180:  # Evitar colores demasiado claros
                    break
            color = (R, G, B)
            population.append(Dinosaur(i, color, True))
        return population
    
    def correr_videojuego(self):

        # Manejar selección del menú
        opcion = self.interfaz.seleccionar_opcion()
        
        while self.run:
            if self.playMode == 'm' or self.playMode == 'c' or self.playMode == 'a':
                self.player.resetStatus()
            elif self.playMode != 'm' and self.playMode != 'c' and self.playMode != 'a' and self.callUpdateNetwork:
                updateNetwork(self.population, self.generaciones)
            
            
            if opcion == 'quit':
                self.run = False
                break
            elif opcion is not None:
                if self.generaciones == 1:
                    self.playMode = opcion
                    if self.playMode == 'm' or self.playMode == 'c' or self.playMode == 'a':
                        self.population = []
                
                # Iniciar el juego
                self.gameScreen()
                # break
            
    def gameScreen(self):
        self.clock = pygame.time.Clock()
        self.game_speed = 20
        self.cloud = Cloud(SCREEN_WIDTH, self.game_speed)
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.points = 0
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.obstacles = []
        self.callUpdateNetwork = True
        
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            self.SCREEN.fill((255, 255, 255))

            if self.playMode == 'm' or self.playMode == 'c':
                userInput = pygame.key.get_pressed()
                self.player.draw(self.SCREEN)
                self.player.update(userInput)
                if self.playMode == 'c':
                    self.imageCapture.capture(userInput)

            elif self.playMode == 'a':
                if self.player.alive:
                    self.player.draw(self.SCREEN)
                    self.imageCapture.capture_live()
                    self.player.predict()

            else:
                for dino in self.population:
                    if dino.alive:
                        dino.draw(self.SCREEN)
                    
                    for obstacle in self.obstacles:
                        obstacle_params = obstacle.rect
                        dino_params = dino.dino_rect
                        # ========================== ACTUALIZAR LA FUNCIÓN 'think' CON LOS PARÁMETROS DE ENTRADA DE LA RED ===================
                        dino.update(dino.think(self.obstacles, self.game_speed))
                        # ====================================================================================================================

            if len(self.obstacles) == 0:
                if random.randint(0, 2) == 0:
                    self.obstacles.append(SmallCactus(SCREEN_WIDTH, self.game_speed, self.obstacles))
                elif random.randint(0, 2) == 1:
                    self.obstacles.append(LargeCactus(SCREEN_WIDTH, self.game_speed, self.obstacles))
                elif random.randint(0, 2) == 2:
                    self.obstacles.append(Bird(SCREEN_WIDTH, self.game_speed, self.obstacles))
            

            for obstacle in self.obstacles:
                obstacle.draw(self.SCREEN)
                obstacle.update()
                obstacle_params = obstacle.rect

                if self.playMode == 'm' or self.playMode == 'c' or self.playMode == 'a':
                    if self.player.dino_rect.colliderect(obstacle_params):
                        self.player.alive = False
                        
                else:
                    for dino in self.population:
                        dino_params = dino.dino_rect
                        if dino.alive and dino_params.colliderect(obstacle_params):
                            
                            if self.points > dino.score:
                                dino.score = self.points
                            dino.alive = False

                            if (self.count_alive(self.population) == 0):
                                last_dino = dino

            if ((self.playMode == 'm' or self.playMode == 'c' or self.playMode == 'a') and self.player.alive == False):
                self.deathUpdates(self.player, obstacle)
                return
            elif (self.playMode != 'm' and self.playMode != 'c' and self.playMode != 'a' and self.count_alive(self.population) == 0):
                self.countSurviving()
                self.currentGeneration()
                self.getBestScore()
                self.deathUpdates(last_dino, obstacle)
                return

            self.background()

            self.cloud.draw(self.SCREEN)
            self.cloud.update()

            self.score()

            if (self.playMode != 'm' and self.playMode != 'c' and self.playMode != 'a'):
                self.countSurviving()
                self.currentGeneration()
                self.getBestScore()

            
            self.clock.tick(30)
            pygame.display.update()
        
    def score(self):
        self.points += 1
        if self.points % 100 == 0:
            self.game_speed += 1

        self.mostrar_datos("Puntos: " + str(self.points), 100, 40)
        
    def countSurviving(self):
        self.mostrar_datos("Vivos: " + str(self.count_alive(self.population)), 1000, 65)

    def currentGeneration(self):
        self.mostrar_datos("Generación: " + str(self.generaciones), 1000, 90)
        
    def getBestScore(self):
        self.mostrar_datos("Mejor puntuación: " + str(self.bestScore), 1000 - 20, 115)
        
    def mostrar_datos(self, texto, pos_x, pos_y):
        text = self.font.render(texto, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (pos_x, pos_y)
        self.SCREEN.blit(text, textRect)

    def background(self):
        image_width = self.BG.get_width()
        self.SCREEN.blit(self.BG, (self.x_pos_bg, self.y_pos_bg))
        self.SCREEN.blit(self.BG, (image_width + self.x_pos_bg, self.y_pos_bg))
        if self.x_pos_bg <= -image_width:
            self.SCREEN.blit(self.BG, (image_width + self.x_pos_bg, self.y_pos_bg))
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed

    def deathUpdates(self, player, obstacle):
        obstacle_params = obstacle.rect
        self.SCREEN.fill((255, 255, 255))
        self.background()
        self.score()
        self.cloud.draw(self.SCREEN)
        self.cloud.update()
        self.SCREEN.blit(player.image, (player.dino_rect.x, player.dino_rect.y))
        self.SCREEN.blit(obstacle.image[obstacle.type], (obstacle_params.x, obstacle_params.y))
        pygame.draw.rect(self.SCREEN, (255, 0, 0), player.dino_rect, 2)
        pygame.draw.rect(self.SCREEN, (0, 0, 255), obstacle_params, 2)
        pygame.display.update()
        pygame.time.delay(1000)
        self.generaciones += 1
        if self.points > self.bestScore:
            self.bestScore = self.points
            
    def count_alive(self, population):
        alive = 0
        for dino in population:
            if dino.alive:
                alive += 1
        return alive