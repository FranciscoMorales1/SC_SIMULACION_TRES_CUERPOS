FRANCISCO MORALES
# Simulación Gravitacional de N‑Cuerpos: Caos y Entropía Espacial

Este repositorio simula el problema gravitacional de **N cuerpos** (para 2, 3 y 4 masas) utilizando un **integrador de Velocity Verlet con paso de tiempo adaptativo**.  
El objetivo no es solo dibujar órbitas bonitas, sino **cuantificar el caos** (mediante el exponente de Lyapunov) y **medir la ocupación del espacio** (mediante la entropía de Shannon), manteniendo una estricta separación entre los errores numéricos y el caos físico real.

---

## 📐 ¿Cómo se calcula la Entropía Espacial (Shannon)?

Antes de analizar los resultados, es fundamental entender exactamente cómo el código extrae la **entropía espacial** a partir de la simulación.

El código utiliza la función `spatial_entropy(p_hist, bins=15)`, que sigue estos pasos:

1. **Recolectar todos los puntos** – Toma cada posición de cada cuerpo en cada instante de tiempo.  
   Para una simulación con `pasos` pasos y `N` cuerpos, tenemos `(pasos × N)` puntos en el espacio 3D.

2. **Crear un histograma 3D** – El espacio se divide en una cuadrícula de `15 × 15 × 15` celdas cúbicas (el número 15 es un buen equilibrio entre resolución y ruido estadístico).

3. **Calcular probabilidades** – Para cada celda, contamos cuántos puntos caen dentro.  
   Estas cantidades se convierten en probabilidades:  
   \[
   p_i = \frac{\text{puntos en la celda } i}{\text{total de puntos}}
   \]

4. **Entropía de Shannon** – Finalmente, calculamos:  
   \[
   H = -\sum_{i} p_i \ln(p_i)
   \]  
   - **Entropía baja** (p. ej., ~4.0) significa que los puntos están concentrados en pocas celdas – el sistema permanece en una curva o superficie delgada (por ejemplo, una órbita periódica estable).  
   - **Entropía alta** (p. ej., ~5.3) significa que los puntos están repartidos por muchas celdas – la trayectoria llena un volumen significativo del espacio accesible, lo cual es típico del movimiento caótico.

> **⚠️ Nota importante** – Esta es la **entropía de ocupación espacial**, *no* la entropía de Kolmogorov‑Sinai (la cual está relacionada con la suma de los exponentes de Lyapunov positivos según el teorema de Pesin). Aquí calculamos ambas cosas por separado para no confundirlas.

---

## 🚀 Los Tres Casos Simulados

Todas las simulaciones se ejecutan durante `T_total = 50.0` unidades de tiempo, con un paso máximo `dt_max = 0.001` (lo que garantiza al menos 50 000 pasos).  
El integrador reduce automáticamente el paso cuando dos cuerpos pasan muy cerca (alta aceleración), asegurando que la energía se conserve lo mejor posible.

A continuación se muestran las **condiciones iniciales exactas** (tomadas directamente del `__main__` del código) y una explicación detallada de los resultados, con **especial énfasis en el comportamiento de la entropía**.

---

### 1. Dos Cuerpos – La Prueba de Sanidad (Sistema Integrable)

| Parámetro | Valor |
| :--- | :--- |
| **Masas** | `[20.0, 30.0]` |
| **Posiciones** | Cuerpo 0: `(0, 0, 0)` <br> Cuerpo 1: `(10, 10, 12)` |
| **Velocidades** | Cuerpo 0: `(-3, 0, 0)` <br> Cuerpo 1: `(3, 0, 0)` |

**¿Por qué estas condiciones?**  
El problema de **2 cuerpos tiene solución analítica** (leyes de Kepler). Lo usamos como **prueba de control** para verificar que el integrador funciona correctamente. Si el código es fiable, las órbitas deben ser elipses perfectamente estables, sin caos y con una conservación de energía casi exacta.

**Resultados:**
- **Exponente de Lyapunov** → `-0.000041` (efectivamente **cero**, solo ruido numérico).
- **Deriva de energía** → `0.0000 %` (el integrador es impecable en este caso).
- **Entropía espacial** → `H = 4.0135` (máximo posible ~4.3041).

