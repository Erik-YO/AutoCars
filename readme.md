
# AutoCars

https://github.com/Erik-YO/AutoCars

## Introducción

Proyecto usado como trabajo final de la asignatura NEUROCOMPUTACIÓN (2023).  
El problema planteado es el entrenamiento de una red neuronal para que conduzca un coche a
través de un circuito de 2 dimensiones sin chocarse con los bordes.  
A pesar de la hipótesis inicial de la lentitud de los algoritmos genéticos para este tipo
de problemas (con gran cantidad de datos por individuo) decidimos probar este método por las siguientes razones:
- Al ser un problema de aprendizaje no supervisado, no hay un dataset con entradas y resultados esperados. Por lo que un modelo de entrenamiento tradicional como el descenso por gradiente no es facilmente aplicable.
- Los resultados de un par entrada-salida pueden tardar más iteraciones _frames_ en reflejarse. Es decir, que en un momento dado el coche decida continuar hacia delante y no se choque inmediatamente no significa que no vaya a hacerlo en el siguiente _frame_.
- Para ofrecer un método de entrenamiento alternativo a los vistos en la asignatura.

## Requisitos
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



## Conclusiones

Vemos que el problema es linealmente separable, porque se puede solucionar con redes de una sola capa.
También hemos visto que el algoritmo es computacionalmente costoso, principalmente porque trabaja en gran
medida con valores aleatorios. Por esto mismo, no se recomienda usar algoritmos genéticos con redes mucho mayores
(a partir de 4 capas).
Finalmente apuntar que este tipo de algoritmos es muy útil cuando tratamos con
problemas de aprendizaje no supervisado que requieren una flexibilidad que no
ofrecen otros algoritmos.

