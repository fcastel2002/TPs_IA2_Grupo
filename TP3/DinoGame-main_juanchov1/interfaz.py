
import pygame
import sys
import os
import json
from constantes import*

class InterfazInteractiva:
    def __init__(self, screen, screen_width, screen_height, font_size=30, bg_color=pygame.Color('DarkSlateGray1'), 
                 text_color=(0, 0, 0), selected_color=(100, 150, 255), selected_text_color=(255, 255, 255)):
        """
        Inicializa el menú interactivo
        
        Args:
            screen: Superficie de pygame donde se dibujará el menú
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
            font_size: Tamaño de la fuente
            bg_color: Color de fondo (R, G, B)
            text_color: Color del texto normal
            selected_color: Color de fondo de la opción seleccionada
            selected_text_color: Color del texto de la opción seleccionada
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = bg_color
        self.text_color = text_color
        self.selected_color = selected_color
        self.selected_text_color = selected_text_color
        
        # Inicializar fuente
        pygame.font.init()
        self.font = pygame.font.Font('freesansbold.ttf', font_size)
        
        # Opciones del menú con sus respectivos caracteres de retorno
        self.opciones = [
            ("Jugar manualmente", 'm'),
            ("Capturar Imagenes", 'c'),
            ("Usar el modelo generado por Tensorflow", 'a'),
            ("Algoritmo Genético", 'x'),
            ("Cargar Genoma", 'l')
        ]
        
        self.opcion_seleccionada = 0  # Índice de la opción seleccionada
        self.espaciado = 60  # Espacio entre opciones
        
    def actualizar_opciones(self, nuevas_opciones):
        """
        Permite actualizar las opciones del menú
        
        Args:
            nuevas_opciones: Lista de tuplas (texto, caracter_retorno)
        """
        self.opciones = nuevas_opciones
        self.opcion_seleccionada = 0  # Resetear selección
        
    def manejar_eventos(self, eventos):
        """
        Maneja los eventos de teclado para navegar por el menú
        
        Args:
            eventos: Lista de eventos de pygame
            
        Returns:
            str o None: Caracter de la opción seleccionada si se presiona ENTER, None en caso contrario
        """
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    # Navegar hacia arriba
                    self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
                elif evento.key == pygame.K_DOWN:
                    # Navegar hacia abajo
                    self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    # Seleccionar opción actual
                    return self.opciones[self.opcion_seleccionada][1]
        return None
    
    def dibujar(self):
        """
        Dibuja el menú en la pantalla
        """
        # Limpiar pantalla con color de fondo
        self.screen.fill(self.bg_color)
        
        # Calcular posición inicial centrada verticalmente
        total_height = len(self.opciones) * self.espaciado
        start_y = (self.screen_height - total_height) // 2
        
        for i, (texto, _) in enumerate(self.opciones):
            # Renderizar texto
            if i == self.opcion_seleccionada:
                # Opción seleccionada
                texto_surface = self.font.render(texto, True, self.selected_text_color)
            else:
                # Opción normal
                texto_surface = self.font.render(texto, True, self.text_color)
            
            # Calcular posición centrada horizontalmente
            texto_rect = texto_surface.get_rect()
            texto_rect.centerx = self.screen_width // 2
            texto_rect.y = start_y + (i * self.espaciado)
            
            # Dibujar fondo de selección si es la opción actual
            if i == self.opcion_seleccionada:
                # Crear rectángulo de fondo más amplio que el texto
                fondo_rect = texto_rect.copy()
                fondo_rect.inflate_ip(20, 10)  # Agregar padding
                pygame.draw.rect(self.screen, self.selected_color, fondo_rect)
            
            # Dibujar texto
            self.screen.blit(texto_surface, texto_rect)
        
        # Agregar instrucciones en la parte inferior
        instrucciones = "↑/↓: Navegar | Enter: Seleccionar"
        inst_surface = pygame.font.Font('freesansbold.ttf', 16).render(instrucciones, True, (128, 128, 128))
        inst_rect = inst_surface.get_rect()
        inst_rect.centerx = self.screen_width // 2
        inst_rect.y = self.screen_height - 50
        self.screen.blit(inst_surface, inst_rect)
    
    def seleccionar_opcion(self):
        """
        Método principal para manejar la selección de opciones.
        Debe ser llamado en un bucle hasta que retorne un valor válido.
        
        Returns:
            str o None: Caracter de la opción seleccionada, None si no se ha seleccionado nada
        """
        clock = pygame.time.Clock()
        while True:
            # Obtener eventos
            eventos = pygame.event.get()
            
            # Manejar eventos de cierre de ventana
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    return 'quit'
            
            # Manejar navegación y selección
            resultado = self.manejar_eventos(eventos)
            
            # Dibujar menú
            self.dibujar()
            
            if resultado is not None:
                break
            # Actualizar pantalla
            pygame.display.update()
            clock.tick(60)  # 60 FPS    
            
        return resultado

    def mostrar_stats_manager(self, stats):
        print("\n🧬 ESTADO DE LA EVOLUCIÓN 🧬")
        print(f"Mejor score histórico: {stats.get('best_score_ever', 0)}")
        print(f"Generaciones completadas: {stats.get('total_generations', 0)}")
        print(f"Individuos de élite: {stats.get('elite_count', 0)}")
        print("=" * 40)
        
        

class MenuSelector:
    def __init__(self, window_size=(800, 600), colors=None, folder_name="datos_buenas_poblaciones"):
        """
        Inicializa el selector de menú para archivos JSON.
        
        Args:
            window_size (tuple): Dimensiones de la ventana (ancho, alto)
            colors (dict): Diccionario con colores personalizados
            folder_name (str): Nombre de la carpeta que contiene los archivos JSON
        """
        pygame.init()
        
        self.window_size = window_size
        self.folder_name = folder_name
        
        # Colores por defecto
        default_colors = {
            'background': (30, 30, 40),
            'text': (255, 255, 255),
            'selected': (100, 150, 255),
            'selected_bg': (50, 80, 120),
            'border': (150, 150, 150)
        }
        
        self.colors = colors if colors else default_colors
        
        # Configuración de pygame
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Selector de Genomas - Dinosaur Game AI")
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 48)
        self.font_option = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Variables del menú
        self.selected_index = 0
        self.json_files = []
        self.clock = pygame.time.Clock()
        
        # Cargar archivos JSON
        self._load_json_files()
    
    def _load_json_files(self):
        """Carga la lista de archivos JSON desde la carpeta especificada."""
        try:
            if os.path.exists(self.folder_name):
                all_files = os.listdir(self.folder_name)
                self.json_files = [f for f in all_files if f.endswith('.json')]
                self.json_files.sort()  # Ordenar alfabéticamente
                
                if not self.json_files:
                    print(f"No se encontraron archivos .json en la carpeta '{self.folder_name}'")
                    sys.exit(1)
            else:
                print(f"La carpeta '{self.folder_name}' no existe")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error al cargar archivos: {e}")
            sys.exit(1)
    
    def _handle_events(self):
        """Maneja los eventos de pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.json_files)
                
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.json_files)
                
                elif event.key == pygame.K_RETURN:
                    return "select"
                
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
        
        return None
    
    def _draw_menu(self):
        """Dibuja el menú en pantalla."""
        self.screen.fill(self.colors['background'])
        
        # Título
        title_text = self.font_title.render("Selector de Genomas", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(self.window_size[0] // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_small.render(f"Carpeta: {self.folder_name}", True, self.colors['text'])
        subtitle_rect = subtitle_text.get_rect(center=(self.window_size[0] // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instrucciones
        instructions = [
            "↑↓ para navegar",
            "ENTER para seleccionar",
            "ESC para salir"
        ]
        
        y_offset = 150
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, self.colors['border'])
            inst_rect = inst_text.get_rect(center=(self.window_size[0] // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 25
        
        # Lista de archivos
        start_y = 250
        visible_items = min(15, len(self.json_files))  # Máximo 15 items visibles
        
        # Calcular el rango de items a mostrar (scroll)
        start_index = max(0, self.selected_index - visible_items // 2)
        end_index = min(len(self.json_files), start_index + visible_items)
        
        if end_index - start_index < visible_items:
            start_index = max(0, end_index - visible_items)
        
        for i in range(start_index, end_index):
            filename = self.json_files[i]
            y_pos = start_y + (i - start_index) * 35
            
            # Fondo para el item seleccionado
            if i == self.selected_index:
                rect = pygame.Rect(50, y_pos - 5, self.window_size[0] - 100, 30)
                pygame.draw.rect(self.screen, self.colors['selected_bg'], rect)
                pygame.draw.rect(self.screen, self.colors['selected'], rect, 2)
                text_color = self.colors['selected']
            else:
                text_color = self.colors['text']
            
            # Texto del archivo
            file_text = self.font_option.render(filename, True, text_color)
            text_rect = file_text.get_rect(center=(self.window_size[0] // 2, y_pos + 10))
            self.screen.blit(file_text, text_rect)
        
        # Indicador de scroll si hay más archivos
        if len(self.json_files) > visible_items:
            scroll_info = f"{self.selected_index + 1}/{len(self.json_files)}"
            scroll_text = self.font_small.render(scroll_info, True, self.colors['border'])
            scroll_rect = scroll_text.get_rect(bottomright=(self.window_size[0] - 20, self.window_size[1] - 20))
            self.screen.blit(scroll_text, scroll_rect)
        
        pygame.display.flip()
    
    def select_file(self):
        """
        Método principal que ejecuta el menú y devuelve el archivo seleccionado.
        
        Returns:
            str: Nombre del archivo JSON seleccionado, o None si se cancela
        """
        if not self.json_files:
            print("No hay archivos JSON disponibles")
            return None
        
        running = True
        while running:
            action = self._handle_events()
            
            if action == "quit":
                return None
            
            elif action == "select":
                selected_file = self.folder_name + "/" + self.json_files[self.selected_index]
                return selected_file
            
            self._draw_menu()
            self.clock.tick(60)  # 60 FPS
        
        #pygame.quit()
        return None
