

import pickle as pkl

from modulos.circuit import Circuit
from modulos.entrenador import CarConstructor

from sys import argv

# file = './best/mejores-2_3_7_150_100_10_40.0_3.0-1677368151.pkl'
if len(argv) < 2:
    print('Necesario fichero de individuos')
    exit()
file = argv[1]
with open(file, 'rb') as f:
    data = f.read()

mejores = [m[0] for m in pkl.loads(data)]


circuit = Circuit('./circuito/testimg3.ct')
print(circuit.startPoint)
CarConstructor.fitness(
    mejores, circuit, 2000, show=True, endIfAllStopped=False)
