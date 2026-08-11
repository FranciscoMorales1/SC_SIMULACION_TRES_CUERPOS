import math
import random
import numpy as np
from itertools import product

# -------------------- 1. GENERACIÓN DEL GRAFO TEMPORAL --------------------

def generar_grafo(num_clientes=35, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    # Coordenadas: nodo 0 = depósito, nodos 1..num_clientes = clientes
    coords = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_clientes + 1)]

    # Matriz de distancias euclidianas (fijas), en "km"
    n = len(coords)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i][j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])

    # Generar ventanas de tiempo y tiempo de servicio
    ventanas = {}
    for i in range(1, n):
        e = random.uniform(480, 840)  # Abre entre 8:00 AM y 2:00 PM
        l = e + random.uniform(60, 180) # Ventana dura entre 1 y 3 horas
        ventanas[i] = (e, l)

    tiempo_servicio = 15.0  # 15 minutos por cliente

    # Función de velocidad según la hora del día (en km/h)
    def velocidad(hora_minutos):
        hora = (hora_minutos % 1440) / 60.0
        if 7.0 <= hora < 9.0:      # Hora punta mañana
            return 15.0
        elif 9.0 <= hora < 17.0:   # Horario valle
            return 40.0
        elif 17.0 <= hora < 19.0:  # Hora punta tarde
            return 20.0
        else:                       # Noche / madrugada
            return 60.0

    return {
        'n': n,
        'coords': coords,
        'dist': dist,
        'velocidad': velocidad,
        'ventanas': ventanas,
        'tiempo_servicio': tiempo_servicio
    }

# -------------------- 2. FUNCIÓN DE COSTO (SIN PENALIZACIÓN) --------------------

def _tiempo_viaje_minutos(dist_ij, velocidad_fn, tiempo_actual):
    horas = dist_ij / velocidad_fn(tiempo_actual)
    return horas * 60.0


def calcular_costo(ruta, grafo):
    dist = grafo['dist']
    velocidad = grafo['velocidad']
    ventanas = grafo['ventanas']
    servicio = grafo['tiempo_servicio']

    tiempo_actual = 480  # 8:00 AM
    costo_viaje = 0.0

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]

        t_viaje = _tiempo_viaje_minutos(dist[origen][destino], velocidad, tiempo_actual)
        costo_viaje += t_viaje
        tiempo_actual += t_viaje

        if destino != 0:
            e, l = ventanas[destino]
            if tiempo_actual < e:
                tiempo_actual = e  # espera pasiva hasta que abre la ventana
            tiempo_actual += servicio

    return costo_viaje


def analizar_ventanas(ruta, grafo):
    dist = grafo['dist']
    velocidad = grafo['velocidad']
    ventanas = grafo['ventanas']
    servicio = grafo['tiempo_servicio']

    tiempo_actual = 480
    detalle = []

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]

        t_viaje = _tiempo_viaje_minutos(dist[origen][destino], velocidad, tiempo_actual)
        tiempo_actual += t_viaje

        if destino != 0:
            e, l = ventanas[destino]
            llegada = tiempo_actual
            if tiempo_actual < e:
                tiempo_actual = e
            retraso = max(0.0, llegada - l)
            tiempo_actual += servicio
            detalle.append({
                'nodo': destino,
                'llegada': llegada,
                'ventana': (e, l),
                'retraso_min': retraso
            })

    return detalle

# -------------------- 3. ALGORITMO ACO --------------------

class ACO:
    def __init__(self, grafo, alpha, beta, rho, num_hormigas, iteraciones):
        self.grafo = grafo
        self.n = grafo['n']
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.num_hormigas = num_hormigas
        self.iteraciones = iteraciones
        self.dist = grafo['dist']
        self.velocidad = grafo['velocidad']
        self.ventanas = grafo['ventanas']
        self.servicio = grafo['tiempo_servicio']

        # Inicializar feromonas
        self.tau = np.ones((self.n, self.n)) * 0.1

    def _construir_ruta(self):
        """Construye una ruta completa para una hormiga."""
        inicio = 0
        no_visitados = list(range(1, self.n))
        ruta = [inicio]
        tiempo_actual = 480  # 8:00 AM
        nodo_actual = inicio

        while no_visitados:
            probs = []
            for j in no_visitados:
                t_viaje = _tiempo_viaje_minutos(self.dist[nodo_actual][j], self.velocidad, tiempo_actual)
                eta = 1.0 / (t_viaje + 0.1)
                tau = self.tau[nodo_actual][j]
                prob = (tau ** self.alpha) * (eta ** self.beta)
                probs.append((j, prob))

            nodos, pesos = zip(*probs)
            pesos = np.array(pesos)
            if pesos.sum() == 0:
                siguiente = random.choice(no_visitados)
            else:
                pesos = pesos / pesos.sum()
                siguiente = np.random.choice(nodos, p=pesos)

            t_viaje = _tiempo_viaje_minutos(self.dist[nodo_actual][siguiente], self.velocidad, tiempo_actual)
            tiempo_actual += t_viaje
            if siguiente != 0:
                e, l = self.ventanas[siguiente]
                if tiempo_actual < e:
                    tiempo_actual = e  # espera
                tiempo_actual += self.servicio

            ruta.append(siguiente)
            no_visitados.remove(siguiente)
            nodo_actual = siguiente

        # Regresar al depósito
        t_viaje = _tiempo_viaje_minutos(self.dist[nodo_actual][0], self.velocidad, tiempo_actual)
        tiempo_actual += t_viaje
        ruta.append(0)

        return ruta

    def _actualizar_feromonas(self, mejor_ruta, mejor_costo):
        """Evaporación + refuerzo en la mejor ruta global."""
        self.tau = (1 - self.rho) * self.tau

        delta = 1.0 / (mejor_costo + 1e-6)
        for i in range(len(mejor_ruta) - 1):
            u = mejor_ruta[i]
            v = mejor_ruta[i + 1]
            self.tau[u][v] += delta
            self.tau[v][u] += delta  # grafo no dirigido

    def ejecutar(self, semilla=None):
        if semilla is not None:
            random.seed(semilla)
            np.random.seed(semilla)

        mejor_ruta = None
        mejor_costo = float('inf')

        for it in range(self.iteraciones):
            rutas = []
            costos = []

            for _ in range(self.num_hormigas):
                ruta = self._construir_ruta()
                costo = calcular_costo(ruta, self.grafo)
                rutas.append(ruta)
                costos.append(costo)

            idx_mejor = np.argmin(costos)
            if costos[idx_mejor] < mejor_costo:
                mejor_costo = costos[idx_mejor]
                mejor_ruta = rutas[idx_mejor].copy()

            self._actualizar_feromonas(mejor_ruta, mejor_costo)

        return mejor_ruta, mejor_costo

