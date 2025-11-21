# Práctica 1 - Juego de coordinación multi-acción (JCMA)

## Introducción

En esta práctica trabajaremos con un juego estático y simétrico en estrategias, donde dos jugadores eligen simultáneamente un número entero en el conjunto $S = \{0,1,2,3,4,5\}$. Si la suma de ambas elecciones no supera un umbral (5), cada jugador obtiene exactamente lo que ha pedido; si lo supera, ambos reciben 0. Este juego presenta múltiples equilibrios puros que maximizan el bienestar social, pero con distintos grados de equidad entre jugadores. Las estrategias son simétricas, en el sentido de que ambos jugadores comparten el mismo conjunto de acciones. Los resultados cuya suma es 5 son eficientes (maximizan la suma de pagos), pero reparten beneficios de forma desigual.

Más abajo encontrarás su definición formal y su matriz de pagos en forma normal, que usaremos como base para el análisis y la implementación.

## Descripción de la práctica

**¡Importante!** Revisa el juego de [Nicky Case](https://ncase.me/trust/) llamado *The Evolution of Trust* (~30min). Aunque originalmente sobre el Dilema del Prisionero Iterado (DPI), sus conceptos sobre cooperación, estrategias reactivas y dinámicas evolutivas son directamente aplicables a nuestro juego de suma limitada iterado. 

En nuestro caso, el juego es simultáneo y repetido: en cada ronda, los jugadores eligen acciones sin conocer la del rival, pero con acceso al historial completo de interacciones pasadas. Esto introduce complejidades como coordinación implícita, retaliación y evolución de normas sociales, haciendo de este juego un "dilema más complejo" que el DPI clásico (más acciones, umbral de suma, y payoffs asimétricos en equidad).

La práctica tiene dos partes:
 - Parte 1: Montar la estructura computacional que permita simular torneos del juego de suma limitada iterado.
 - Parte 2: Diseñar una estrategia para un torneo de tres fases (enfrentamiento directo, evolutivo, y en ecosistema ampliado).

 ## Definición formal del JCMA

- Jugadores: P1, P2.
- Acciones posibles: $S = \{0,1,2,3,4,5\}$.
- Funciones de pago: sea $i$ la acción escogida por el jugador P1 y $j$ la acción escogida por el jugador P2, se define $u_1$ y $u_2$ como los pagos que obtiene el jugador P1 y P2 respectivamente:

$$
 u_1(i,j)=\begin{cases}
 i, & \text{si } i+j\le 5,\\
 0, & \text{si } i+j>5,
 \end{cases}
 \qquad
 u_2(i,j)=\begin{cases}
 j, & \text{si } i+j\le 5,\\
 0, & \text{si } i+j>5.
 \end{cases}
$$

Es decir cada jugador obtiene *"lo que pide"*, a no ser que la suma de lo que todos piden sea mayor que 5, en cuyo caso nadie gana nada.

## Matriz de pagos

Por filas la acción del jugador P1, por columnas la acción del jugador P2.

<center>

|   i\j |     0 |     1 |     2 |     3 |         4 |         5 |
| ----: | ----: | ----: | ----: | ----: | --------: | --------: |
| **0** | (0,0) | (0,1) | (0,2) | (0,3) |   (0,4)   |   (0,5)   |
| **1** | (1,0) | (1,1) | (1,2) | (1,3) |   (1,4)   |   (0,0)   |
| **2** | (2,0) | (2,1) | (2,2) | (2,3) |   (0,0)   |   (0,0)   |
| **3** | (3,0) | (3,1) | (3,2) | (0,0) |   (0,0)   |   (0,0)   |
| **4** | (4,0) | (4,1) | (0,0) | (0,0) |   (0,0)   |   (0,0)   |
| **5** | (5,0) | (0,0) | (0,0) | (0,0) |   (0,0)   |   (0,0)   |


</center>

## Parte 1: Software para el estudio del JCMA

El primer objetivo es crear un software que permita simular torneos del juego definido arriba en las versiones "enfrentamiento directo" y  "evolutiva".

Requisitos mínimos:

- Programado en Python >3.8, utilizando programación orientada a objetos (OOP).
- Entradas para el torneo de enfrentamiento directo:
  - `all_players`: lista o tupla de jugadores participantes (con su estrategia).
  - `game`: objeto que define el juego (conjunto de acciones S={0..5}, umbral T=5 y función de pagos u1,u2).
  - `repetitions`: número de veces que una estrategia se enfrenta a otra.
  - `noise` (opcional): probabilidad de ejecución errónea de la acción elegida.
- Salidas: información (visual) del resultado del campeonato (ranking y puntuaciones agregadas).
- Incluir al menos estrategias básicas: `AlwaysK` para K∈{0,1,2,3,4,5} y `UniformRandom`. Debe ser sencillo añadir nuevas estrategias.

Estructura de proyecto recomendada (solo si piensas trabajar en local, si usas este notebook como lugar de trabajo, ignórala):

```
.
└── limited_sum/
    ├── limited_sum/
    │   ├── __init__.py
    │   ├── game.py        # define S, T y la función de pagos u1,u2
    │   ├── player.py      # clase base Player y estrategias básicas (AlwaysK, Random)
    │   ├── match.py       # partida one-shot entre dos jugadores y registro de payoffs
    │   ├── tournament.py  # lógica del torneo todos-contra-todos
    │   └── evolution.py   # dinámica evolutiva
    ├── main.py
    └── ...
```

## Parte 2: diseño de una estrategia

A continuación deberás implementar una estrategia que se enfrentará a las de tus compañeros en un torneo del JCMA.

Los juegos contra tus rivales tendrán un final **no determinista**. Esto quiere decir que el número de rondas que se van a jugar no se sabe con precisión. En lugar de eso, después de cada ronda, la partida tiene una cierta probabilidad de acabar (pequeña). ¿Por qué haremos esto? En juegos iterados con duración finita conocida, la proximidad del final juega un papel crucial en las decisiones estratégicas (e.g., incentivos a desertar en las últimas rondas).

Con el objetivo de dejar esta complejidad adicional fuera, jugaremos un número de rondas aleatorio: puedes pensar que tu estrategia va a jugar "muchas veces" contra cada rival. **En media, se jugarán 100 rondas** (puedes quedarte con ese número). Los puntos obtenidos en cada interacción se normalizarán por el número de rondas jugadas para evitar sesgos por duración variable.

# Para ejecutar tests
```python
python -m unittest discover -s tests -v
```

# Problemas con ficheros grandes
Debido a que los ficheros que resultan de ejecutar evoluciones grandes tienen mucho peso, se ha usado lfs (Github large file storage) para almacenarlos.
Si se está usando la terminal para actualizar el proyecto, es probable que no aparezca la ayuda de github para sincronizar el proyecto con lfs.
En ese caso ficheros como *best_models_for_tournament_type.csv* pueden aparecer de la siguiente manera

```bash
version https://git-lfs.github.com/spec/v1
oid sha256:xxxxxx
size 123456
```
Esto significa que Git LFS no está instalado o no se han descargado los ficheros reales.
**Cómo solucionarlo**
### 1. Instalar Git LFS 
Ubuntu / Debian
```bash
sudo apt update
sudo apt install git-lfs

```
Windows

1. Descargar el instalador oficial desde: https://git-lfs.com
2. Ejecutarlo y seguir los pasos (instala git-lfs.exe automáticamente).
2. Inicializar LFS en tu repositorio
### 2.Inicial LFS en el repositorio
(Sólo hace falta una vez por repositorio)
```bash
git lfs install
```

### 3. Descargar los ficheros reales
```bash
git pull

```
