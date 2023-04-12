
from typing import Tuple, Union
from math import cos, pi, sin
import pygame as pg

from modulos.constants import error


class Point():

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def set(self, x: float, y: float) -> 'Point':
        self.x, self.y = x, y
        return self

    def addOffset(self, x: float = 0, y: float = 0):
        self.x += x
        self.y += y

    def addPoint(self, point: 'Point') -> None:
        self.x += point.x
        self.y += point.y

    def asTuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def copy(self) -> 'Point':
        return Point(self.x, self.y)

    def scale(self, factor: Union[float, Tuple[float, float]]) -> 'Point':
        if type(factor) is tuple:
            xf, yf = factor
        else:
            xf, yf = factor, factor

        self.x *= xf
        self.y *= yf
        return self

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.x}, {self.y})'

    def add(a: 'Point', b: 'Point') -> 'Point':
        return Point(a.x + b.x, a.y + b.y)

    def subtract(a: 'Point', b: 'Point') -> 'Point':
        return Point(a.x - b.x, a.y - b.y)

    def negative(a: 'Point') -> 'Point':
        return Point(-a.x, -a.y)

    def dot(a: 'Point', b: 'Point') -> float:
        return a.x * b.x + a.y * b.y

    def module(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def cross(a: 'Point', b: 'Point') -> float:
        return a.x * b.y - a.y * b.x

    def distance(self, p: 'Point') -> float:
        a, b = (self.x - p.x), (self.y - p.y)
        return (a*a + b*b) ** 0.5

    def inRadius(self, p: 'Point', radius: float) -> bool:
        a, b = (self.x - p.x), (self.y - p.y)
        r2 = radius * radius
        return (a * a + b * b) < r2

    def rotateDegree(self, angle: float):
        angle *= (pi / 180)
        self.rotateRadians(angle)
        return

    def rotateRadians(self, angle: float):
        '''
        x2=r-u=cosβx1-sinβy1
        y2=t+s=sinβx1+cosβy1
        '''
        c, s = cos(angle), sin(angle)
        x = c * self.x - s * self.y
        y = s * self.x + c * self.y

        m1 = self.module()
        m2 = (x ** 2 + y ** 2) ** 0.5
        m = (m1 / m2)
        self.x = x * m
        self.y = y * m

        return


class Line():

    a: Point
    b: Point

    def __init__(self, x1, y1, x2=None, y2=None) -> None:

        if (
                x2 is None and y2 is None and
                type(y1) is Point and type(x1) is Point):
            self.a = x1
            self.b = y1
        else:
            self.a = Point(x1, y1)
            self.b = Point(x2, y2)

    def addOffset(self, x: int = 0, y: int = 0):
        self.a.addOffset(x, y)
        self.b.addOffset(x, y)

    def scale(self, factor: Union[float, Tuple[float, float]]):

        self.a.scale(factor)
        self.b.scale(factor)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'{(self.a.x, self.a.y, self.b.x, self.b.y)}')

    def draw(self, surface: pg.Surface, color: Tuple[int, int, int]):
        pg.draw.line(
            surface, color,
            self.a.asTuple(), self.b.asTuple(), width=2)

    def intersection_prev(self, line: 'Line') -> Union[Point, None]:
        '''
        Devuelve el punto de interseccion de esta linea con otra

        c + cd * t2 = a + ab * t1
        c - a = ab * t1 + cd * t2
        ac = ab * t1 + cd * t2
        '''

        a, b, c, d = self.a, self.b, line.a, line.b

        cd = Point.subtract(d, c)
        ab = Point.subtract(b, a)

        ab_cross_cd = Point.cross(ab, cd)
        if not ab_cross_cd:
            return None

        ac = Point.subtract(c, a)
        t1 = Point.cross(ac, cd) / ab_cross_cd
        t2 = - Point.cross(ab, ac) / ab_cross_cd

        if t1 > 1 or t1 < 0 or t2 > 1 or t2 < 0:
            return None

        p = Point.add(a, ab.scale(t1))

        return p

    def intersection(self, line: 'Line') -> Union[Point, None]:
        '''
        Devuelve el punto de interseccion de esta linea con otra
        Optimizacion

        c + cd * t2 = a + ab * t1
        c - a = ab * t1 + cd * t2
        ac = ab * t1 + cd * t2
        '''
        a, b, c, d = self.a, self.b, line.a, line.b

        cd_x, cd_y = d.x - c.x, d.y - c.y  # Point.subtract(d, c)
        ab_x, ab_y = b.x - a.x, b.y - a.y  # Point.subtract(b, a)

        ab_cross_cd = ab_x * cd_y - ab_y * cd_x  # Point.cross(ab, cd)
        if not ab_cross_cd:
            return None

        ac_x, ac_y = c.x - a.x, c.y - a.y  # Point.subtract(c, a)
        t1 = (ac_x * cd_y - ac_y * cd_x) / ab_cross_cd  # Point.cross(ac, cd)
        t2 = (ab_y * ac_x - ab_x * ac_y) / ab_cross_cd  # Point.cross(ab, ac)

        if t1 > 1 or t1 < 0 or t2 > 1 or t2 < 0:
            return None

        # p = Point.add(a, ab.scale(t1))
        p = Point(a.x + ab_x * t1, a.y + ab_y * t1)

        return p


