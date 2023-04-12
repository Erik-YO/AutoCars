
from typing import List, Tuple, Union
from random import randint
import numpy as np


class NeuralNetwork():

    activacionBipolar = True
    espacioPesos = (-2, 2)
    normalizarInputs = True

    pesos: List[np.ndarray]

    def __init__(
            self, ninputs: int, noutputs: int,
            layers: int, layersize: int,
            isCopy: bool = False) -> None:
        '''
        Todos los argumentos pueden ser None si se trata de una copia
        - nimputs: tamano de la capa de entrada
        - noutputs: tamano de la capa de salida
        - layers: numero de capas (incluye la de salida y las ocultas,
            no la de entrada)
        - layersize: numero de neuronas de las capas ocultas (mismo numero
            de neuronas para todas)
        '''

        self.pesos = []

        if not isCopy:
            self.init(ninputs, noutputs, layers, layersize)

    def init(
            self, ninputs: int, noutputs: int,
            layers: int, layersize: int):

        if layers < 1:
            raise Exception(f'layers debe ser al menos 1, no {layers}')
        if layersize < 1:
            raise Exception(f'layersize debe ser al menos 1, no {layersize}')

        if layers == 1:
            self.pesos.append(NeuralNetwork.randomToEspacioPesos(
                np.random.random((ninputs, noutputs))))

        else:
            self.pesos.append(NeuralNetwork.randomToEspacioPesos(
                np.random.random((ninputs, layersize))))
            while len(self.pesos) < layers - 1:
                self.pesos.append(NeuralNetwork.randomToEspacioPesos(
                        np.random.random((layersize, layersize))))
            self.pesos.append(NeuralNetwork.randomToEspacioPesos(
                np.random.random((layersize, noutputs))))

    def process(self, inputs: np.ndarray) -> np.ndarray:
        '''
        La funcion de activacion por defecto es:
         - Bipolar f(x) = 1 si x >= 0, -1 si x < 0
         - Binaria f(x) = 1 si x >= 0,  0 si x < 0
        '''

        ish, psh = inputs.shape[0], self.pesos[0].shape[0]
        if ish != psh:
            raise Exception(f'Input size != first layer size ({ish} != {psh})')

        if NeuralNetwork.normalizarInputs:
            inputs = inputs / np.linalg.norm(inputs)

        for _, layer in enumerate(self.pesos):
            output = np.zeros((layer.shape[1]), dtype=float)
            for i, comp in enumerate(layer.T):
                temp = comp * inputs
                output[i] += np.sum(temp)
            inputs = np.where(
                output > 0, 1,
                # Funcion de activacion
                -1 if NeuralNetwork.activacionBipolar else 0)

        # input(inputs)
        output = inputs > 0

        return output

    def mutate(self, mrate: float) -> 'NeuralNetwork':
        '''
        Muta inplace
        mrate: proporcion de pesos que mutan.
        Return: self
        '''

        i = 0
        while i < len(self.pesos):
            layer = self.pesos[i]
            choice = np.random.random(layer.shape)
            variacion = NeuralNetwork.randomToEspacioPesos(
                np.random.random(layer.shape))

            self.pesos[i] = np.where(choice < mrate, variacion, layer)

            i += 1

        return self

    def cruzar(
            a: 'NeuralNetwork', b: 'NeuralNetwork', inplace: bool = False
            ) -> Tuple['NeuralNetwork', 'NeuralNetwork']:
        '''
        Genera 2 nuevas redes cruzando 2 originales.
        '''

        if not inplace:
            a, b = a.copy(), b.copy()

        if len(a.pesos) > 1 and len(b.pesos) > 1:
            pos = randint(1, min(len(a.pesos), len(b.pesos)) - 1)
            a.pesos, b.pesos = (
                a.pesos[:pos] + b.pesos[pos:],
                b.pesos[:pos] + a.pesos[pos:])

        return a, b

    def copy(self) -> 'NeuralNetwork':

        nn = NeuralNetwork(None, None, None, None, True)
        nn.pesos = [lay.copy() for lay in self.pesos]

        return nn

    def randomToEspacioPesos(
            input: Union[np.ndarray, int, float]
            ) -> Union[np.ndarray, int, float]:
        '''Transforma datos inplace del rango [0, 1] al rango de los pesos'''

        inf, sup = NeuralNetwork.espacioPesos
        input *= (sup - inf)
        input += inf

        return input


if __name__ == '__main__':
    nn = NeuralNetwork(6, 3, 2, 6)

    inp = np.array([23, 34, 80, 3, 40, 26], dtype=float)
    inp = inp / np.linalg.norm(inp)

    out = nn.calculate(inp)
    print(inp)
    print(out)
