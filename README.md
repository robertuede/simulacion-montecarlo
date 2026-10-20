# PERT & Monte Carlo Project Simulator 

Este repositorio contiene una herramienta en **Python** diseñada para estimar la duración total de un proyecto mediante dos enfoques: el análisis analítico tradicional **PERT** (*Program Evaluation and Review Technique*) y una **Simulación Monte Carlo** de 10,000 iteraciones.

Combina teoría de grafos y modelos estadísticos para ir más allá de las estimaciones estáticas tradicionales y ofrecer una visión mucho más realista del riesgo en la gestión de proyectos.

---

## ¿Cómo funciona?

En la gestión de proyectos tradicional, el método PERT calcula una duración esperada basada en tres escenarios (optimista, más probable y pesimista). Sin embargo, PERT suele **subestimar la duración real** porque ignora que los caminos paralelos se pueden convertir en la ruta crítica si ocurren retrasos.

Este script soluciona ese problema dividiendo el análisis en tres fases:

### 1. Modelado de Red (Teoría de Grafos)
Utiliza la librería `networkx` para construir un **Grafo Dirigido Acíclico (DAG)** con las dependencias entre las 12 actividades definidas. Encuentra la **Ruta Crítica** (el camino de mayor duración que determina la fecha mínima de entrega).

### 2. Cálculo Analítico PERT
Para cada actividad, calcula:
* **Duración esperada ($T_e$):** $T_e = \frac{a + 4m + b}{6}$
* **Varianza ($\sigma^2$):** $\sigma^2 = \left(\frac{b - a}{6}\right)^2$

Posteriormente, asume una distribución Normal acumulada a lo largo de la ruta crítica.

### 3. Simulación Monte Carlo (10,000 iteraciones)
Para capturar la variabilidad real:
1. Muestrea duraciones aleatorias para cada actividad usando una distribución **Beta-PERT** entre sus límites ($a, m, b$).
2. Recalcula la ruta crítica del proyecto en cada una de las **10,000 ejecuciones**.
3. Genera métricas de confianza, como el **Percentil 90 (P90)**, que representa el número de días necesarios para tener un 90% de certeza de entregar a tiempo.

---

## 🛠️ Requisitos Previos

Asegúrate de tener Python 3.8+ instalado y las siguientes librerías:

```bash
pip install networkx numpy scipy matplotlib
