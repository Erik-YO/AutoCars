

import matplotlib.pyplot as plt
import pickle as pkl
from time import time
from sys import argv

from modulos.circuit import Circuit
from modulos.entrenador import Entrenador, CarConstructor


mejores = None
if len(argv) > 1:
    with open(argv[-1], 'rb') as f:
        data = f.read()

    mejores = [m[0] for m in pkl.loads(data)]


circuit = Circuit('./circuito/train1.ct')

minL = 1
maxL = 2
layersSize = 10

popSize = 250
maxGens = 60
nIterNoChng = 10
probCruce = 0.2
probMutac = 0.09

cc = CarConstructor(circuit.startPoint.asTuple(), minL, maxL, layersSize)
p = Entrenador(
    cc, popSize, maxGens, nIterNoChng, probCruce, probMutac, renovacion=0.2)

try:
    p.train(circuit, mejores)
except KeyboardInterrupt:
    pass

filename = ''.join((
    './best/mejores',
    f'-{round(time())}',
    f'-{len(p.individuo.brain.pesos)}layers' if p.individuo else '',
    f'-{round(p.list_fit_best[-1], 2)}' if len(p.list_fit_best) else '',
    '.pkl'))

data = pkl.dumps(p.mejores)

with open(filename, 'wb') as f:
    f.write(data)


generaciones = [i for i in range(len(p.list_fit_best))]

plt.figure(filename)
# Impresion de graficas
plt.plot(generaciones, p.list_fit_best, label='best')
plt.plot(generaciones, p.list_fit_med, label='media')

plt.xlabel('Generacion')
plt.ylabel('Fit')
plt.title('Evolucion del fit por generacion')
plt.show()

"""filename = './best/mejores-' + '_'.join([str(e) for e in [
    minL,
    maxL,
    layersSize,

    popSize,
    maxGens,
    nIterNoChng,
    int(probCruce*100),
    int(probMutac*100),
    ]]) + f'-{round(time())}' + '.pkl'"""