# -------------------- 4. GRID SEARCH --------------------

def grid_search(grafo, ejecuciones_por_combo=3):
    """Prueba combinaciones de (alpha, beta, rho) y devuelve la mejor."""

    alphas = [0.5, 1.0, 1.5, 2.0]
    betas = [1.0, 2.0, 3.0, 4.0]
    rhos = [0.1, 0.3, 0.5, 0.7]

    mejor_costo_global = float('inf')
    mejor_params = None
    mejor_ruta_global = None

    total_combos = len(alphas) * len(betas) * len(rhos)
    contador = 0

    for alpha, beta, rho in product(alphas, betas, rhos):
        contador += 1
        print(f"Probando combo {contador}/{total_combos}: alpha={alpha}, beta={beta}, rho={rho}")

        costos_combo = []
        rutas_combo = []

        for ejec in range(ejecuciones_por_combo):
            semilla = ejec * 100 + contador
            aco = ACO(grafo, alpha, beta, rho, num_hormigas=20, iteraciones=50)
            ruta, costo = aco.ejecutar(semilla=semilla)
            costos_combo.append(costo)
            rutas_combo.append(ruta)

        mejor_idx = np.argmin(costos_combo)
        mejor_costo_combo = costos_combo[mejor_idx]
        mejor_ruta_combo = rutas_combo[mejor_idx]

        if mejor_costo_combo < mejor_costo_global:
            mejor_costo_global = mejor_costo_combo
            mejor_params = (alpha, beta, rho)
            mejor_ruta_global = mejor_ruta_combo
            print(f"  -> NUEVA MEJOR: {mejor_costo_global:.2f}")

    return mejor_params, mejor_ruta_global, mejor_costo_global

# -------------------- 5. EJECUCIÓN FINAL --------------------

if __name__ == "__main__":
    print("Generando grafo de prueba (35 clientes + depósito)...")
    grafo = generar_grafo(num_clientes=35, seed=42)

    print("\n--- INICIANDO GRID SEARCH ---")
    mejor_params, mejor_ruta, mejor_costo = grid_search(grafo, ejecuciones_por_combo=2)

    print("\n" + "=" * 60)
    print("RESULTADOS DEL GRID SEARCH:")
    print(f"Mejores parámetros encontrados: alpha={mejor_params[0]}, beta={mejor_params[1]}, rho={mejor_params[2]}")
    print(f"Mejor costo alcanzado: {mejor_costo:.2f} minutos")
    print(f"Ruta encontrada: {mejor_ruta}")
    print("=" * 60)

    print("\n--- EJECUCIÓN FINAL CON LA MEJOR CONFIGURACIÓN ---")
    aco_final = ACO(grafo,
                     alpha=mejor_params[0],
                     beta=mejor_params[1],
                     rho=mejor_params[2],
                     num_hormigas=30,
                     iteraciones=100)

    ruta_final, costo_final = aco_final.ejecutar(semilla=1234)
    total = calcular_costo(ruta_final, grafo)

    print(f"Ruta definitiva: {ruta_final}")
    print(f"Costo total final (tiempo de viaje): {total:.2f} min")

    detalle = analizar_ventanas(ruta_final, grafo)
    retrasados = [d for d in detalle if d['retraso_min'] > 0]
    print(f"\nClientes con llegada fuera de ventana: {len(retrasados)} / {len(detalle)}")
    if retrasados:
        peor = max(retrasados, key=lambda d: d['retraso_min'])
        print(f"Peor retraso: cliente {peor['nodo']}, {peor['retraso_min']:.1f} min "
              f"(ventana {peor['ventana']}, llegó en {peor['llegada']:.1f})")