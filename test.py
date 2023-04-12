

import pickle as pkl

from modulos.circuit import Circuit
from modulos.entrenador import CarConstructor

from sys import argv

if len(argv) < 2:
    print('Necesario fichero de individuos')
    exit()
file = argv[1]
with open(file, 'rb') as f:
    data = f.read()

mejores = [m[0] for m in pkl.loads(data)]


circuit = Circuit('./circuito/test1.ct')
print(circuit.startPoint)
CarConstructor.fitness(
    mejores, circuit, 2000, show=True, endIfAllStopped=False)
