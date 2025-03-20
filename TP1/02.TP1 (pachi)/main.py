from aplicacion import Aplicacion

def main():
    tablero = {'filas':11,'columnas':13}
    aplicacion = Aplicacion(tablero,'ordenes.csv')
    aplicacion.run()

if __name__ == "__main__":
    main()