
from typing import Iterable, List, Tuple, Union
import pygame as pg
import numpy as np

from modulos.geometry import Shape, Circle, Line
from modulos.neuralnetwork import NeuralNetwork
from modulos.constants import C_BLACK, C_RED
from modulos.circuit import Circuit


class Car():
    body: Shape
    brain: NeuralNetwork
    speed: float
    statusDead: bool
    nextRewardIdx: int

    RADIUS = 7

    MAX_SPEED = 25
    ACCELERATION = 5
    FRICTION = 0.3

    ROTATION_RATE = 5

    ANGULOS = (-90, -60, -30, 0, 30, 60, 90)  # (-80, -40, 0, 40, 80)
    NINPUTS = len(ANGULOS) + 1

    def __init__(
            self, pos: Tuple[float, float],
            layers: int, layersize: int, isCopy: bool = False) -> None:

        self.body = Circle(*pos, Car.RADIUS)
        self.brain = NeuralNetwork(Car.NINPUTS, 3, layers, layersize, isCopy)

        self.speed = 0
        self.statusDead = False
        self.nextRewardIdx = 0

    def checkCollision(self, lines: Union[List[Line], Line]) -> bool:

        if type(lines) is not list:
            return self.body.touchingLine(lines)

        for line in lines:
            if self.body.touchingLine(line):
                return True

        return False

    def think(self, data: np.ndarray) -> Iterable[bool]:
        '''
        Return:
            - turnleft
            - accelerate
            - turnright
        '''
        return self.brain.process(data)

    def move(self, turnleft: bool, accelerate: bool, turnright: bool) -> None:

        self.speed *= Car.FRICTION

        if turnleft != turnright:
            if turnleft:
                self.body.rotateDegree(Car.ROTATION_RATE)
            else:
                self.body.rotateDegree(-Car.ROTATION_RATE)

        if accelerate:
            self.speed += Car.ACCELERATION
            self.speed = min(self.speed, Car.MAX_SPEED)

        vx = self.speed * self.body.direction.x
        vy = self.speed * self.body.direction.y
        self.body.addOffset(vx, vy)
        return

    def update(self, circuit: Circuit) -> bool:
        ''' Devuelve False solo si no se ha procesado nada (coche "muerto") '''

        if self.statusDead:
            return False

        if len(circuit.limits) and self.checkCollision(circuit.limits):
            self.statusDead = True
            self.speed = 0
            return True

        rll = len(circuit.reward_lines)
        if rll and self.checkCollision(
                circuit.reward_lines[self.nextRewardIdx % rll]):
            self.nextRewardIdx += 1

        data = self.getEnvironment(circuit)
        tl, acc, tr = self.think(data)
        self.move(tl, acc, tr)

        return True

    def draw(self, surface: pg.Surface):

        self.body.draw(surface, C_RED)
        long = 20
        x, y = long * self.body.direction.x, long * self.body.direction.y
        a = (self.body.center.x, self.body.center.y)
        b = (a[0] + x, a[1] + y)
        pg.draw.line(surface, C_BLACK, a, b, 2)
        return

    def copy(self) -> 'Car':
        c = Car((0, 0), 5, 5, True)
        c.speed = self.speed
        c.statusDead = self.statusDead
        c.nextRewardIdx = 0

        c.brain = self.brain.copy()
        c.body = self.body.copy()

        return c

    def recombinar(
            a: 'Car', b: 'Car'
            ) -> None:
        '''
        Genera 2 nuevas redes cruzando 2 originales. Inplace.
        '''
        NeuralNetwork.cruzar(a.brain, b.brain, True)
        return

    def getEnvironment(self, circuit: Circuit) -> np.ndarray:

        data = np.zeros((Car.NINPUTS, ), dtype=float)

        for i, an in enumerate(Car.ANGULOS):
            data[i] = self.getDistanceOnAngle(circuit, an)

        data[-1] = self.speed
        return data

    def getDistanceOnAngle(
            self, circuit: Circuit, angulo: float) -> float:

        ray = self.body.direction.copy()
        ray.rotateDegree(angulo)
        ray.scale(10000)
        ray.addOffset(ray.x, ray.y)
        ray = Line(self.body.center, ray)

        points = [
            segment.intersection(ray)
            for segment in circuit.limits]
        points = [
            p for p in points
            if p is not None]

        if not len(points):
            return 999999

        dis = [
            self.body.center.distance(poi)
            for poi in points]

        return min(dis)

    def resetBody(self) -> None:
        self.body.direction.set(-1, 0)
        self.body.center.set(0, 0)

    def resetStatusDead(self) -> None:
        self.statusDead = False

    def resetSpeed(self) -> None:
        self.speed = 0

    def resetNextReward(self) -> None:
        self.nextRewardIdx = 0

    def resetAll(self) -> None:
        self.resetBody()
        self.resetStatusDead()
        self.resetSpeed()
        self.resetNextReward()

        return

    def setPosition(self, x: float, y: float) -> None:
        self.body.center.set(x, y)

    def mutate(self, mrate: float) -> 'Car':
        '''Return: self'''
        self.brain.mutate(mrate)
        return self

    def __repr__(self) -> str:
        c = self.__class__.__name__
        lin = len(self.brain.pesos)
        shp = self.body.__class__.__name__
        return f'{c}(shape={shp}, layers={lin})'
