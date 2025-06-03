import json
import os
from datetime import datetime

class GenomeManager:
    def __init__(self, filename="best_genomes.json"):
        self.filename = filename
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Crea el archivo si no existe"""
        if not os.path.exists(self.filename):
            initial_data = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "total_generations": 0,
                    "best_score_ever": 0
                },
                "elite_genomes": []
            }
            with open(self.filename, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def save_elite_genomes(self, elite_dinosaurs, generation, best_score):
        """Guarda los genomas de la élite actual"""
        try:
            # Leer datos existentes
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            # Preparar genomas para guardar
            elite_genomes = []
            for i, dino in enumerate(elite_dinosaurs):
                genome_data = {
                    "rank": i + 1,
                    "id": dino.id,
                    "score": dino.score,
                    "generation": generation,
                    "connections": dino.count_connections(),
                    "genome": dino.get_genome()
                }
                elite_genomes.append(genome_data)
            
            # Actualizar datos
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_generations"] = generation
            data["metadata"]["best_score_ever"] = max(data["metadata"]["best_score_ever"], best_score)
            data["elite_genomes"] = elite_genomes
            
            # Guardar
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Genomas de élite guardados: {len(elite_genomes)} individuos")
            
        except Exception as e:
            print(f"Error al guardar genomas: {e}")
    
    def load_elite_genomes(self):
        """Carga los genomas de la élite guardados"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            elite_genomes = data.get("elite_genomes", [])
            metadata = data.get("metadata", {})
            
            if elite_genomes:
                print(f"Cargados {len(elite_genomes)} genomas de élite")
                print(f"Mejor score histórico: {metadata.get('best_score_ever', 0)}")
                print(f"Última generación: {metadata.get('total_generations', 0)}")
                
            return elite_genomes, metadata
            
        except Exception as e:
            print(f"Error al cargar genomas: {e}")
            return [], {}
    
    def apply_elite_genomes_to_population(self, population, elite_genomes):
        """Aplica los genomas de élite a la población inicial"""
        if not elite_genomes:
            return 0
        
        applied_count = 0
        for i, genome_data in enumerate(elite_genomes):
            if i < len(population):
                try:
                    population[i].set_genome(genome_data["genome"])
                    population[i].score = genome_data["score"]
                    population[i].id = genome_data["id"]
                    population[i].resetStatus(genetico=True)
                    applied_count += 1
                except Exception as e:
                    print(f"Error aplicando genoma {i}: {e}")
        
        print(f"Aplicados {applied_count} genomas de élite a la población inicial")
        return applied_count
    
    def get_stats(self):
        """Obtiene estadísticas del archivo de genomas"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            metadata = data.get("metadata", {})
            elite_genomes = data.get("elite_genomes", [])
            
            stats = {
                "best_score_ever": metadata.get("best_score_ever", 0),
                "total_generations": metadata.get("total_generations", 0),
                "elite_count": len(elite_genomes),
                "last_updated": metadata.get("last_updated", "Nunca")
            }
            
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}