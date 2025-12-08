<a id="readme-top"></a>
<div align="center">
  <h1 align="center">🧠 Prácticas de Optimización Exacta y Aproximada</h1>

  [![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![Dependency Manager](https://img.shields.io/badge/uv-astral-purple?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
  [![Code Style Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
  [![Imports isort](https://img.shields.io/badge/Imports-isort-blue)](https://pycqa.github.io/isort/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Status](https://img.shields.io/badge/Status-En_Desarrollo-orange)]()

  <p align="center">
    <br />
    <strong>Máster en Aprendizaje Automático y Datos Masivos</strong>
    <br />
    <br />
    <a href="#estructura-del-proyecto">Estructura</a> •
    <a href="#p1">Práctica 1</a> •
    <a href="#p2">Práctica 2</a> •
    <a href="#p3">Práctica 3</a> •
    <a href="#autores">Autores</a> •
    <a href="#licencia">Licencia</a>
  </p>

</div>

<a id="estructura-del-proyecto"></a>
# 📁 Estructura del proyecto

```
.
└── limited_sum/            # Módulo con la implementación de la P1
  │  ├── __init__.py
  │  ├── game.py            # Define S, T y la función de pagos u1,u2
  │  ├── player.py          # Clase base Player e implementaciones de estrategias
  │  ├── match.py           # Partida entre dos jugadores y registro de payoffs
  │  ├── tournament.py      # Lógica del torneo todos-contra-todos
  │  ├── evolution.py       # Dinámica evolutiva
  │  ├── championship.py    # Campeonato compuesto de 3 fases
  │  └── chosen_player.py   # Implementación del jugador para el torneo de clase
└── discarded/              # Directorio con ideas y evolutivos descartados durante la práctica
  │  └── ...
  ├── README.md             # Contiene la explicación del repositorio
  ├── P1_main.py            # Enseña el uso de las clases definidas en la P1
  ├── P1_championship.py    # Entorno de pruebas del campeonato
  ├── P2_enunciado.ipynb    # Enunciado e implementación de la P2
  ├── P2_nelder_mead.pdf    # Explicación del algoritmo del ejercicio 6 de la P2
  ├── P2_nelder_mead.py     # Diseño de las clases del ejercicio 6 de la P2
  ├── P2_nelder_mead.ipynb  # Implementación de ejemplo del ejercicio 6 de la P2
  ├── P3_enunciado.ipynb    # Enunciado e implementación de la P3
  └── ...                   # Resto de ficheros no evaluables

```

<a id="empezando"></a>
# 🔥 Empezando

Sigue estos pasos para levantar el entorno de desarrollo localmente.

### Requisitos previos

Este proyecto ha sido desarrollado usando **Python (>3.11)**.

> [!IMPORTANT]
> Para la gestión de dependencias y entornos virtuales se utiliza **[uv](https://docs.astral.sh/uv/)**, un gestor de paquetes extremadamente rápido escrito en Rust.
> 
> Si no dispones de `uv`, instálalo ejecutando:
> ```bash
> # En macOS/Linux
> curl -LsSf https://astral.sh/uv/install.sh | sh
>
> # En Windows
> powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```

### Instalación

Una vez instalado `uv`, la configuración es automática. Desde la raíz del repositorio:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/yabol02/practica_biocomp.git
   ```

2. Sincroniza el entorno:
    ```bash
    uv sync
    ```
    Este comando creará el virtual environment (`.venv`) e instalará todas las librerías exactas definidas en el `uv.lock`.


<p align="right">(<a href="#readme-top">Volver arriba</a>)</p>

<a id="p1"></a>
# 🫱🏼‍🫲🏼 Práctica 1 - Juego de coordinación multi-acción (JCMA)

## Introducción

En esta práctica se trabaja un juego estático y simétrico en estrategias, donde dos jugadores eligen simultáneamente un número entero en el conjunto $S = \{0,1,2,3,4,5\}$. Si la suma de ambas elecciones no supera un umbral ($5$), cada jugador obtiene exactamente lo que ha pedido; si lo supera, ambos reciben $0$. Este juego presenta múltiples equilibrios puros que maximizan el bienestar social, pero con distintos grados de equidad entre jugadores. Las estrategias son simétricas, en el sentido de que ambos jugadores comparten el mismo conjunto de acciones. Los resultados cuya suma es 5 son eficientes (maximizan la suma de pagos), pero reparten beneficios de forma desigual.

## Descripción de la práctica

> [!IMPORTANT] 
> La implementación está basada en el juego de [Nicky Case](https://ncase.me/trust/) llamado *The Evolution of Trust* (~30min). Aunque originalmente sobre el **Dilema del Prisionero Iterado (DPI)**, sus conceptos sobre cooperación, estrategias reactivas y dinámicas evolutivas son directamente aplicables al juego de suma limitada iterado. 

En este caso, el juego es simultáneo y repetido: en cada ronda, los jugadores eligen acciones sin conocer la del rival, pero con acceso al historial completo de interacciones pasadas. Esto introduce complejidades como *coordinación implícita*, *retaliación* y *evolución de normas sociales*, haciendo de este juego un "dilema más complejo" que el DPI clásico (más acciones, umbral de suma, y payoffs asimétricos en equidad).

## Definición formal del JCMA

- Jugadores: P1, P2.
- Acciones posibles: $S = \{0,1,2,3,4,5\}$.
- Funciones de pago: sea $i$ la acción escogida por el jugador P1 y $j$ la acción escogida por el jugador P2, se define $u_1$ y $u_2$ como los pagos que obtiene el jugador P1 y P2 respectivamente:

$$
 u_1(i,j)=\ 
  \begin{cases}
    i, & \text{si } i+j \le 5,\\
    0, & \text{si } i+j>5,
 \end{cases}
 \qquad
 u_2(i,j)=\ 
  \begin{cases}
    j, & \text{si } i+j\le 5,\\
    0, & \text{si } i+j>5.
 \end{cases}
$$

Es decir, cada jugador obtiene *"lo que pide"*, a no ser que la suma de lo que todos piden sea mayor que 5, en cuyo caso nadie gana nada.

## Matriz de pagos

Por filas la acción del jugador P1, por columnas la acción del jugador P2. La celda resultado es la puntuación al final de cada ronda, donde el primer valor corresponde al P1 y el segundo al P2.

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

## Software para el estudio del JCMA

El programa se compone de múltiples clases:

### `Game`
La clase `Game` encapsula la definición formal del juego de suma limitada. Representa el entorno en el que interactúan los jugadores y ofrece los métodos necesarios para calcular pagos y validar acciones. Su función central es generar la matriz de pagos y evaluar los resultados de cada emparejamiento entre acciones. Se compone de varios elementos:
- Atributo `actions`: define el conjunto de acciones disponibles para los jugadores. Por defecto coincide con el conjunto del juego.
- Atributo `threshold`: establece el umbral máximo permitido para la suma de las acciones. Si la suma supera este valor, ambos jugadores reciben cero. Este valor controla por tanto la dureza del juego, el grado de penalización por falta de coordinación y los puntos de equilibrio.
- Propiedad `payoff_matrix`: construye de forma programática la matriz de pagos del juego. Para cada par de acciones verifica si la suma está por debajo del umbral. Si es así asigna a cada jugador el valor de su acción, mientras que si lo supera asigna cero a ambos.
- Método `evaluate_result`: recibe dos acciones y devuelve el pago exacto obteniendo directamente el resultado de la matriz construida. Garantiza así un cálculo consistente y evita duplicar lógica en otras partes del programa.

### `Player`
La clase `Player` define la estructura básica de cualquier jugador del juego de suma limitada. Es una clase abstracta que establece la interfaz común que deberán implementar todas las estrategias. Su papel es proporcionar el comportamiento esencial que todos los jugadores comparten y dejar a cada subclase la responsabilidad de decidir cómo actúa en cada ronda. Sus elementos son:
- Atributo `game`: vincula al jugador con las reglas del entorno en el que va a operar. 
- Atributo `name`: permite etiquetar la estrategia para interpretaciones posteriores, análisis de torneos y depuración.
- Atributo `history`: historial de acciones propio que registra todas sus decisiones a lo largo de la partida. Este historial sirve como memoria para las estrategias reactivas, que ajustan su comportamiento en función de cómo actúa el oponente.
- Método `strategy`: corazón de cada jugador. Debe ser implementado obligatoriamente por todas las subclases y devuelve la acción escogida para la siguiente ronda. La decisión puede basarse únicamente en la propia lógica interna de la estrategia o en la observación del historial del adversario, lo que permite modelar comportamientos como cooperación condicional, represalias o patrones adaptativos.
- Método `compute_scores`: calcula las puntuaciones acumuladas de una partida completa entre dos jugadores. Recorre ambas secuencias de acciones y aplica la función de pagos del juego a cada ronda, devolviendo los resultados totales.
- Método `clean_history`: permite reiniciar el estado del jugador al comenzar una nueva partida.

### `Match`
La clase `Match` modela una partida iterada entre dos jugadores dentro del juego de suma limitada. Su objetivo es coordinar el proceso de interacción ronda a ronda, registrar las acciones elegidas por cada jugador y calcular la puntuación final. Una instancia de esta clase representa una única partida entre dos estrategias concretas.
- Atributos `player_1` y `player_2`: jugadores que se enfrentarán entre si. 
- Atributo `stop_prob`: probabilidad de que la partida termine después de cada ronda, para introducir incertidumbre en la duración de cada enfrentamiento.
- Atributo `max_rounds`: establece un límite máximo de rondas para evitar partidas demasiado largas y asegura que la simulación siempre concluya.
- Atributo `error`: introduce una probabilidad de que el jugador ejecute una acción distinta a la planificada, lo que permite modelar fallos aleatorios en la estrategia.
- Método `play`: contiene la lógica principal de la clase, ejecutando la partida completa. Cada iteración representa una ronda en la que ambos jugadores seleccionan una acción mediante su método de estrategia. El juego calcula los pagos de la ronda, actualiza los historiales y acumula las puntuaciones. Al finalizar, el método almacena el resultado medio para cada jugador en un nuevo atributo `score`. Admite un argumento para mostrar por pantalla las rondas con sus acciones y pagos correspondientes. Admite otro argumento opcional un registro completo con toda la información relevante de la partida.

### `Tournament`
La clase `Tournament` organiza una competición todos contra todos entre un conjunto de estrategias. Cada jugador se enfrenta a todos los demás en varias partidas independientes y el torneo acumula los resultados obtenidos por cada participante. Su objetivo principal es evaluar el rendimiento relativo de las estrategias en un entorno donde cada una interactúa con todas las demás.
- Atributo `players`: colección de jugadores que participan en el torneo.
- Atributo `stop_prob`: probabilidad de que la partida termine después de cada ronda.
- Atributo `max_rounds`: número máximo de rondas.
- Atributo `error`: probabilidad de que el jugador ejecute una acción distinta a la planificada.
- Atributo `repetitions`: indica cuántas veces debe repetirse cada emparejamiento, lo que reduce la variabilidad estadística al calcular los resultados agregados.
- Método `play`: ejecuta el torneo completo. Para cada par de jugadores crea una instancia de la clase `Match` y la simula tantas veces como indique el parámetro de repeticiones. Cada resultado contribuye a la puntuación acumulada en el atributo `ranking`, el cual almacena los puntos de todos los jugadores durante el desarrollo del torneo. Este método también permite mostrar información detallada de las partidas mientras se ejecutan, lo que facilita la depuración y el análisis del comportamiento de cada estrategia. Admite otro argumento opcional para guardar la información detallada de todas las partidas.
- Método `plot_results`: genera un gráfico de barras con la clasificación final. Presenta el nombre de cada jugador y la puntuación total obtenida, lo que permite comparar visualmente el rendimiento de todas las estrategias.

### `Evolution`
La clase `Evolution` extiende la lógica de los torneos iterados para simular un proceso evolutivo completo. Cada estrategia está representada por múltiples individuos y, generación tras generación, las poblaciones cambian en función del rendimiento de cada jugador. Se trata de un modelo inspirado en la selección natural, donde las estrategias más eficaces tienden a reproducirse mientras que las menos exitosas desaparecen progresivamente.
- Atributo `players`: tupla con los jugadores.
- Atributo `stop_prob`: probabilidad de terminar la partida en cada ronda.
- Atributo `max_rounds`: número máximo de rondas por partida.
- Atributo `error`: probabilidad de fallo en cada ronda.
- Atributo `repetitions`: número de veces que se repite cada partida.
- Atributo `generations`: fija cuántas generaciones se simularán.
- Atributo `reproductivity`: determina qué fracción de la población será reemplazada en cada ciclo por copias de los jugadores con mayor puntuación.
- Atributo `initial_population`: indica el número total de individuos o la distribución exacta de individuos por jugador y define el tamaño inicial de la población.
- Método `natural_selection`: ejecuta el mecanismo de selección natural después de cada torneo generacional. Clasifica a todos los individuos según la puntuación obtenida, elimina a los que ocupan las posiciones más bajas y crea descendencia a partir de los jugadores mejor posicionados. Los nuevos individuos son copias limpias de los progenitores y forman una población renovada para la siguiente generación.
- Método `count_strategies`: resume la composición de la población contando cuántos individuos de cada estrategia permanecen vivos en un instante determinado. Este recuento es esencial para seguir la evolución de las poblaciones a lo largo del proceso.
- Método `play`: simula el proceso evolutivo completo. En cada generación se crea un torneo donde todos los individuos interactúan entre sí y, tras acumularse las puntuaciones, se aplica la selección natural que determina la siguiente población. Este método registra la evolución de cada estrategia, permite imprimir resultados intermedios y puede generar un gráfico que muestra la dinámica poblacional durante todas las generaciones. Admite también un argumento opcional para devolver el historial completo con todas las partidas disputadas.
- Método `stackplot`: genera un gráfico que muestra la evolución temporal de cada estrategia dentro de la población. Representa claramente qué tipos aumentan, disminuyen o se extinguen a medida que avanza el proceso evolutivo. 

### `Championship`
La clase `Championship` organiza una competición estructurada en tres fases distintas y asigna puntos en cada una de ellas para determinar una clasificación final. Cada fase utiliza un sistema de evaluación propio y el campeonato combina distintas dinámicas de interacción para medir el desempeño de las estrategias de manera más completa. La 1ª fase corresponde a un `Tournament` entre todos los jugadores. La 2ª es una `Evolution` con una característica adicional: ahora la forma de reproducción en cada ronda es proporcional a la cantidad de puntos obtenida durante toda la generación por los individuos de una clase. La 3ª fase se corresponde de nuevo a este tipo de `Evolution` pero añadiendo más agentes para darle mayor variabilidad a todo el juego y que existan, por ejemplo, estrategias sencillas de explotar. Estos jugadores se corresponden a: *Always0*, *Always3*, *UniformRandom*, *Focal5*, *TitForTat*, *CastigadorInfernal*. Cada uno de los agentes recibirá una cantidad de puntos en cada fase en función de su rendimiento. Ganará el que, al final del torneo, tenga una mayor cantidad de puntos.
- Atributo `players`: tiene que ser una tupla con todos los jugadores. 
- Atributo `max_rounds`: marca el máximo número de rondas por enfrentamiento.
- Atributo `stop_prob`: es la probabilidad de terminar cada partida.
- Atributo `error`: corresponde a la probabilidad de cambiar la acción del jugador. 
- Atributo `repetitions`: es el número de veces que se repite cada enfrentamiento.
- Atributo `generations`: fija el número de generaciones de las evoluciones del campeonato
- Atributo `initial_population`: es exactamente igual que en `Evolution`.
- Método `play`: coordina la ejecución completa del campeonato. Llama secuencialmente a las tres fases, imprime la clasificación intermedia si el usuario lo solicita y finalmente muestra el podio con el resultado final. Las puntuaciones obtenidas en cada una de las fases son:
<div align="center">

  | Posición | 1ª Fase | 2ª Fase | 3ª Fase |
  |---------|---------|---------|---------|
  | 1º      | 24      | 24      | 12      |
  | 2º      | 17      | 17      | 8       |
  | 3º      | 12      | 12      | 4       |
  | 4º      | 8       | —       | —       |
  | 5º      | 4       | —       | —       |
  | 6º      | 4       | —       | —       |

</div>

## Ejecución del código
La P1 tiene varios ficheros de ejecución:

### Código principal
En el fichero [P1_main.py](P1_main.py) está la lógica completa de la práctica y sirve para probar todas las clases vistas en el apartado anterior: una partida (`Match`), un torneo (`Tournament`), una evolución (`Evolution`) y un campeonato (`Championship`). El objetivo de este fichero es mostrar el buen funcionamiento del código. Para ejecutar este fichero, hay que realizar:

```bash
py .\P1_main.py
```

### Campeonato largo y resultados
Para hacer las distintas pruebas sobre el campeonato está el fichero [P1_championship.py](P1_championship.py). Para ejecutarlo correctamente, hace falta indicar la ruta donde guardar los resultados, por ejemplo:

```bash
py .\P1_championship.py ".\results\championship"
```

Este fichero almacena los resultados en crudo en ficheros *Parquet*, los cuales se pueden procesasr con el Notebook [analysis.ipynb](./notebooks/analysis.ipynb). Este Notebook lee los datos y los procesa para analizar los resultados y así poder elegir la mejor estrategia para el juego.

<a id="p2"></a>
# 📈 Práctica 2 - Métodos de optimización de funciones
La P2 se compone de varios ficheros. El primero y más importante es [P2_enunciado.ipynb](P2_enunciado.ipynb), que contiene la solución de los ejercicios de optimización con restricciones. Dado que el ejercicio 6 consiste en describir un algorimto de optimización, se ha separado todo su desarrollo y explicación en varios ficheros adicionales:
- [P2_nelder_mead.pdf](P2_nelder_mead.pdf): contiene la explicación paso a paso del algoritmo en una carilla A4.
- [P2_nelder_mead.py](P2_nelder_mead.py): contiene el código del algoritmo. Este fichero se puede ejecutar para ver cómo optimiza diversas funciones: [Rosenbrock](https://es.wikipedia.org/wiki/Funci%C3%B3n_de_Rosenbrock), [Sphere de N dimensiones](https://es.wikipedia.org/wiki/N-esfera) y la función [Himmelblau](https://es.wikipedia.org/wiki/Funci%C3%B3n_de_Himmelblau). Muestra tanto el resultado final como el paso a paso (de las funciones donde exista la posibilidad).
- [P2_nelder_mead.ipynb](P2_nelder_mead.ipynb): notebook con distintas funciones típicas a optimizar, la explicación del algoritmo y la posibilidad de emplear el código anterior para optimizar las funciones.

<p align="right">(<a href="#readme-top">Volver arriba</a>)</p>

<a id="p3"></a>
# 🧠 Práctica 3 - Redes Neuronales Artificiales desde 0
La P3 se corresponde a un único Notebook ([P3_enunciado.ipynb](P3_enunciado.ipynb)) con la creación paso a paso de un [perceptrón multicapa](https://es.wikipedia.org/wiki/Perceptr%C3%B3n). 

<p align="right">(<a href="#readme-top">Volver arriba</a>)</p>

# ⚠️ Problemas con ficheros grandes
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
### 2. Inicial LFS en el repositorio
(Sólo hace falta una vez por repositorio)
```bash
git lfs install
```

### 3. Descargar los ficheros reales
```bash
git pull
```

<a id="autores"></a>
## 🫂 Autores

<a href="https://github.com/yabol02/oeya_p1/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yabol02/oeya_p1" />
</a>

###### Made with [contrib.rocks](https://contrib.rocks).

- [Aguirregabiria Herrero, Rodrigo](https://github.com/raguirregabiria)
- [Boleas Francisco, Yago](https://github.com/yabol02)
- [Estoquera Núñez, Adrian](https://github.com/aestoquera)

<p align="right">(<a href="#readme-top">Volver arriba</a>)</p>

<a id="licencia"></a>
## 🗝️ Licencia

Distribuido bajo la licencia MIT. Ve a [`LICENSE`](LICENSE) para mayor información.

<p align="right">(<a href="#readme-top">Volver arriba</a>)</p>

<a href="https://www.etsisi.upm.es/">
  <img src="https://www.upm.es/gsfs/SFS11386"></img>
</a>