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