'''Formas con area'''


class Shape():

    DEFAULT_DIRECTION = (-1, 0)

    center: Point
    direction: Point

    def copy(self) -> 'Shape':
        raise NotImplementedError()

    def touchingLine(self, line: Line) -> bool:
        raise NotImplementedError()

    def touchingPoint(self, point: Point) -> bool:
        raise NotImplementedError()

    def addOffset(self, x: float, y: float) -> None:
        raise NotImplementedError()

    def draw(self, surface: pg.Surface, color: Tuple[int, int, int]) -> None:
        raise NotImplementedError()

    def rotateDegree(self, angle: float) -> None:
        self.direction.rotateDegree(angle)

    def rotateRadians(self, angle: float) -> None:
        self.direction.rotateRadians(angle)


class Circle(Shape):

    def __init__(self, x: float, y: float, radius: float) -> None:
        self.center = Point(x, y)
        self.direction = Point(*Shape.DEFAULT_DIRECTION)
        self.radius = radius

    def touchingLineFastCheck(self, line: Line) -> bool:
        '''False es seguro que no, True es puede que si'''

        c, r = self.center, self.radius
        a, b = line.a, line.b
        if a.x > c.x + r and b.x > c.x + r:
            return False
        if a.x < c.x - r and b.x < c.x - r:
            return False

        if a.y > c.y + r and b.y > c.y + r:
            return False
        if a.y < c.y - r and b.y < c.y - r:
            return False

        return True

    def touchingLine(self, line: Line) -> bool:

        if not self.touchingLineFastCheck(line):
            return False

        # Check p inside Circle, a inside Circle & b inside Circle
        p, a, b = self.center, line.a, line.b
        if self.touchingPoint(a):
            return True
        if self.touchingPoint(b):
            return True

        vx, vy = b.x - a.x, b.y - a.y
        vy2, vx2 = vy * vy, vx * vx
        vxy = vx * vy

        up = vxy * (p.y - a.y) + (vy2 * a.x + vx2 * p.x)
        do = (vy2 + vx2)

        # Proyeccion del punto sobre la linea
        if not do:
            do = 0.000001
        x = up / do
        if not vy:
            vy = 0.000001
        y = p.y - ((vx / vy) * (x - p.x))

        return self.touchingPoint(x, y)

    def touchingPoint(self, pointOrX: Union[float, Point], y: float = None):

        if y is None:
            x, y = pointOrX.x, pointOrX.y
        else:
            x = pointOrX

        a = x - self.center.x
        b = y - self.center.y
        dis = a * a + b * b

        return dis <= (self.radius * self.radius)

    def addOffset(self, mx: float = 0, my: float = 0):
        self.center.addOffset(mx, my)
        return

    def copy(self) -> 'Circle':
        c = Circle(self.center.x, self.center.y, self.radius)
        c.direction = self.direction.copy()
        return c

    def draw(self, surface: pg.Surface, color: Tuple[int, int, int]):
        pg.draw.circle(
            surface, color,
            self.center.asTuple(), self.radius, width=0)
