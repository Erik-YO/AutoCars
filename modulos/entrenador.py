
from random import randint, random
from typing import Any, List, Tuple
import pygame as pg

from math import ceil
import numpy as np

from modulos.constants import C_BLACK, C_WHITE, TRAINING_TICK
from modulos.circuit import Circuit
from modulos.car import Car

LOG = True
DEBUG = True


class RandomConstructorInterface():

    def getRandomIndividual(self) -> Any:
        raise NotImplementedError()

    def fitness(self, poblacion: List[Any]) -> List[float]:
        raise NotImplementedError()

    def recombinacion(self, a: Any, b: Any) -> Tuple[Any, Any]:
        raise NotImplementedError()

    def mutacion(self, ind: Any, mrate: float) -> Any:
        raise NotImplementedError()


class CarConstructor(RandomConstructorInterface):

    pos: Tuple[float, float]
    minLayers: int
    maxLayers: int
    layersSize: int

    def __init__(
            self, pos: Tuple[float, float],
            minLayers: int, maxLayers: int,
            layersSize: int) -> None:
        self.minLayers = minLayers
        self.maxLayers = maxLayers
        self.layersSize = layersSize
        self.pos = pos

    def getRandomIndividual(self):
        layers = randint(self.minLayers, self.maxLayers)
        return Car(self.pos, layers, self.layersSize)

    def recombinacion(self, a: Car, b: Car) -> Tuple[Car, Car]:
        Car.recombinar(a, b)
        return a, b

    def mutacion(self, ind: Car, mrate: float) -> Car:
        ind.mutate(mrate)
        return ind

    def fitness(
            poblacion: List[Car], circuito: Circuit,
            maxIters: int = 400, generacion: int = None,
            show: bool = False, endIfAllStopped: bool = True) -> List[float]:

        for ind in poblacion:  # Resetear los individuos
            ind.resetAll()
            ind.setPosition(*circuito.startPoint.asTuple())

        if show:  # Objetos de visualizacion
            window_size = (circuito.width, circuito.height)
            clock = pg.time.Clock()
            window = pg.display.set_mode(window_size)
            if generacion:
                pg.font.init()
                fuente = pg.font.SysFont('arial', 20)

        # Numero de "frames" que lleva sobreviviendo cada individuo
        aliveIters = [0 for _ in poblacion]
        # Numero de "frames" que llevan parados todos los individuos
        speedStopped = 0
        # Numero de individuos con vida
        aliveIndividuos = len(poblacion)

        # Variables de bucle
        run = updated = True
        iters = 1
        while run and speedStopped < 3 and iters < maxIters:

            if show and run and updated:
                # Visualizacion
                window.fill(C_WHITE)
                circuito.draw(window, True, True, True)
                for car in poblacion:
                    car.draw(window)

                if generacion:  # Informacion
                    text = fuente.render(
                        f'Generacion {generacion} - Frame {iters}',
                        False, C_BLACK)
                    window.blit(text, (0, 0))

                pg.display.update()
                updated = False

            if show:
                clock.tick(TRAINING_TICK)

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        run = False

            for i, ind in enumerate(poblacion):  # Actualizacion
                dead = ind.statusDead
                updated = ind.update(circuito) or updated
                if dead != ind.statusDead:
                    aliveIters[i] = iters

            if run:
                aliveIndividuos = sum(  # Cuantos "vivos"
                    1 for ind in poblacion if (not ind.statusDead))
                if not aliveIndividuos:
                    run = False

            if run and any(
                    i.nextRewardIdx > len(circuito.reward_lines) * 3
                    # Mas de 3 vueltas completas al circuito
                    for i in poblacion):
                run = False

            if endIfAllStopped and run:
                if all(ind.speed < 0.01 for ind in poblacion):
                    speedStopped += 1  # Todos quietos
                else:
                    speedStopped = 0

            iters += 1

        print('Frames:', iters, '/', maxIters)
        if show:
            pg.display.quit()
            if generacion:
                pg.font.quit()

        print(
            'Max reward:',
            max(ind.nextRewardIdx for ind in poblacion))
        fits = [
            # Lo lejos que llegan + ~proporcion de tiempo que estan vivos
            # Valoramos que usen menos frames para llegar a las
            # mismas recompensas
            (
                (
                    (ind.nextRewardIdx)  # + (1 - (aliveFrames / maxIters)) / 2
                ) if ind.nextRewardIdx > 0 else (aliveFrames / maxIters) * 0.9
                ) * 100 / maxIters
            for ind, aliveFrames in zip(poblacion, aliveIters)]

        return fits


