import networkx as nx
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# ==========================================
# 1. DEFINICIÓN DE LAS 12 ACTIVIDADES
# ==========================================
actividades = {
    'A': {'a': 2, 'm': 4, 'b': 6, 'pred': []},
    'B': {'a': 3, 'm': 5, 'b': 9, 'pred': ['A']},
    'C': {'a': 1, 'm': 3, 'b': 5, 'pred': ['A']},
    'D': {'a': 4, 'm': 7, 'b': 10, 'pred': ['B']},
    'E': {'a': 2, 'm': 4, 'b': 8, 'pred': ['B', 'C']},
    'F': {'a': 3, 'm': 6, 'b': 9, 'pred': ['C']},
    'G': {'a': 5, 'm': 8, 'b': 12, 'pred': ['D']},
    'H': {'a': 2, 'm': 5, 'b': 7, 'pred': ['E', 'F']},
    'I': {'a': 4, 'm': 6, 'b': 10, 'pred': ['G']},
    'J': {'a': 2, 'm': 3, 'b': 6, 'pred': ['H']},
    'K': {'a': 3, 'm': 5, 'b': 8, 'pred': ['I', 'J']},
    'L': {'a': 1, 'm': 2, 'b': 4, 'pred': ['K']}
}

# ==========================================
# 2. FUNCIÓN PARA CONSTRUIR EL GRAFO Y CALCULAR RUTA CRÍTICA
# ==========================================
def calcular_duracion_proyecto(duraciones_dict):
    """
    Construye el grafo asignando las duraciones a los nodos objetivo (edges)
    para que dag_longest_path_length funcione correctamente.
    """
    G = nx.DiGraph()
    
    # Agregamos inicio y fin ficticios para conectar la red limpiamente
    G.add_node('Start')
    G.add_node('End')
    
    for act, datos in actividades.items():
        dur_act = duraciones_dict[act]
        predecesores = datos['pred']
        
        if not predecesores:
            # Si no tiene predecesor, viene de 'Start'
            G.add_edge('Start', act, weight=dur_act)
        else:
            for p in predecesores:
                G.add_edge(p, act, weight=dur_act)
                
    # Identificar nodos finales (que no son predecesores de nadie)
    todos_predecesores = set(p for d in actividades.values() for p in d['pred'])
    nodos_finales = set(actividades.keys()) - todos_predecesores
    for f in nodos_finales:
        G.add_edge(f, 'End', weight=0)

    # Duración de la ruta más larga (Ruta Crítica)
    duracion_total = nx.dag_longest_path_length(G, weight='weight')
    ruta = nx.dag_longest_path(G, weight='weight')
    
    # Limpiamos 'Start' y 'End' de la ruta mostrada
    ruta_limpia = [n for n in ruta if n not in ('Start', 'End')]
    
    return duracion_total, ruta_limpia

# ==========================================
# 3. CÁLCULO ANALÍTICO PERT
# ==========================================
duraciones_esperadas = {}
varianzas = {}

for act, d in actividades.items():
    te = (d['a'] + 4 * d['m'] + d['b']) / 6.0
    var = ((d['b'] - d['a']) / 6.0) ** 2
    duraciones_esperadas[act] = te
    varianzas[act] = var

te_analitica, ruta_critica = calcular_duracion_proyecto(duraciones_esperadas)
var_critica = sum(varianzas[act] for act in ruta_critica)
std_analitica = np.sqrt(var_critica)

print("--- CÁLCULO ANALÍTICO PERT ---")
print(f"Ruta Crítica Analítica: {' -> '.join(ruta_critica)}")
print(f"Duración Esperada Analítica (Te): {te_analitica:.2f} días")
print(f"Desviación Estándar Analítica (σ): {std_analitica:.2f}\n")

# ==========================================
# 4. SIMULACIÓN MONTE CARLO (10,000 ITERACIONES)
# ==========================================
N_SIMULACIONES = 10000

def sample_beta_pert(a, m, b):
    if a == b:
        return a
    alpha = 1 + 4 * (m - a) / (b - a)
    beta = 1 + 4 * (b - m) / (b - a)
    return stats.beta.rvs(alpha, beta, loc=a, scale=(b - a))

duraciones_simuladas = []

for _ in range(N_SIMULACIONES):
    # Generar un tiempo simulado para cada una de las 12 actividades
    tiempos_sim = {act: sample_beta_pert(d['a'], d['m'], d['b']) for act, d in actividades.items()}
    dur_sim, _ = calcular_duracion_proyecto(tiempos_sim)
    duraciones_simuladas.append(dur_sim)

duraciones_simuladas = np.array(duraciones_simuladas)

# ==========================================
# 5. RESULTADOS Y GRAFICACIÓN
# ==========================================
media_simulada = np.mean(duraciones_simuladas)
std_simulada = np.std(duraciones_simuladas)
p90_simulada = np.percentile(duraciones_simuladas, 90)

print("--- RESULTADOS SIMULACIÓN MONTE CARLO ---")
print(f"Media Simulada: {media_simulada:.2f} días")
print(f"Desviación Estándar Simulada: {std_simulada:.2f}")
print(f"Duración al 90% de confianza: {p90_simulada:.2f} días\n")

plt.figure(figsize=(10, 5))

# Histograma
count, bins, _ = plt.hist(
    duraciones_simuladas, 
    bins=40, 
    density=True, 
    alpha=0.6, 
    color='#3498db', 
    edgecolor='black', 
    label='Simulación Monte Carlo'
)

# Curva teórica Normal
x_axis = np.linspace(duraciones_simuladas.min() - 2, duraciones_simuladas.max() + 2, 200)
pdf_analitica = stats.norm.pdf(x_axis, loc=te_analitica, scale=std_analitica)
plt.plot(x_axis, pdf_analitica, 'r--', linewidth=2, label=f'Analítica N({te_analitica:.1f}, {std_analitica:.2f}²)')

# Percentil 90
plt.axvline(p90_simulada, color='#e67e22', linestyle='-', linewidth=2, label=f'Confianza 90% ({p90_simulada:.2f} días)')

plt.title('Comparación: Distribución Analítica PERT vs. Simulación Monte Carlo', fontsize=12)
plt.xlabel('Duración Total del Proyecto (días)')
plt.ylabel('Densidad de Probabilidad')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()