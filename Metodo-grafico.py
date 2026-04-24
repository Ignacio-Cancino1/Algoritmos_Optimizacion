import math
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# PARÁMETROS DEL PROBLEMA
# =========================================================

coef_objetivo = [3, 4]
tipo_optimizacion = "max"  # "max" para maximizar, "min" para minimizar
# cada restricciones  esta en formato a, b, c,  signo
restricciones = [
    [-1, 2, 8, "<="],    # x1 <= 4
    [3, -1, 16, ">="],   # 2x2 <= 12
    [1, 1, 20, "<="],   # 3x1 + 2x2 <= 18
    [1, 0, 0, ">="],    # x1 >= 0
    [0, 1, 0, ">="]     # x2 >= 0
]

holgura = 0.2  # Nos permite agregar un margen alrededor del grafico
resolucion = 500
tolerancia = 1e-6  # Tolerancia para comparaciones de casi-cero

# =========================================================
# FUNCIONES
# =========================================================

def funcion_objetivo(punto, coef):
    x1, x2 = punto
    return coef[0] * x1 + coef[1] * x2


def es_factible(punto, restricciones, tolerancia=1e-6):
    x1, x2 = punto  #Separamos los valores de los puntos a y b

    for a, b, c, signo in restricciones:    #recorremos cada restriccion y aplicamos la formula
        valor = a * x1 + b * x2

        if signo == "<=" and valor > c and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia): # si el signo es <= el resultado de la formula no puede ser mayor que c
            return False
        elif signo == ">=" and valor < c and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia): # si el signo es >= el resultado de la formula es menor que c
            return False
        elif signo == "=" and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia): # si el signo es =, entonces estan practicamente igual
            return False

    return True


def ordenar_poligono(puntos):  #ordenamos los puntos del poligono para que quede en secuencia alrededor del centro 
    cx = sum(p[0] for p in puntos) / len(puntos) #promedio de coordenadas x 
    cy = sum(p[1] for p in puntos) / len(puntos) # promedio de coordenads y 
    return sorted(puntos, key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))   #calculo el angulo  para poder ordenarlo alrededor de la region factible 


def quitar_duplicados(puntos, tolerancia=1e-6):  # quito los puntos que este repetidos en la intersecciones o sean casi iguales
    unicos = [] # variable para almacenar los puntos
    for p in puntos:
        repetido = False
        for q in unicos:
            if math.isclose(p[0], q[0], rel_tol=tolerancia, abs_tol=tolerancia) and math.isclose(p[1], q[1], rel_tol=tolerancia, abs_tol=tolerancia): # si la diferencia es pequeña lo considero repetido
                repetido = True
                break
        if not repetido:  # si no esta repetido lo agrego a unicos
            unicos.append(p)
    return unicos


def texto_restriccion(a, b, c, signo):  # lo uso para mostarlo por la terminal y en las leyendas de la grafica
    return f"{a}x1 + {b}x2 {signo} {c}"


