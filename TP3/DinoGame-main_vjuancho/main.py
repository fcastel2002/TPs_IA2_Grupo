import pygame
import os
import sys

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
                pygame.quit()
                return None
            
            elif action == "select":
                selected_file = self.json_files[self.selected_index]
                pygame.quit()
                return selected_file
            
            self._draw_menu()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        return None

# Ejemplo de uso
if __name__ == "__main__":
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
        window_size=(900, 700),
        colors=custom_colors,  # Opcional, usa colores por defecto si no se especifica
        folder_name="datos_buenas_poblaciones"
    )
    
    # Ejecutar el selector
    selected_file = menu.select_file()
    
    if selected_file:
        print(f"Archivo seleccionado: {selected_file}")
        # Aquí puedes cargar y usar el archivo JSON seleccionado
        # Por ejemplo:
        # import json
        # with open(f"datos_buenas_poblaciones/{selected_file}", 'r') as f:
        #     genome_data = json.load(f)
    else:
        print("Selección cancelada")