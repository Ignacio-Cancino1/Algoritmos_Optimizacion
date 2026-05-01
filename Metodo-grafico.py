import math
import numpy as np
import matplotlib.pyplot as plt

holgura    = 0.2   # margen extra alrededor del grafico
resolucion = 500   # cantidad de puntos en la malla
tolerancia = 1e-6  # margen de error numerico


# Pide los datos del problema al usuario por consola
def pedir_datos():
    print("=" * 50)
    print("   MÉTODO GRÁFICO - PROGRAMACIÓN LINEAL")
    print("=" * 50)

    # Numero de variables
    while True:
        try:
            n_vars = int(input("\n¿Cuántas variables tiene el problema? (normalmente 2): "))
            break
        except ValueError:
            print("  Error: ingrese un número entero.")

    # Coeficientes de la funcion objetivo
    coef_objetivo = []
    for i in range(1, n_vars + 1):
        while True:
            try:
                c = float(input(f"  Coeficiente de x{i} en la función objetivo: "))
                coef_objetivo.append(c)
                break
            except ValueError:
                print("  Error: ingrese un número.")

    # Tipo de optimizacion
    while True:
        tipo = input("\nTipo de optimización (max / min): ").strip().lower()
        if tipo in ("max", "min"):
            tipo_optimizacion = tipo
            break
        print("  Error: ingrese 'max' o 'min'.")

    print("\nNota: las restricciones de no negatividad (x1 >= 0, x2 >= 0)")
    print("      se agregan automáticamente. No las ingrese.")

    # Numero de restricciones
    while True:
        try:
            n_rest = int(input("\n¿Cuántas restricciones tiene el problema (sin contar no negatividad)? "))
            break
        except ValueError:
            print("  Error: ingrese un número entero.")

    # Datos de cada restriccion
    restricciones = []
    for i in range(1, n_rest + 1):
        print(f"\n  Restricción {i}:")
        while True:
            try:
                a = float(input("    Coeficiente de x1: "))
                break
            except ValueError:
                print("    Error: ingrese un número.")
        while True:
            try:
                b = float(input("    Coeficiente de x2: "))
                break
            except ValueError:
                print("    Error: ingrese un número.")
        while True:
            try:
                c = float(input("    Lado derecho (LD): "))
                break
            except ValueError:
                print("    Error: ingrese un número.")
        while True:
            signo = input("    Signo (<=, >= o =): ").strip()
            if signo in ("<=", ">=", "="):
                break
            print("    Error: ingrese '<=', '>=' o '='.")
        restricciones.append([a, b, c, signo])

    # Agregar no negatividad automaticamente
    restricciones.append([1, 0, 0, ">="])
    restricciones.append([0, 1, 0, ">="])

    return coef_objetivo, tipo_optimizacion, restricciones


coef_objetivo, tipo_optimizacion, restricciones = pedir_datos()


# Evalua Z = c1*x1 + c2*x2 en un punto dado
def funcion_objetivo(punto, coef):
    x1, x2 = punto
    return coef[0] * x1 + coef[1] * x2


# Verifica si un punto cumple todas las restricciones
def es_factible(punto, restricciones, tolerancia=1e-6):
    x1, x2 = punto
    for a, b, c, signo in restricciones:
        valor = a * x1 + b * x2
        if signo == "<=" and valor > c and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia):
            return False
        elif signo == ">=" and valor < c and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia):
            return False
        elif signo == "=" and not math.isclose(valor, c, rel_tol=tolerancia, abs_tol=tolerancia):
            return False
    return True


# Ordena los vertices en sentido antihorario para dibujar el poligono correctamente
def ordenar_poligono(puntos):
    # Centroide del poligono
    cx = sum(p[0] for p in puntos) / len(puntos)
    cy = sum(p[1] for p in puntos) / len(puntos)
    # Ordenar por angulo respecto al centroide
    return sorted(puntos, key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))


# Elimina puntos repetidos usando tolerancia numerica
def quitar_duplicados(puntos, tolerancia=1e-6):
    unicos = []
    for p in puntos:
        repetido = False
        for q in unicos:
            if math.isclose(p[0], q[0], rel_tol=tolerancia, abs_tol=tolerancia) and \
               math.isclose(p[1], q[1], rel_tol=tolerancia, abs_tol=tolerancia):
                repetido = True
                break
        if not repetido:
            unicos.append(p)
    return unicos


