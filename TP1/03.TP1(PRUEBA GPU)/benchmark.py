# benchmark.py

import time
import numpy as np
from aplicacion import Aplicacion
from agente import Agente
from gpu_pathfinder import a_star_gpu, temple_simulado_gpu

def benchmark_a_star():
    """Compara rendimiento de A* en CPU vs GPU"""
    # Crear tablero
    app = Aplicacion({'filas': 11, 'columnas': 13})
    app.llenar_tablero()
    tablero = app.tablero
    
    # Seleccionar inicio y objetivos
    inicio = tablero.casilleros[5 * tablero.columnas + 0]  # Celda C
    objetivos = []
    for i in range(1, 6):
        indice = tablero.buscar_por_caracter(str(i))
        if indice is not None:
            objetivos.append(tablero.casilleros[indice])
    
    agente = Agente(tablero)
    
    # Benchmark CPU
    start_time = time.time()
    for _ in range(10):  # Ejecutar varias veces para obtener un promedio
        for objetivo in objetivos:
            camino_cpu = agente.a_star(inicio, objetivo, mostrar=False)
    cpu_time = time.time() - start_time
    
    # Benchmark GPU
    start_time = time.time()
    for _ in range(10):
        for objetivo in objetivos:
            camino_gpu = agente.a_star_gpu(inicio, objetivo, mostrar=False)
    gpu_time = time.time() - start_time
    
    print(f"Tiempo A* en CPU: {cpu_time:.4f} segundos")
    print(f"Tiempo A* en GPU: {gpu_time:.4f} segundos")
    print(f"Aceleración: {cpu_time/gpu_time:.2f}x")

def benchmark_temple_simulado():
    """Compara rendimiento de Temple Simulado en CPU vs GPU"""
    # Crear tablero
    app = Aplicacion({'filas': 11, 'columnas': 13})
    app.llenar_tablero()
    tablero = app.tablero
    
    # Configurar objetivos
    for i in range(1, 6):
        indice = tablero.buscar_por_caracter(str(i))
        if indice is not None:
            tablero.set_objetivo(indice)
    
    tablero.set_inicio(5 * tablero.columnas + 0)  # Celda C
    
    agente = Agente(tablero)
    
    # Benchmark CPU
    start_time = time.time()
    for _ in range(5):
        camino_cpu = agente.temple_simulado_multi_objetivo()
    cpu_time = time.time() - start_time
    
    # Benchmark GPU
    start_time = time.time()
    for _ in range(5):
        camino_gpu = agente.temple_simulado_multi_objetivo_gpu()
    gpu_time = time.time() - start_time
    
    print(f"Tiempo Temple Simulado en CPU: {cpu_time:.4f} segundos")
    print(f"Tiempo Temple Simulado en GPU: {gpu_time:.4f} segundos")
    print(f"Aceleración: {cpu_time/gpu_time:.2f}x")

if __name__ == "__main__":
    print("Benchmarking A*...")
    benchmark_a_star()
    print("\nBenchmarking Temple Simulado...")
    benchmark_temple_simulado()