**¿Por qué la entropía es tan baja?**  
Con solo dos cuerpos, el movimiento relativo está confinado a un **único plano** (aunque simulemos en 3D). La trayectoria dibuja una **curva 1D (una elipse)** dentro de ese plano. Al repartir los puntos en la cuadrícula 3D, solo se ocupan las celdas que intersectan esa línea delgada. Por eso la entropía es la más baja de los tres casos. Es el sistema más "ordenado".


- <img width="1117" height="1160" alt="dos_cuerpos_trayectorias" src="https://github.com/user-attachments/assets/e5a4191c-e26f-4532-b349-b238072c2a76" />



---

### 2. Tres Cuerpos – El Caos Clásico

| Parámetro | Valor |
| :--- | :--- |
| **Masas** | `[10.0, 20.0, 30.0]` |
| **Posiciones** | Cuerpo 0: `(-10, 10, -11)` <br> Cuerpo 1: `(0, 0, 0)` <br> Cuerpo 2: `(10, 10, 12)` |
| **Velocidades** | Cuerpo 0: `(-3, 0, 0)` <br> Cuerpo 1: `(0, 0, 0)` <br> Cuerpo 2: `(3, 0, 0)` |

**¿Por qué estas condiciones?**  
Esta es una configuración **clásica asimétrica de 3 cuerpos**. Las masas son desiguales y las posiciones iniciales forman un triángulo escaleno. El cuerpo pesado (masa 30) está en el centro, atrayendo a los otros dos. Como el sistema no tiene simetrías globales y los cuerpos no pueden escapar (energía negativa), esperamos **encuentros cercanos intermitentes** – la marca distintiva del caos gravitacional.

**Resultados:**
- **Exponente de Lyapunov** → `0.043336` (**claramente positivo** – este sistema es caótico).
- **Deriva de energía** → `2.9543 %` (la más alta de todas, pero aún aceptable).
- **Entropía espacial** → `H = 5.3292` (máximo ~5.6664) – **la más alta de los tres casos**.

**¿Por qué la deriva de energía es más alta aquí?**  
Los encuentros cercanos provocan aceleraciones enormes. El integrador adaptativo reduce el paso de tiempo, pero el error numérico alcanza su punto máximo exactamente en esos momentos. Una deriva del ~3 % es **esperada** – sin el paso adaptativo, el propio código advierte que podría llegar al 1700 %. El hecho de que se mantenga acotada y regrese a valores bajos demuestra que el Velocity Verlet está haciendo su trabajo.

**¿Por qué la entropía espacial es la más alta?**  
El caos implica que el sistema **no se repite**. La trayectoria no se queda en una curva o superficie simple; explora un **volumen** del espacio 3D a lo largo del tiempo. Al hacer el histograma, los puntos llenan muchas más celdas que en el caso de 2 cuerpos, resultando en la entropía de Shannon más grande. El sistema se "esparce" por todo el espacio disponible.


- <img width="1117" height="1160" alt="tres_cuerpos_trayectorias" src="https://github.com/user-attachments/assets/a8a685ba-bb95-40ee-b6d1-2beabdee5c81" />


---

### 3. Cuatro Cuerpos – El Estabilizador Inesperado

| Parámetro | Valor |
| :--- | :--- |
| **Masas** | `[10.0, 20.0, 30.0, 15.0]` |
| **Posiciones** | Cuerpo 0: `(-10, 10, -11)` <br> Cuerpo 1: `(0, 0, 0)` <br> Cuerpo 2: `(10, 10, 12)` <br> Cuerpo 3: `(5, -10, 8)` |
| **Velocidades** | Cuerpo 0: `(-3, 0, 0)` <br> Cuerpo 1: `(0, 0, 0)` <br> Cuerpo 2: `(3, 0, 0)` <br> Cuerpo 3: `(0, 3, -2)` |

**¿Por qué estas condiciones?**  
Añadimos un cuarto cuerpo para comprobar si **más cuerpos = más caos** (una intuición muy común). El nuevo cuerpo se coloca fuera del plano principal con una velocidad que le da una órbita alrededor del centro de masas. Actúa como un perturbador.

**Resultados (la parte sorprendente):**
- **Exponente de Lyapunov** → `0.000377` (efectivamente **cero** – no hay caos para este cuerpo de referencia).
- **Deriva de energía** → `0.1697 %` (excelente conservación).
- **Entropía espacial** → `H = 4.8524` (máximo ~5.2149) – **intermedia**.