# Genera el texto de una restriccion para mostrar en consola y leyenda
def texto_restriccion(a, b, c, signo):
    return f"{a}x1 + {b}x2 {signo} {c}"


# Evita el -0.0 que puede aparecer en operaciones con floats
def limpiar_cero(valor, tolerancia=1e-6):
    return 0.0 if math.isclose(valor, 0, rel_tol=tolerancia, abs_tol=tolerancia) else valor


# Si algun LD es negativo, multiplica esa restriccion por -1 e invierte su signo
def normalizar_restricciones(restricciones, tolerancia=1e-6):
    normalizadas = []
    for i, (a, b, c, signo) in enumerate(restricciones, start=1):
        if c < 0 and not math.isclose(c, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            signo_nuevo = ">=" if signo == "<=" else "<=" if signo == ">=" else signo
            normalizadas.append([-a, -b, -c, signo_nuevo])
            print(f"  [Normalización] R{i}: LD negativo → se multiplicó por -1 y el signo cambió a '{signo_nuevo}'")
        else:
            normalizadas.append([a, b, c, signo])
    return normalizadas


# Mostrar datos ingresados
print("FUNCIÓN OBJETIVO:")
accion = "Maximizar" if tipo_optimizacion == "max" else "Minimizar"
print(f"{accion} Z = {coef_objetivo[0]}*x1 + {coef_objetivo[1]}*x2")

print("\nRESTRICCIONES:")
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    print(f"R{i}: {texto_restriccion(a, b, c, signo)}")

# Normalizar restricciones con LD negativo
print("\nNORMALIZACIÓN DE RESTRICCIONES:")
restricciones = normalizar_restricciones(restricciones, tolerancia)

# Calcular intersecciones entre todos los pares de restricciones usando la Regla de Cramer
intersecciones = []
for i in range(len(restricciones)):
    for j in range(i + 1, len(restricciones)):
        a1, b1, c1, _ = restricciones[i]
        a2, b2, c2, _ = restricciones[j]
        D = a1 * b2 - a2 * b1  # determinante; si es 0 las rectas son paralelas
        if not math.isclose(D, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            x = (c1 * b2 - c2 * b1) / D
            y = (a1 * c2 - a2 * c1) / D
            intersecciones.append((limpiar_cero(x, tolerancia), limpiar_cero(y, tolerancia)))

intersecciones = quitar_duplicados(intersecciones, tolerancia)

print("\nINTERSECCIONES:")
for p in intersecciones:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# Filtrar los puntos que cumplen todas las restricciones (vertices de la region factible)
puntos_factibles = [p for p in intersecciones if es_factible(p, restricciones, tolerancia)]

# El origen no siempre surge de intersecciones, lo revisamos aparte
if es_factible((0, 0), restricciones, tolerancia):
    puntos_factibles.append((0, 0))

puntos_factibles = quitar_duplicados(puntos_factibles, tolerancia)

print("\nPUNTOS FACTIBLES:")
for p in puntos_factibles:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# Ordenar vertices para poder dibujar el poligono sin lineas cruzadas
if len(puntos_factibles) >= 3:
    puntos_ordenados = ordenar_poligono(puntos_factibles)
else:
    puntos_ordenados = puntos_factibles[:]

print("\nVÉRTICES FACTIBLES ORDENADOS:")
for p in puntos_ordenados:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# Evaluar Z en cada vertice y guardar el mejor
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

# Calcular limites del grafico incluyendo el origen y el punto optimo
todos_x = [p[0] for p in intersecciones] + [0, mejor_punto[0]]
todos_y = [p[1] for p in intersecciones] + [0, mejor_punto[1]]

xmin, xmax = min(todos_x), max(todos_x)
ymin, ymax = min(todos_y), max(todos_y)

# Evitar rango cero si todos los puntos tienen la misma coordenada
rango_x = xmax - xmin if xmax != xmin else 1
rango_y = ymax - ymin if ymax != ymin else 1

# Agregar margen para que nada quede cortado en el borde
xmin -= rango_x * holgura
xmax += rango_x * holgura
ymin -= rango_y * holgura
ymax += rango_y * holgura

# Crear malla de puntos y marcar cuales son factibles para colorear la region
xx, yy = np.meshgrid(
    np.linspace(xmin, xmax, resolucion),
    np.linspace(ymin, ymax, resolucion)
)

region = np.ones_like(xx, dtype=bool)  # empezar asumiendo todo factible
for a, b, c, signo in restricciones:
    if signo == "<=":
        region &= (a * xx + b * yy <= c + tolerancia)
    elif signo == ">=":
        region &= (a * xx + b * yy >= c - tolerancia)
    elif signo == "=":
        region &= (np.abs(a * xx + b * yy - c) <= tolerancia)

# --- Graficar ---
plt.figure(figsize=(11, 8))

# Colorear la region factible
plt.contourf(xx, yy, region, levels=[0.5, 1], colors=["limegreen"], alpha=0.35)

x_vals = np.linspace(xmin, xmax, resolucion)

# Dibujar cada restriccion como una recta
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    etiqueta = f"R{i}: {texto_restriccion(a, b, c, signo)}"
    if not math.isclose(b, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        y_vals = (c - a * x_vals) / b  # despejar x2
        plt.plot(x_vals, y_vals, linewidth=2, label=etiqueta)
    else:
        # Recta vertical cuando b == 0: x1 = c/a
        x_recta = c / a
        plt.axvline(x=x_recta, linewidth=2, label=etiqueta)

# Dibujar la recta de la funcion objetivo en su valor optimo
if not math.isclose(coef_objetivo[1], 0, rel_tol=tolerancia, abs_tol=tolerancia):
    y_obj = (mejor_valor - coef_objetivo[0] * x_vals) / coef_objetivo[1]
    plt.plot(x_vals, y_obj, 'b-.', linewidth=2.8, label=f"Z óptima = {mejor_valor:.0f}")

# Centroide del poligono para calcular la direccion de las etiquetas
cx = sum(p[0] for p in puntos_ordenados) / len(puntos_ordenados)
cy = sum(p[1] for p in puntos_ordenados) / len(puntos_ordenados)

OFFSET_PX = 48  # distancia en pixeles entre el punto y su etiqueta

# Marcar y etiquetar cada vertice factible
for p in puntos_ordenados:
    plt.plot(p[0], p[1], 'ro', markersize=7)

    # El punto optimo tiene su propia etiqueta mas abajo
    if math.isclose(p[0], mejor_punto[0], rel_tol=tolerancia, abs_tol=tolerancia) and \
       math.isclose(p[1], mejor_punto[1], rel_tol=tolerancia, abs_tol=tolerancia):
        continue

    # Vector desde el centroide hacia el vertice (apunta hacia afuera)
    vx = p[0] - cx
    vy = p[1] - cy
    norma = np.hypot(vx, vy)
    if not math.isclose(norma, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        vx, vy = vx / norma, vy / norma  # normalizar a longitud 1
    else:
        vx, vy = 1.0, 0.0  # direccion por defecto si el vertice esta en el centroide

    plt.annotate(
        f"({p[0]:.2f}, {p[1]:.2f})",
        (p[0], p[1]),
        textcoords="offset points",
        xytext=(int(vx * OFFSET_PX), int(vy * OFFSET_PX)),
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
        arrowprops=dict(arrowstyle="->", linewidth=0.8)
    )

# Dibujar el contorno del poligono factible
if len(puntos_ordenados) >= 3:
    pol_x = [p[0] for p in puntos_ordenados] + [puntos_ordenados[0][0]]  # cerrar el poligono
    pol_y = [p[1] for p in puntos_ordenados] + [puntos_ordenados[0][1]]
    plt.plot(pol_x, pol_y, 'r--', linewidth=2, label="Región factible")

# Marcar el punto optimo con un punto azul y su etiqueta
plt.plot(mejor_punto[0], mejor_punto[1], 'bo', markersize=12, label="Punto óptimo")

# Calcular direccion de la etiqueta del optimo (hacia afuera del poligono)
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

# Configuracion final y mostrar el grafico
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
