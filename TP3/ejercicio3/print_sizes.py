from PIL import Image
import os

# Ajusta estas rutas si tu carpeta Assets está en otro lugar
folders = [
    "Assets/Bird",
    "Assets/Cactus"
]

for folder in folders:
    print(f"\nCarpeta: {folder}")
    for fname in os.listdir(folder):
        if fname.lower().endswith(".png"):
            path = os.path.join(folder, fname)
            with Image.open(path) as img:
                w, h = img.size
            print(f"  {fname}: ancho = {w}px, alto = {h}px")
