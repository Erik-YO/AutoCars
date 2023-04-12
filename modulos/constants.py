
# Colores para la interfaz grafica
C_BLACK = (0, 0, 0)
C_WHITE = (250, 250, 250)
C_GREEN = (40, 240, 40)
C_RED = (230, 40, 40)
C_MAGENTA = (200, 30, 200)
C_BLUE = (10, 10, 250)

WARNINGS = True
'''Impresion de warnings'''

TICK = 20
'''Cuantas actualizaciones por segundo'''
TRAINING_TICK = 30
'''Cuantas actualizaciones por segundo en entrenamiento'''


def warning(msg):
    if WARNINGS:
        print(f'Warning: {msg}')


def error(msg):
    raise Exception(f'Error: {msg}')