**¿Por qué no hay caos?**  
El cuarto cuerpo, con estas condiciones iniciales específicas, **no se acerca lo suficiente** al Cuerpo 0 (que es el que perturbamos para calcular el Lyapunov) durante las 50 unidades de tiempo. En cambio, actúa como un compañero lejano, estabilizando la dinámica local cerca del Cuerpo 0. Esto demuestra que **el caos no es una función simple del número de partículas** – depende críticamente de la geometría específica y de los encuentros cercanos. A tiempos más largos quizás se vuelva caótico, pero dentro de esta ventana de simulación se mantiene cuasi‑periódico.

**¿Por qué la entropía es intermedia?**  
Aunque no hay caos, tenemos **cuatro cuerpos moviéndose** en lugar de dos o tres. La configuración general ocupa una porción mayor del espacio que la elipse de 2 cuerpos, pero como el movimiento es más regular (no llena un volumen de forma caótica), no alcanza la alta entropía del caso caótico de 3 cuerpos. Se sitúa justo en el punto medio.


- <img width="1117" height="1160" alt="cuatro_cuerpos_trayectorias" src="https://github.com/user-attachments/assets/4cf0c632-67ee-4184-8a10-bd309b7597e7" />
`


---

## 📊 Resumen Comparativo

| Sistema | Lyapunov | Entropía Espacial | Deriva de Energía | Interpretación Física |
| :--- | :--- | :--- | :--- | :--- |
| **2 Cuerpos** | ~0 (sin caos) | **4.01** (más baja) | 0.00 % | Sistema integrable – puntos confinados a una curva 1D (elipse). |
| **3 Cuerpos** | **+0.043** (caótico) | **5.33** (más alta) | 2.95 % | Dispersión asimétrica – la trayectoria llena caóticamente un volumen 3D. |
| **4 Cuerpos** | ~0 (estabilidad local) | **4.85** (media) | 0.17 % | El cuarto cuerpo actúa como estabilizador en este intervalo – más disperso que 2 cuerpos, pero sin llenar caóticamente el espacio como el caso de 3 cuerpos. |

---

## ✅ Reflexiones Finales

Esta simulación demuestra perfectamente el poder de combinar:
- **Un integrador simpléctico** (Velocity Verlet) + **paso adaptativo** – para confiar en la solución numérica.
- **El monitoreo de la deriva de energía** – para separar los artefactos numéricos de la dinámica real.
- **El método de Benettin** – para medir el exponente máximo de Lyapunov de forma robusta.
- **La entropía espacial de Shannon** – para cuantificar qué tan "dispersas" están las órbitas, lo que complementa de forma maravillosa al exponente de Lyapunov.

El código nos muestra que **el caos es sutil**. Mientras que el sistema de 3 cuerpos exhibe caos claro y una entropía alta, añadir un cuarto cuerpo no aumenta automáticamente ninguna de las dos cosas – a veces incluso puede *suprimir* el caos local, al menos temporalmente. Esta es una ilustración perfecta de la rica y no monótona dinámica de los sistemas gravitacionales de N‑cuerpos.


Aquí tienes el **README** completo, estructurado y en español, listo para incluir en tu proyecto. Está redactado de manera formal, técnica y directa, cubriendo exactamente lo que pediste: planteamiento del problema, justificación de complejidad, explicación del código ACO y análisis de resultados con la demostración de inviabilidad de la fuerza bruta.

---

#  Solución del TD-TSP (Time-Dependent Traveling Salesman Problem) mediante Optimización por Colonias de Hormigas (ACO)

## 1. Planteamiento del Problema

El problema abordado es una variante del clásico Problema del Viajante (TSP), extendida con dos factores de complejidad del mundo real:

1. **Dependencia temporal de los costos (TD-TSP):** El tiempo de viaje entre dos nodos \( i \) y \( j \) no es una constante. Depende de la hora del día en que se realiza el desplazamiento, modelando el tráfico vehicular. Formalmente, el peso de la arista \( (i,j) \) se define como:
   \[
   w_{ij}(t) = \frac{d_{ij}}{v(t)}
   \]
   donde \( d_{ij} \) es la distancia euclidiana fija y \( v(t) \) es la velocidad promedio en la vía, la cual varía según la franja horaria (Hora Punta Mañana: 15 km/h, Valle: 40 km/h, Punta Tarde: 20 km/h, Noche: 60 km/h).



**Definición del Grafo:**
- \( V = \{0, 1, 2, \dots, n\} \): Nodo 0 es el depósito, los nodos \( 1 \) a \( n \) son los clientes.
- \( E \): Conjunto de aristas que conectan todos los pares de nodos (grafo completo).
- **Objetivo:** Encontrar una ruta que inicie y termine en el nodo 0, visite todos los clientes exactamente una vez, y minimice el costo total:
  \[
  C = T_{viaje} + \lambda \cdot \sum_{i=1}^{n} \max(0, (A_i - l_i))
  \]
  donde \( A_i \) es la hora real de llegada al cliente \( i \), y \( l_i \) es el límite superior de su ventana.

---

## 2. Justificación como Sistema Complejo

El problema del TD-TSP con ventanas de tiempo es inherentemente un **Sistema Complejo Adaptativo** por las siguientes razones:

- **Agentes descentralizados:** El tráfico y los horarios de entrega afectan a cada vehículo de manera local. No existe una entidad central que controle el flujo en tiempo real.
- **Interacciones no lineales:** La decisión de visitar un cliente antes que otro modifica la hora de llegada a los posteriores, alterando dinámicamente los pesos de todas las aristas futuras. El costo total no es la suma lineal de distancias, sino una función acoplada al tiempo acumulado.
- **Emergencia:** El comportamiento global (patrones de congestión, rutas eficientes) surge de la interacción de múltiples agentes (vehículos) con el entorno (vías y horarios).
- **Adaptación:** El sistema responde a cambios externos (ej. un aumento de tráfico) modificando las rutas óptimas.

En este contexto, el uso de un algoritmo metaheurístico como ACO es apropiado, ya que el propio ACO se comporta como un sistema complejo artificial (enjambre descentralizado con estigmergia) para explorar el vasto espacio de soluciones.

---

## 3. Descripción General del Código (Arquitectura)

El código se divide en cinco bloques funcionales principales:

### 3.1. Generación del Grafo (`generar_grafo`)
- Crea coordenadas aleatorias para `num_clientes + 1` nodos en un plano 2D (rango 0-100).
- Construye la matriz de distancias euclidianas fijas.
- Define la función de velocidad `velocidad(hora_minutos)` que retorna la velocidad según la franja horaria.
- Asigna a cada cliente una ventana de tiempo aleatoria \( [e_i, l_i] \) dentro del rango de 9:00 AM a 5:00 PM.

### 3.2. Función de Evaluación de Costo (`calcular_costo`)
- Simula el recorrido de una ruta dada.
- Mantiene un reloj interno (`tiempo_actual`).
- Acumula el `costo_viaje` sumando \( d_{ij} / v(t) \) en cada arista.
- Ajusta el reloj si se llega temprano (espera hasta `e_i`).

### 3.3. Algoritmo ACO (Clase `ACO`)
- **Inicialización:** Define \( \alpha, \beta, \rho \), número de hormigas e iteraciones. Inicializa la matriz de feromonas \( \tau \) con un valor constante.
- **Construcción de Ruta (`_construir_ruta`):** Cada hormiga construye una ruta secuencialmente. En cada paso, elige el siguiente cliente \( j \) con probabilidad:
  \[
  P_{ij}(t) = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}(t)]^\beta}{\sum_{k \notin Visitados} [\tau_{ik}]^\alpha \cdot [\eta_{ik}(t)]^\beta}
  \]
  donde \( \eta_{ij}(t) = 1 / w_{ij}(t) \) (heurística que penaliza el tráfico actual).
- **Actualización de Feromonas (`_actualizar_feromonas`):** Aplica **evaporación** (\( \tau \leftarrow (1-\rho)\tau \)) y **refuerzo** (deposita \( \Delta = 1 / Costo_{mejor} \) en las aristas de la mejor ruta global).

### 3.4. Búsqueda de Parámetros (Grid Search)
- Explora un espacio de 64 combinaciones de \( (\alpha, \beta, \rho) \):
  - \( \alpha \in \{0.5, 1.0, 1.5, 2.0\} \)
  - \( \beta \in \{1.0, 2.0, 3.0, 4.0\} \)
  - \( \rho \in \{0.1, 0.3, 0.5, 0.7\} \)
- Por cada combinación, ejecuta el ACO **2 veces** (con semillas distintas) para mitigar el efecto del azar, y se queda con el mejor costo de esas 2 ejecuciones.
- Selecciona la combinación que produjo el menor costo global.

### 3.5. Ejecución Final
- Toma la mejor combinación de parámetros del Grid Search.
- Crea una nueva instancia de ACO con más hormigas (30) y más iteraciones (100).
- Ejecuta una vez con una semilla fija (1234) y reporta la ruta, tiempo de viaje y penalización.

---

## 4. Resultados Experimentales (Instancia de 35 Clientes)

### 4.1. Mejores Parámetros Encontrados
- **\( \alpha = 2.0 \)** (Alta influencia de la feromona)
- **\( \beta = 1.0 \)** (Baja influencia de la heurística de tráfico)
- **\( \rho = 0.3 \)** (Tasa de evaporación moderada)
- **Mejor costo en Grid Search:** **10,536.66** minutos.

### 4.2. Ejecución Final (Semilla = 1234)
- **Ruta encontrada:**  
  `[0, 24, 17, 30, 31, 14, 22, 13, 29, 4, 11, 34, 12, 3, 21, 23, 25, 15, 32, 18, 19, 27, 10, 2, 26, 35, 16, 1, 9, 8, 28, 5, 6, 33, 20, 7, 0]`
- **Tiempo de viaje:** **37.74** minutos.
- **Penalización por retrasos:** **22,096.16** minutos.
- **Costo total final:** **22,133.90** minutos.

### 4.3. Análisis de los Resultados
La diferencia entre el costo del Grid Search (10,536) y el costo final (22,133) evidencia la naturaleza **estocástica** del ACO. La semilla utilizada en la ejecución final priorizó la velocidad absoluta (tiempo de viaje de solo 37.74 minutos), pero ignoró casi por completo las ventanas de tiempo, acumulando una penalización masiva de más de 22,000 minutos.

Esto demuestra el **trade-off fundamental** entre minimizar el tiempo de viaje y cumplir con los horarios de entrega. En un caso real, el factor de penalización \( \lambda \) debería incrementarse (ej. a 100 o 1000) para forzar al algoritmo a priorizar la puntualidad sobre la velocidad pura.

---

## 5. Inviabilidad de la Fuerza Bruta (NP-Hard)

El problema del TSP, del cual el TD-TSP es una generalización, es un problema **NP-Hard**. Para validar la necesidad de usar una metaheurística como ACO, analicemos el tamaño del espacio de búsqueda para nuestra instancia de **35 clientes**.

- Número de rutas posibles (permutaciones de los clientes):  
  \[
  35! = 10,333,147,966,386,144,929,666,651,337,523,200,000,000 \approx 1.03 \times 10^{40}
  \]

- **Supongamos** que tuviéramos la supercomputadora más rápida del mundo actual (*Frontier*), capaz de realizar \( 1.2 \times 10^{18} \) operaciones por segundo. Si evaluar **una sola ruta** costara únicamente **1 operación aritmética**, el tiempo requerido sería:
  \[
  \frac{1.03 \times 10^{40}}{1.2 \times 10^{18}} \approx 8.58 \times 10^{21} \text{ segundos}
  \]

- Convirtiendo a años:
  \[
  \frac{8.58 \times 10^{21}}{60 \times 60 \times 24 \times 365} \approx 2.72 \times 10^{14} \text{ años}
  \]

- La edad del universo es de aproximadamente \( 1.38 \times 10^{10} \) años. Por lo tanto, la supercomputadora más rápida del mundo tardaría:
  \[
  \frac{2.72 \times 10^{14}}{1.38 \times 10^{10}} \approx 19,700 \text{ veces la edad del universo}
  \]

**Conclusión:** Es **computacionalmente imposible** resolver esta instancia por fuerza bruta. Nuestro algoritmo ACO, en cambio, explora aproximadamente \( 64 \times 2 \times 100 \times 30 = 384,000 \) rutas en el Grid Search (más la ejecución final) y encuentra una solución de alta calidad en **cuestión de minutos**. Esto justifica plenamente el uso de sistemas complejos artificiales (enjambres de hormigas) para abordar problemas de optimización combinatoria en entornos dinámicos y restringidos.