def normalizar_restricciones(restricciones, tolerancia=1e-6):  # si el LD es negativo multiplica toda la fila por -1 e invierte el signo
    normalizadas = []
    for i, (a, b, c, signo) in enumerate(restricciones, start=1):
        if c < 0 and not math.isclose(c, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            signo_nuevo = ">=" if signo == "<=" else "<=" if signo == ">=" else signo
            normalizadas.append([-a, -b, -c, signo_nuevo])
            print(f"  [Normalización] R{i}: LD negativo → se multiplicó por -1 y el signo cambió a '{signo_nuevo}'")
        else:
            normalizadas.append([a, b, c, signo])
    return normalizadas


# =========================================================
# MOSTRAR DATOS DEL PROBLEMA
# =========================================================

print("FUNCIÓN OBJETIVO:")
accion = "Maximizar" if tipo_optimizacion == "max" else "Minimizar"
print(f"{accion} Z = {coef_objetivo[0]}*x1 + {coef_objetivo[1]}*x2")

print("\nRESTRICCIONES:")
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    print(f"R{i}: {texto_restriccion(a, b, c, signo)}")

# =========================================================
# NORMALIZAR RESTRICCIONES
# =========================================================

print("\nNORMALIZACIÓN DE RESTRICCIONES:")
restricciones = normalizar_restricciones(restricciones, tolerancia)

# =========================================================
# CALCULAR INTERSECCIONES
# =========================================================

intersecciones = []

for i in range(len(restricciones)):
    for j in range(i + 1, len(restricciones)):
        a1, b1, c1, _ = restricciones[i]
        a2, b2, c2, _ = restricciones[j]

        D = a1 * b2 - a2 * b1   # Calculo la determinante 

        if not math.isclose(D, 0, rel_tol=tolerancia, abs_tol=tolerancia):  # Regla de cramer
            x = (c1 * b2 - c2 * b1) / D
            y = (a1 * c2 - a2 * c1) / D
            intersecciones.append((x, y))

intersecciones = quitar_duplicados(intersecciones, tolerancia) # elimino intersecciones repetidas

print("\nINTERSECCIONES:")  # Las muestras  por consola 
for p in intersecciones:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# =========================================================
# FILTRAR PUNTOS FACTIBLES
# =========================================================

puntos_factibles = [p for p in intersecciones if es_factible(p, restricciones, tolerancia)]

if es_factible((0, 0), restricciones, tolerancia): # agrego el origen manualmente porque puede pertenecer al region factible
    puntos_factibles.append((0, 0))

puntos_factibles = quitar_duplicados(puntos_factibles, tolerancia) # elimino duplicados

print("\nPUNTOS FACTIBLES:")  
for p in puntos_factibles:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# =========================================================
# ORDENAR VÉRTICES FACTIBLES
# =========================================================

if len(puntos_factibles) >= 3:  # si hay mas de 3 puntos los ordeno si no los dejo como estan, porque 3, es porque 
    puntos_ordenados = ordenar_poligono(puntos_factibles)
else:
    puntos_ordenados = puntos_factibles[:]

print("\nVÉRTICES FACTIBLES ORDENADOS:") # solo los muestro ordenados 
for p in puntos_ordenados:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# =========================================================
# EVALUAR FUNCIÓN OBJETIVO
# =========================================================

mejor_punto = None
mejor_valor = -float("inf") if tipo_optimizacion == "max" else float("inf")

print("\nEVALUACIÓN DE LA FUNCIÓN OBJETIVO:")
for p in puntos_factibles:
    z = funcion_objetivo(p, coef_objetivo)
    print(f"Punto ({p[0]:.4f}, {p[1]:.4f}) -> Z = {z:.2f}")

    if tipo_optimizacion == "max" and z > mejor_valor:
        mejor_valor = z
        mejor_punto = p
    elif tipo_optimizacion == "min" and z < mejor_valor:
        mejor_valor = z
        mejor_punto = p

print("\nSOLUCIÓN ÓPTIMA:")
print(f"Punto óptimo = ({mejor_punto[0]:.4f}, {mejor_punto[1]:.4f})")
etiqueta_valor = "máximo" if tipo_optimizacion == "max" else "mínimo"
print(f"Valor {etiqueta_valor} de Z = {mejor_valor:.2f}")

# =========================================================
# DEFINIR VENTANA DEL GRÁFICO
# =========================================================

todos_x = [p[0] for p in intersecciones] + [0, mejor_punto[0]] # creo coordenadas x
todos_y = [p[1] for p in intersecciones] + [0, mejor_punto[1]] #creo coordenadas y


# Calculo los valores de la ventana que se genera 
xmin = min(todos_x)
xmax = max(todos_x)
ymin = min(todos_y)
ymax = max(todos_y)
# si el tamaño del rango de x y y de la grafica
rango_x = xmax - xmin if xmax != xmin else 1
rango_y = ymax - ymin if ymax != ymin else 1
 # agregamos los valores de las holgura para verlo mejor 
xmin -= rango_x * holgura
xmax += rango_x * holgura
ymin -= rango_y * holgura
ymax += rango_y * holgura

# =========================================================
# CREAR MALLA PARA LA REGIÓN FACTIBLE
# =========================================================

xx, yy = np.meshgrid(  # meshgrid combina ambos 
    np.linspace(xmin, xmax, resolucion), #genero muchos valores para x 
    np.linspace(ymin, ymax, resolucion) # genero muchos valores para y 
)
# considero que todos los puntos son de la region factible 
region = np.ones_like(xx, dtype=bool)
  # Recorro y veo si cumple las restricciones o no 
for a, b, c, signo in restricciones:
    if signo == "<=":
        region &= (a * xx + b * yy <= c + tolerancia)
    elif signo == ">=":
        region &= (a * xx + b * yy >= c - tolerancia)
    elif signo == "=":
        region &= (np.abs(a * xx + b * yy - c) <= tolerancia)

# =========================================================
# GRAFICAR
# =========================================================

plt.figure(figsize=(11, 8)) # tamaño de la figura 

# Región factible
plt.contourf(xx, yy, region, levels=[0.5, 1], colors=["limegreen"], alpha=0.35)

# Valores de x para graficar líneas
x_vals = np.linspace(xmin, xmax, resolucion)

# Restricciones DIBUJO LAS RECTAS 
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    etiqueta = f"R{i}: {texto_restriccion(a, b, c, signo)}" 

    if not math.isclose(b, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        y_vals = (c - a * x_vals) / b # veo como formar la recta
        plt.plot(x_vals, y_vals, linewidth=2, label=etiqueta)
    else:
        x_recta = c / a # veo si la recta es vertical
        plt.axvline(x=x_recta, linewidth=2, label=etiqueta)

# =========================================================
# FUNCIÓN OBJETIVO ÓPTIMA
# =========================================================

if not math.isclose(coef_objetivo[1], 0, rel_tol=tolerancia, abs_tol=tolerancia):
    y_obj = (mejor_valor - coef_objetivo[0] * x_vals) / coef_objetivo[1]
    plt.plot(
        x_vals,
        y_obj,
        'b-.',
        linewidth=2.8,
        label=f"Z óptima = {mejor_valor:.0f}"
    )
        
# =========================================================
# DIBUJAR SOLO VÉRTICES FACTIBLES CON ETIQUETAS
# =========================================================

# Centroide del polígono para calcular dirección de cada etiqueta
cx = sum(p[0] for p in puntos_ordenados) / len(puntos_ordenados)
cy = sum(p[1] for p in puntos_ordenados) / len(puntos_ordenados)

OFFSET_PX = 48  # distancia en puntos desde el vértice

for p in puntos_ordenados:
    plt.plot(p[0], p[1], 'ro', markersize=7)

    # Si es el punto óptimo, su etiqueta la pone el bloque de abajo
    if math.isclose(p[0], mejor_punto[0], rel_tol=tolerancia, abs_tol=tolerancia) and math.isclose(p[1], mejor_punto[1], rel_tol=tolerancia, abs_tol=tolerancia):
        continue

    # Vector desde el centroide hacia el vértice (dirección "hacia afuera")
    vx = p[0] - cx
    vy = p[1] - cy
    norma = np.hypot(vx, vy)
    if not math.isclose(norma, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        vx, vy = vx / norma, vy / norma
    else:
        vx, vy = 1.0, 0.0

    dx = int(vx * OFFSET_PX)
    dy = int(vy * OFFSET_PX)

    plt.annotate(
        f"({p[0]:.2f}, {p[1]:.2f})",
        (p[0], p[1]),
        textcoords="offset points",
        xytext=(dx, dy),
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
        arrowprops=dict(arrowstyle="->", linewidth=0.8)
    )

# =========================================================
# POLÍGONO FACTIBLE
# =========================================================
# marcamos el poligono factible en rojo 
if len(puntos_ordenados) >= 3:
    pol_x = [p[0] for p in puntos_ordenados] + [puntos_ordenados[0][0]]
    pol_y = [p[1] for p in puntos_ordenados] + [puntos_ordenados[0][1]]
    plt.plot(pol_x, pol_y, 'r--', linewidth=2, label="Región factible")

# =========================================================
# PUNTO ÓPTIMO
# =========================================================

plt.plot(mejor_punto[0], mejor_punto[1], 'bo', markersize=12, label="Punto óptimo")

# Etiqueta hacia afuera del centroide
vx_opt = mejor_punto[0] - cx
vy_opt = mejor_punto[1] - cy
norma_opt = np.hypot(vx_opt, vy_opt)
if not math.isclose(norma_opt, 0, rel_tol=tolerancia, abs_tol=tolerancia):
    vx_opt, vy_opt = vx_opt / norma_opt, vy_opt / norma_opt
else:
    vx_opt, vy_opt = 1.0, 0.0

plt.annotate(
    f"({mejor_punto[0]:.2f}, {mejor_punto[1]:.2f})\nÓptimo  Z={mejor_valor:.0f}",
    (mejor_punto[0], mejor_punto[1]),
    textcoords="offset points",
    xytext=(int(vx_opt * OFFSET_PX), int(vy_opt * OFFSET_PX)),
    fontsize=10,
    color="blue",
    ha="center",
    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
    arrowprops=dict(arrowstyle="->", color="blue", linewidth=0.8)
)

# =========================================================
# DETALLES FINALES
# =========================================================

plt.axhline(0, color='black', linewidth=0.8)
plt.axvline(0, color='black', linewidth=0.8)
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.grid(True)
plt.xlabel("x1")
plt.ylabel("x2")
plt.title(f"Método gráfico - {'Maximización' if tipo_optimizacion == 'max' else 'Minimización'}")
plt.legend()
plt.show()