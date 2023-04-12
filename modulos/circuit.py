
from typing import List, Tuple, Union
from os.path import isfile
import pygame as pg

from modulos.constants import C_MAGENTA, C_BLACK, C_WHITE, error, warning
from modulos.geometry import Line, Point


class Circuit():

    limits: List[Line]
    reward_lines: List[Line]
    width: float
    height: float
    startPoint: Point

    background: Union[None, pg.Surface]
    background_path: Union[None, str]
    background_offset: Point
    background_size: Union[None, Tuple[int, int]]

    def __init__(
            self, filename: Union[str, None] = None,
            background_file: Union[str, None] = None) -> None:

        self.limits = None
        self.reward_lines = None
        self.width = None
        self.height = None
        self.startPoint = Point(0, 0)

        self.background = None
        self.background_path = None
        self.background_offset = Point(0, 0)
        self.background_size = None

        if filename is None:
            self.limits = []
            self.reward_lines = []
        else:
            self.readFromFile(filename)

        if background_file is not None:
            # Sobreescribe el background que hubiera
            if self.background:
                del self.background
            self.background_path = background_file
            self.background = pg.image.load(background_file)
        if self.background:
            self.background_size = (
                self.background.get_width(), self.background.get_height())

    def readFromFile(self, filename: str):

        with open(filename, 'r') as f:
            lines = f.readlines()

        self.reward_lines = []
        self.limits = []

        rew = False
        maxp = Point(-float('inf'), -float('inf'))
        minp = Point(float('inf'), float('inf'))
        for i, lin in enumerate(lines, 1):
            lin = lin.lstrip().rstrip().lower()
            if not len(lin) or lin.startswith('#'):
                continue

            if lin in 'start' or 'start' in lin:
                words = lin.split()[-2:]
                if len(words) < 2:
                    error('Starting point must have 2 coordinates')
                x, y = float(words[0]), float(words[1])
                self.startPoint.x = x
                self.startPoint.y = y

            elif lin in 'rewards' or 'rewards' in lin:
                rew = True
            elif lin in 'background' or 'background' in lin:
                words = lin.split()
                if len(words) != 2 and len(words) != 4:
                    warning(
                        f'Error en linea {i} de background, la linea '
                        f'deberia tener 2 componentes, no {len(words)}')
                else:
                    if isfile(words[1]):
                        self.background_path = words[1]
                        if len(words) == 4:
                            self.background_size = (
                                int(float(words[2])), int(float(words[3])))
                    else:
                        warning(f'No existe la imagen background "{words[1]}"')
            else:

                components = [e for e in lin.split() if len(e)]
                if len(components) > 4:
                    warning(f'Demasiados elementos en la linea {i}')
                    components = components[:4]

                if len(components) % 2 or not len(components):
                    error(f'Numero erroneo de elementos en la linea {i}')

                a = Point(*(int(float(c)) for c in components[:2]))
                b = (
                    Point(*(int(float(c)) for c in components[2:]))
                    if len(components) == 4 else None)

                if b is None and (
                        (not rew and not len(self.limits)) or
                        (rew and not len(self.reward_lines))):
                    error(
                        f'El segundo punto de la linea {i} '
                        'deberia estar inicializado')

                if b is None:
                    a, b = (
                        self.reward_lines[-1].b.copy()
                        if rew else self.limits[-1].b.copy()), a

                if rew:
                    self.reward_lines.append(Line(a, b))
                else:
                    self.limits.append(Line(a, b))

                minp.x, minp.y = min(minp.x, a.x, b.x), min(minp.y, a.y, b.y)
                maxp.x, maxp.y = max(maxp.x, a.x, b.x), max(maxp.y, a.y, b.y)

        self.height = maxp.y - minp.y
        self.width = maxp.x - minp.x
        if self.background_path:
            self.background = pg.image.load(self.background_path)
            if self.background_size:
                self.background = pg.transform.scale(
                    self.background, self.background_size)
            else:
                self.background_size = (
                    self.background.get_width(), self.background.get_height())

            self.width = max(self.width, self.background_size[0])
            self.height = max(self.height, self.background_size[1])

        if not self.startPoint.x and not self.startPoint.y:
            self.startPoint.x = self.width / 2
            self.startPoint.y = self.height / 2

    def addOffset(self, x: int = 0, y: int = 0):

        self.background_offset.addOffset(x, y)

        for lin in self.limits:
            lin.addOffset(x, y)

        for lin in self.reward_lines:
            lin.addOffset(x, y)

    def scale(self, factor: Union[float, Tuple[float, float]]):

        if type(factor) is tuple:
            xf, yf = factor
        else:
            xf, yf = factor, factor

        for lin in self.limits:
            lin.scale(factor)

        for lin in self.reward_lines:
            lin.scale(factor)

        if self.width and self.height:
            self.width = int(self.width * xf)
            self.height = int(self.height * yf)

        self.scaleBackground(factor)

    def scaleBackground(self, factor: Union[float, Tuple[float, float]]):

        if not self.background:
            warning(
                'No se puede escalar el fondo porque no '
                'hay ninguno cargado')
            return

        if type(factor) is tuple:
            xf, yf = factor
        else:
            xf, yf = factor, factor

        news = (
            int(self.background.get_width() * xf),
            int(self.background.get_height() * yf))
        self.background = pg.transform.scale(
            self.background, news)
        self.background_size = news

    def backgroundNewSize(
            self, width: Union[int, float], height: Union[int, float]):
        if not self.background:
            warning(
                'No se puede cambiar el tamano del fondo porque no '
                'hay ninguno cargado')
            return

        news = (int(width), int(height))
        self.background = pg.transform.scale(
            self.background, news)
        self.background_size = news

        if self.width and self.height:
            self.height = max(self.height, height)
            self.width = max(self.width, width)
        else:
            self.height, self.width = height, width

    def dumps(self) -> str:

        s = t = ''
        prev = None
        for line in self.limits:
            if prev and prev.b.inRadius(line.a, 4):
                # Junta puntos de lineas que esten muy cerca
                # Para reducir espacio del fichero
                s += f'{line.b.x} {line.b.y}\n'
            else:
                s += f'{line.a.x} {line.a.y} {line.b.x} {line.b.y}\n'
            prev = line

        s += f'Start {self.startPoint.x} {self.startPoint.y}\n'
        prev = None
        for line in self.reward_lines:
            if prev and prev.b.inRadius(line.a, 4):
                t += f'{line.b.x} {line.b.y}\n'
            else:
                t += f'{line.a.x} {line.a.y} {line.b.x} {line.b.y}\n'
            prev = line

        if self.background_path is not None:
            bg = (
                f'\n\nBackground {self.background_path} '
                f'{self.background_size[0]} {self.background_size[1]}\n')

            return s + '\n\nReward\n\n' + t + bg + '\n'

        return s + '\n\nReward\n\n' + t

    def draw(
            self, surface: pg.Surface, showRewards: bool = False,
            showLimits: bool = True, showBackground: bool = True):

        if showBackground and self.background:
            surface.blit(self.background, self.background_offset.asTuple())

        if showLimits:
            for lin in self.limits:
                lin.draw(surface, C_BLACK)

        if showRewards:
            n = min(len(self.reward_lines) * 5, 240)
            for lin in self.reward_lines:
                lin.draw(surface, (n, 240, n))
                n -= 5
                n = max(0, n)

        if self.startPoint:
            x, y = self.startPoint.asTuple()
            pg.draw.line(surface, C_MAGENTA, (x+3, y), (x-3, y), width=2)
            pg.draw.line(surface, C_MAGENTA, (x, y+3), (x, y-3), width=2)

    def removeInRadius(self, point: Point, radius: float):
        '''
        Elimina todas las lineas que tengan al menos un punto dentro del radio
        '''
        rem = 0

        i = 0
        while i < len(self.limits):
            lin = self.limits[i]
            if lin.a.inRadius(point, radius) or lin.b.inRadius(point, radius):
                self.limits.pop(i)
                rem += 1
            else:
                i += 1
        i = 0
        while i < len(self.reward_lines):
            lin = self.reward_lines[i]
            if lin.a.inRadius(point, radius) or lin.b.inRadius(point, radius):
                self.reward_lines.pop(i)
                rem += 1
            else:
                i += 1

        return rem

    def addLine(self, line: Line, reward: bool) -> None:
        if reward:
            self.reward_lines.append(line)
        else:
            self.limits.append(line)


if __name__ == '__main__':
    c = Circuit('circuito/testimg1.ct')

    c.scale(1.3)
    # c.addOffset(*padding[:2])

    window_size = (c.width, c.height)

    clock = pg.time.Clock()
    window = pg.display.set_mode(window_size)

    window.fill(C_WHITE)
    c.draw(window, True)
    pg.display.update()

    run = True
    TICK = 10
    while run:
        clock.tick(TICK)

        pos = None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
