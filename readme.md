

# AutoCars

Probado con python desde 3.6.4 hasta 3.10.9

Requiere las bibliotecas:
- pygame
- numpy
- pickle
- matplotlib

En algunos equipos será necesario usar el comando 
```export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6```
para solucionar el error
```libGL error: MESA-LOADER: failed to open iris```

```
python -m pip install pygame
python -m pip install numpy
python -m pip install pickle
python -m pip install matplotlib
```

## Pruebas

Entrenamiento:
```
python .\train.py
```

Test:
```
python .\test.py .\best\mejores-1681299667-1layers-97.5.pkl
```

Perfilado:
```
python -m cProfile -o testprofile.txt .\train.py
```
y para ver los resultados:
```
python .\showprofile.py
```

## Estructura de modulos

### Modulos

constants: variables generales

geometry: modulo de geometria, con puntos, lineas y formas
- constants

circuit: modulo del circuito, background, lectura y escritura en fichero
- constants
- geometry

neuralnetwork: modulo que implementa el funcionamiento de las redes neuronales, su mutación y su cruce

car: 
- constants
- geometry
- neuralnetwork
- circuit

entrenador: modulo que implementa la clase de entrenamiento de individuos
- constants
- circuit
- car


### Main

circuit_builder: main con el bucle principal de construccion de circuitos
- constants
- geometry
- circuit

train: main que entrena individuos y guarda el mejor
- circuit
- entrenador

test: main que usa individuos guardados
- circuit
- entrenador
