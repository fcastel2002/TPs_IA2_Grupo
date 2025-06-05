import os
import subprocess
from aplicacion import Videojuego

        
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=INFO, 1=WARNING, 2=ERROR, 3=FATAL
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


if __name__ == "__main__":
    videojuego = Videojuego()
    videojuego.correr_videojuego()
