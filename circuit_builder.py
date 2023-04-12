
import pygame as pg
from sys import argv

from modulos.constants import C_BLACK, C_GREEN, C_WHITE, TICK
from modulos.geometry import Line, Point
from modulos.circuit import Circuit


help = f'''
Help:
 - Para editar un circuito existente: {argv[0]} <fichero>.ct
 - Para crear un nuevo circuito con fondo: {argv[0]} <imagen>

 - Any key to switch mode between drawing limits and rewards
 - Left click to mark a point
 - If left click and point already marked, it will create a line
 - Right click to remove all the lines that have at least 1 point in the radius
 - If right click and point already marked, unmark last point
'''

if __name__ == '__main__':
    print(help)
    window_size = (700, 500)

    bg = edit = None
    if len(argv) == 2:
        ar = argv[1].lstrip().rstrip()
        if ar.endswith('.ct'):  # Editar circuito existente
            edit = ar
            print(f'Editing "{edit}" track')
        else:  # Usar el fichero como imagen de fondo
            bg = ar
            print(f'Using "{bg}" as background')

    # Creacion del circuito
    c = Circuit(filename=edit, background_file=bg)
    if edit is None:
        c.backgroundNewSize(*window_size)

    # objetos pygame de impresion
    clock = pg.time.Clock()
    window = pg.display.set_mode(window_size)
    # Superficie con capa alpha
    draw_surf = pg.Surface(window_size, pg.SRCALPHA)

    # Variables de bucle
    run = updated = True
    shownTimes = 0

    cursorprev, cursor = (0, 0), None  # Variables de posicion del cursor

    lastPoint = None  # Ultimo punto creado
    removeRadius = 10  # Radio de borrado
    rewards = False  # Creando limites o rewards
    while run:

        if run and updated:
            window.fill(C_WHITE)
            # Impresion del circuito
            c.draw(window, True, True, True)

            # Marca del ultimo punto pulsado
            if lastPoint is not None:
                pg.draw.circle(
                    window, (C_GREEN if rewards else C_BLACK),
                    lastPoint, 2, width=0)

            # Zona de borrado
            # Y marca si esta creando limite o reward
            if cursor is not None:
                draw_surf.fill((0, 0, 0, 0))
                col = pg.Color(*(C_GREEN if rewards else C_BLACK), 150)
                pg.draw.circle(  # Semi transparente
                    draw_surf, col,
                    cursor, removeRadius, width=0)
                window.blit(draw_surf, (0, 0))

            pg.display.update()
            shownTimes += 1
            print(
                '      ' 'Times shown:', shownTimes,
                '\t Cursor:', cursor, end='                 \r')
            updated = False

        clock.tick(TICK)

        # Input
        cursor = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            elif event.type == pg.MOUSEBUTTONDOWN:
                clickLeft, _, clickRight = pg.mouse.get_pressed()
                updated = True

                if clickRight:  # Borrar lineas
                    lastPoint = None
                    c.removeInRadius(Point(*cursor), removeRadius)

                elif clickLeft:
                    if lastPoint is None:  # Crear punto 1
                        lastPoint = cursor
                    else:  # Crear nueva linea
                        c.addLine(Line(*lastPoint, *cursor), rewards)
                        lastPoint = None if rewards else cursor

            elif event.type == pg.KEYDOWN:
                key, keyname = event.unicode, pg.key.name(event.key)
                print(key, end='\r')
                rewards = not rewards  # Cambiar el modo
                lastPoint = None
                updated = True
                if keyname == 'escape':
                    run = False

        if cursor != cursorprev:
            updated = True

        cursorprev = cursor

    pg.display.quit()
    s = c.dumps()
    if edit:
        file = edit
    else:
        print('                        ')
        file = input('Filename: ').lstrip().rstrip()
        if len(file):
            file = './circuito/' + file + '.ct'

    if len(file):
        with open(file, 'w') as f:
            f.write(s)
