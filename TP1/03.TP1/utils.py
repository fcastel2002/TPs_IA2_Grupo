# utils.py

import csv
import sys

def compute_frequencies(orders):
    """
    Calcula la frecuencia de cada producto (entero) en la lista de órdenes.
    orders: lista de listas, cada orden es una lista de productos (como strings).
    Retorna un diccionario {producto: frecuencia}.
    """
    freq = {}
    for order in orders:
        for prod in order:
            try:
                p = int(prod)
                freq[p] = freq.get(p, 0) + 1
            except:
                continue
    return freq