class Entrenador:

    constructor: CarConstructor
    list_best_fit_indiv: List[Any]
    list_fit_med: List[float]
    list_fit_best: List[float]

    populationSize: int
    maxGeneraciones: int
    nIterNoChange: int
    maxLayers: int
    layersSize: int
    probabCruce: float
    mutationRate: float
    elitismo: int
    ruleta: bool
    renovacion: int

    individuo: Car

    def __init__(
            self,
            constructor: CarConstructor,
            populationSize: int = 50,
            maxGeneraciones: int = 50,
            nIterNoChange: int = None,
            probabCruce: float = 0.6,
            mutationRate: float = 0.01,
            elitismo: int = 0.05,
            ruleta: bool = True,
            renovacion: float = 0.05
            ) -> None:
        """
        populationSize: int, Numero de individuos a entrenar
        maxGeneraciones: int, numero maximo de generaciones a entrenar
        nIterNoChange: numero de generaciones sin mejoras de fitness tras las
        cuales se para el entrenamiento
        maxLayers: int, numero maximo de reglas por individuo
        probabCruce: float en [0, 1], probabilidad de recombinar un
        individuo con otro
        mutationRate: float en [0, 1], es la proporcion de individuos que seran
        cambiados aleatoriamente.
        elitismo: float en [0, 1], la proporcion de mejores individuos que se
        reservan de una generacion a la siguiente
        ruleta: bool, seleccionar individuos aleatoriamente con probabilidad
        proporcional al fitness
        renovacion: float, porcentaje de nuevos individuos en cada generacion
        """

        if populationSize < 1:
            raise ValueError('populationSize debe ser al menos 1')

        if maxGeneraciones < 1:
            raise ValueError('maxGeneraciones debe ser al menos 1')

        if nIterNoChange is None:
            nIterNoChange = maxGeneraciones
        if nIterNoChange < 1 or nIterNoChange > maxGeneraciones:
            raise ValueError(
                'nIterNoChange debe estar entre 1 y maxGeneraciones')

        if probabCruce > 1 or probabCruce < 0:
            raise ValueError('probabCruce debe estar en el rango [0, 1]')

        if mutationRate > 1 or mutationRate < 0:
            raise ValueError('mutationRate debe estar en el rango [0, 1]')

        if elitismo < 0 or elitismo > 1:
            raise ValueError('elitismo debe estar en el rango [0, 1]')

        if renovacion < 0 or renovacion + elitismo > 1:
            raise ValueError(
                'renovacion debe estar en el rango [0, 1-elitismo]')

        # Listas de control de mejora intergeneracional
        self.list_best_fit_indiv = []
        self.list_fit_med = []
        self.list_fit_best = []

        # Hiperparametros
        self.populationSize = populationSize
        self.maxGeneraciones = maxGeneraciones
        self.nIterNoChange = nIterNoChange + 1
        self.probabCruce = probabCruce
        self.mutationRate = mutationRate
        self.elitismo = ceil(elitismo * populationSize)
        self.ruleta = ruleta
        self.renovacion = ceil(renovacion * populationSize)

        if self.elitismo + self.renovacion > populationSize:
            raise ValueError(
                'renovacion es demasiado grande para esta poblacion')

        self.constructor = constructor

        # Mejor individuo
        self.individuo = None
        self.mejores = None

    def train(
            self, circuito: Circuit, starting_individuals: List[Any] = None,
            show: int = None):
        '''
        show: int, si None o 0 no se muestra, si > 0 se muestra una
        de cada <show> generaciones
        '''

        if not len(circuito.limits) or not len(circuito.reward_lines):
            raise ValueError('Circuito sin limites o recompensas')

        poblacion = self.createGeneration()  # Primera generacion
        if starting_individuals:
            newps = self.populationSize - len(starting_individuals)
            poblacion = poblacion[:newps]
            poblacion.extend(starting_individuals)

        if DEBUG:
            print(poblacion[0])

        self.mejores = []
        pobBase = self.populationSize - self.elitismo - self.renovacion
        for generacion in range(self.maxGeneraciones):
            # Calculo de fitness
            poblacionSorted, fits = self.get_fitness_population(
                poblacion, circuito, generacion, show)

            # Seleccion de progenitores
            if self.ruleta:
                progenitores = self.seleccionRuleta(
                    poblacionSorted, fits, pobBase)
            else:
                progenitores = poblacionSorted[:pobBase]

            progenitores = self.recombinacion([
                p.copy() for p in progenitores])
            progenitores = self.mutacion([
                p.copy() for p in progenitores])

            if self.elitismo:
                elite, i = [], 0
                while len(elite) < self.elitismo and i < len(poblacionSorted):
                    if poblacionSorted[i] not in elite:
                        elite.append(poblacionSorted[i].copy())
                    i += 1
                progenitores.extend(elite)
            if self.renovacion:
                progenitores.extend(self.createGeneration(self.renovacion))

            poblacion = progenitores

            self.mejores.append((poblacionSorted[0], fits[0]))
            if len(self.mejores) > self.nIterNoChange:
                self.mejores.pop(0)

            self.list_best_fit_indiv.append(self.mejores[-1][1])
            self.list_fit_med.append(np.mean(fits))
            self.list_fit_best.append(fits[0])

            if LOG:
                print(
                    f'Generacion {generacion}',
                    f'Mejor: {self.mejores[-1][0]}',
                    f'Con fitness {self.mejores[-1][1]}',
                    f'Fitness medio: {np.mean(fits)} ',
                    '', sep='\n')

            if len(self.mejores) >= self.nIterNoChange:
                if self.mejores[-1] == self.mejores[0]:
                    if LOG:
                        print(
                            self.nIterNoChange - 1,
                            'generaciones sin cambios.',
                            'Deteniendo el entrenamiento.')
                    break

        self.individuo = self.mejores[-1][0]

        if DEBUG:

            print(
                f'\nMEJORES ({min(5, len(poblacionSorted))}):\n', '\n'.join([
                    str(m) + ' - ' + ' - ' + str(round(ft, 4))
                    for m, ft
                    in zip(poblacionSorted[:5], fits[:5])
                    if len(str(m)) < 999]), sep='')

        input(
            '###  ENTRENAMIENTO TERMINADO ###\n      '
            'Enter para mostrar los resultados')
        self.constructor.__class__.fitness([
            m[0] for m in self.mejores], circuito, show=True)

        return self

    def createGeneration(self, n: int = None):
        '''Crea una generacion aleatoria'''
        if n is None:
            n = self.populationSize

        poblacion = [
            self.constructor.getRandomIndividual()
            for _ in range(n)]

        return poblacion

    def get_fitness_population(
            self, poblacion: List[Car], circuito: Circuit,
            generacion: int, show: int = None
            ) -> Tuple[List[Car], List[float]]:
        """
        Devuelve una lista con la poblacion ordenada por fitness
        y otra lista con los valores de fitness
        """
        # Aumentamos el maximo de frames cada 5 generaciones
        maxIt = max(50 * (1 + generacion // 5), 100)
        show = show and not (generacion % show)
        # Calcular lista de fitness
        fits = self.constructor.__class__.fitness(
            poblacion, circuito,
            # Parametros de ajuste
            maxIters=maxIt,
            generacion=generacion,
            show=show)

        # Ordenar individuos y fit por fit
        poblacion = [
            ind for ind, _ in
            sorted(
                zip(poblacion, fits),
                key=lambda e: e[1],
                reverse=True)]
        fits.sort(reverse=True)

        return poblacion, fits

    def recombinacion(
            self, progenitores: List[Car]) -> List[Car]:
        """
        Con probabilidad probabCruce, cruza 2 individuos en un punto (inplace).
        """
        prg = progenitores
        if self.probabCruce == 0:
            return prg

        cruz = []
        for i in range(len(prg)):
            r = random()
            if r < self.probabCruce:
                cruz.append(i)

        # Numero par de individuos
        if len(cruz) % 2:
            cruz.pop()

        for i in range(0, len(cruz), 2):
            a, b = prg[cruz[i]], prg[cruz[i + 1]]
            # Se reemplazan los progenitores por los descendientes
            prg[cruz[i]], prg[cruz[i + 1]] = self.constructor.recombinacion(
                a, b)

        return prg

    def mutacion(self, poblacion) -> List:
        for i in range(len(poblacion)):
            poblacion[i] = self.constructor.mutacion(
                poblacion[i], self.mutationRate)

        return poblacion

    def seleccionRuleta(
            self, poblacion: List[int],
            fits: List[float], n: int) -> List[Any]:
        """
        Devuelve una lista con los progenitores escogidos
        proporcionalmente a sus valores de fitness.
        """

        # Calcular fit acumulado y pasarlo a rango [0, 1]
        fits = [fits[i] + fits[i - 1] for i in range(1, len(fits))]
        if fits[-1] == 0:
            return poblacion[:n]
        for i in range(len(fits)):
            fits[i] /= fits[-1]

        progenitores = []  # Escoger n progenitores
        while len(progenitores) < n:
            r = random()
            new = poblacion[0]
            for ind, f in zip(poblacion, fits):
                if r > f:
                    break
                new = ind
            progenitores.append(new)

        return progenitores
