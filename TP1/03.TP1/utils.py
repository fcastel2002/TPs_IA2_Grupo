def get_initial_config():
    """
    Retorna la lista de productos en el orden de la configuración inicial
    (la misma que se ve en la imagen por defecto).
    Ajusta este bloque si tu 'llenar_tablero()' difiere en la forma de enumerar.
    """
    config = []
    # Bloque 1..8
    for i in range(1, 9):
        config.append(i)
    # Bloque 9..16
    for i in range(9, 17):
        config.append(i)
    # Bloque 17..24
    for i in range(17, 25):
        config.append(i)
    # Bloque 25..32
    for i in range(25, 33):
        config.append(i)
    # Bloque 33..40
    for i in range(33, 41):
        config.append(i)
    # Bloque 41..48
    for i in range(41, 49):
        config.append(i)
    
    return config
