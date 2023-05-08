

# AutoCars

https://github.com/Erik-YO/AutoCars

Probado con python desde 3.6.4 hasta 3.10.9

Requiere las bibliotecas:
- pygame
- numpy
- pickle
- matplotlib

```
python -m pip install pygame
python -m pip install numpy
python -m pip install pickle
python -m pip install matplotlib
```

En algunos equipos será necesario usar el comando:  
```export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6```  
para solucionar el error:  
```libGL error: MESA-LOADER: failed to open iris```

## Pruebas

Entrenamiento:
```
python .\train.py
```

Test:
```
python .\test.py .\best\mejores-1681326062-1layers-13.58.pkl
```

Perfilado:
```
python -m cProfile -o testprofile.txt .\train.py
```
y para ver los resultados:
```
python .\showprofile.py
```

## Estructura de los módulos

Formato:

nombre_del_modulo: descripción del módulo
- dependencia_1
- dependencia_2
- ...

### Módulos

constants: variables generales

geometry: módulo de geometria, con puntos, lineas y formas
- constants

circuit: módulo del circuito, background, lectura y escritura en fichero
- constants
- geometry

neuralnetwork: módulo que implementa el funcionamiento de las redes neuronales, su mutación y su cruce

car: módulo que implementa el comportamiento de los individuos
- constants
- geometry
- neuralnetwork
- circuit

entrenador: módulo que implementa la clase de entrenamiento de individuos
- constants
- circuit
- car


### Main

circuit_builder: ejecutable con el bucle principal de construccion de circuitos
- constants
- geometry
- circuit

train: ejecutable que entrena individuos y guarda el mejor, aquí se definen los hiperparámetros de entrenamiento
- circuit
- entrenador

test: ejecutable que usa individuos guardados
- circuit
- entrenador
