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
    
    # Matriz de distancias euclidianas (fijas)
    n = len(coords)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i][j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])

    # Función de velocidad según la hora del día (en km/h)
    def velocidad(hora_minutos):
        hora = hora_minutos / 60.0
        if 7.0 <= hora < 9.0:      # Hora punta mañana
            return 15.0
        elif 9.0 <= hora < 17.0:   # Horario valle
            return 40.0
        elif 17.0 <= hora < 19.0:  # Hora punta tarde
            return 20.0
        else:                       # Noche / madrugada
            return 60.0

    # Ventanas de tiempo para cada cliente: (hora más temprana, hora más tarde)
    # El depósito (nodo 0) no tiene restricción
    hora_inicio = 480  # 8:00 AM en minutos
    ventanas = [(0, 1000)]  # Depósito
    for i in range(1, n):
        # Ventanas aleatorias entre 9:00 AM (540) y 5:00 PM (1020)
        e = random.randint(540, 840)
        l = e + random.randint(60, 180)  # ventana de 1 a 3 horas
        ventanas.append((e, l))

    return {
        'n': n,
        'coords': coords,
        'dist': dist,
        'velocidad': velocidad,
        'ventanas': ventanas,
        'tiempo_servicio': 10  # minutos de descarga en cada cliente
    }

# -------------------- 2. FUNCIÓN DE COSTO (CON PENALIZACIÓN) --------------------

def calcular_costo(ruta, grafo):
    """
    ruta: lista de nodos [0, 3, 1, 4, ..., 0]
    Retorna: (tiempo_total, penalizacion, costo_total)
    """
    dist = grafo['dist']
    velocidad = grafo['velocidad']
    ventanas = grafo['ventanas']
    servicio = grafo['tiempo_servicio']
    
    tiempo_actual = 480  # 8:00 AM
    costo_viaje = 0
    penalizacion = 0

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i+1]
        
        # Tiempo de viaje dinámico
        t_viaje = dist[origen][destino] / velocidad(tiempo_actual)
        costo_viaje += t_viaje
        tiempo_actual += t_viaje
        
        # Si no es el depósito, aplicamos tiempo de servicio y revisamos ventana
        if destino != 0:
            # Tiempo de servicio
            tiempo_actual += servicio
            
            # Penalización por llegar tarde (blanda)
            e, l = ventanas[destino]
            if tiempo_actual > l:
                penalizacion += (tiempo_actual - l) * 10  # lambda = 10
            # Si llega muy temprano, espera (se suma al tiempo)
            if tiempo_actual < e:
                tiempo_actual = e  # espera pasiva, suma tiempo

    return costo_viaje, penalizacion, costo_viaje + penalizacion

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
            # Calcular probabilidades para cada nodo no visitado
            probs = []
            for j in no_visitados:
                t_viaje = self.dist[nodo_actual][j] / self.velocidad(tiempo_actual)
                # Heurística = inversa del tiempo de viaje (evita tráfico)
                eta = 1.0 / (t_viaje + 0.1)
                tau = self.tau[nodo_actual][j]
                prob = (tau ** self.alpha) * (eta ** self.beta)
                probs.append((j, prob))

            # Normalizar y elegir por ruleta
            nodos, pesos = zip(*probs)
            pesos = np.array(pesos)
            if pesos.sum() == 0:
                # Si todo es cero, elegir aleatorio
                siguiente = random.choice(no_visitados)
            else:
                pesos = pesos / pesos.sum()
                siguiente = np.random.choice(nodos, p=pesos)

            # Avanzar
            t_viaje = self.dist[nodo_actual][siguiente] / self.velocidad(tiempo_actual)
            tiempo_actual += t_viaje
            if siguiente != 0:
                tiempo_actual += self.servicio
                e, l = self.ventanas[siguiente]
                if tiempo_actual < e:
                    tiempo_actual = e  # espera

            ruta.append(siguiente)
            no_visitados.remove(siguiente)
            nodo_actual = siguiente

        # Regresar al depósito
        t_viaje = self.dist[nodo_actual][0] / self.velocidad(tiempo_actual)
        tiempo_actual += t_viaje
        ruta.append(0)

        return ruta

    def _actualizar_feromonas(self, mejor_ruta, mejor_costo):
        """Evaporación + refuerzo en la mejor ruta global."""
        # Evaporación
        self.tau = (1 - self.rho) * self.tau
        
        # Refuerzo (solo en la mejor ruta)
        delta = 1.0 / (mejor_costo + 1e-6)
        for i in range(len(mejor_ruta) - 1):
            u = mejor_ruta[i]
            v = mejor_ruta[i+1]
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
            
            # Construir rutas para todas las hormigas
            for _ in range(self.num_hormigas):
                ruta = self._construir_ruta()
                _, _, costo = calcular_costo(ruta, self.grafo)
                rutas.append(ruta)
                costos.append(costo)
            
            # Mejor de esta iteración
            idx_mejor = np.argmin(costos)
            if costos[idx_mejor] < mejor_costo:
                mejor_costo = costos[idx_mejor]
                mejor_ruta = rutas[idx_mejor].copy()
            
            # Actualizar feromonas con la mejor global
            self._actualizar_feromonas(mejor_ruta, mejor_costo)

        return mejor_ruta, mejor_costo

# -------------------- 4. GRID SEARCH --------------------

def grid_search(grafo, ejecuciones_por_combo=3):
    """Prueba combinaciones de (alpha, beta, rho) y devuelve la mejor."""
    
    # Espacio de búsqueda grueso
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

        # Ejecutar varias veces con diferentes semillas para robustez
        for ejec in range(ejecuciones_por_combo):
            semilla = ejec * 100 + contador
            aco = ACO(grafo, alpha, beta, rho, num_hormigas=20, iteraciones=50)
            ruta, costo = aco.ejecutar(semilla=semilla)
            costos_combo.append(costo)
            rutas_combo.append(ruta)

        # Tomamos el mejor costo de estas ejecuciones
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
    print("Generando grafo de prueba (10 clientes + depósito)...")
    grafo = generar_grafo(num_clientes=35, seed=42)

    print("\n--- INICIANDO GRID SEARCH ---")
    mejor_params, mejor_ruta, mejor_costo = grid_search(grafo, ejecuciones_por_combo=2)

    print("\n" + "="*60)
    print("RESULTADOS DEL GRID SEARCH:")
    print(f"Mejores parámetros encontrados: alpha={mejor_params[0]}, beta={mejor_params[1]}, rho={mejor_params[2]}")
    print(f"Mejor costo alcanzado: {mejor_costo:.2f} minutos (incluye penalizaciones)")
    print(f"Ruta encontrada: {mejor_ruta}")
    print("="*60)

    print("\n--- EJECUCIÓN FINAL CON LA MEJOR CONFIGURACIÓN ---")
    aco_final = ACO(grafo, 
                    alpha=mejor_params[0], 
                    beta=mejor_params[1], 
                    rho=mejor_params[2],
                    num_hormigas=30,
                    iteraciones=100)
    
    ruta_final, costo_final = aco_final.ejecutar(semilla=1234)
    tiempo_viaje, penalizacion, total = calcular_costo(ruta_final, grafo)
    
    print(f"Ruta definitiva: {ruta_final}")
    print(f"Tiempo de viaje: {tiempo_viaje:.2f} min")
    print(f"Penalización por retrasos: {penalizacion:.2f}")
    print(f"Costo total final: {total:.2f} min")