import math           # Para comparaciones numéricas precisas con math.isclose()
import numpy as np    # Para cálculos numéricos y manejo de matrices/arreglos
import matplotlib.pyplot as plt  # Para graficar la región factible y las restricciones

# Parámetros técnicos fijos: el usuario no necesita modificarlos
holgura    = 0.2    # Margen extra (20%) que se agrega alrededor del gráfico para que no quede cortado
resolucion = 500    # Cantidad de puntos en cada eje de la malla; más puntos = región factible más suave
tolerancia = 1e-6   # Margen de error numérico: dos valores se consideran "iguales" si difieren menos que esto

# =========================================================
# ENTRADA DE DATOS POR CONSOLA
# Esta sección pide al usuario todos los datos del problema:
# coeficientes de la función objetivo, tipo de optimización
# y cada restricción. Incluye validación para evitar errores.
# =========================================================

def pedir_datos():
    """
    Solicita al usuario por consola todos los datos necesarios para resolver
    el problema de programación lineal y los retorna listos para usar.

    No recibe parámetros.

    Retorna:
        coef_objetivo    : lista de floats con los coeficientes de la función objetivo [c1, c2, ...]
        tipo_optimizacion: string 'max' o 'min' según lo que el usuario quiera optimizar
        restricciones    : lista de restricciones, cada una en formato [a, b, c, signo]
                           donde a*x1 + b*x2 signo c. Ya incluye las de no negatividad.
    """
    # Encabezado visual para que el usuario sepa qué programa está corriendo
    print("=" * 50)
    print("   MÉTODO GRÁFICO - PROGRAMACIÓN LINEAL")
    print("=" * 50)

    # --- Función objetivo ---

    # Pedimos cuántas variables tiene el problema (siempre 2 en 2D, pero lo pedimos para ser flexibles)
    while True:
        try:
            n_vars = int(input("\n¿Cuántas variables tiene el problema? (normalmente 2): "))
            break  # Si la conversión a int fue exitosa, salimos del bucle
        except ValueError:
            # Si el usuario escribió letras u otro valor no numérico, pedimos de nuevo
            print("  Error: ingrese un número entero.")

    # Pedimos el coeficiente de cada variable de la función objetivo
    coef_objetivo = []  # Lista vacía que iremos llenando con cada coeficiente
    for i in range(1, n_vars + 1):  # Iteramos desde x1 hasta xn
        while True:
            try:
                c = float(input(f"  Coeficiente de x{i} en la función objetivo: "))
                coef_objetivo.append(c)  # Agregamos el coeficiente a la lista
                break
            except ValueError:
                print("  Error: ingrese un número.")

    # Pedimos si se quiere maximizar o minimizar
    while True:
        tipo = input("\nTipo de optimización (max / min): ").strip().lower()  # strip() quita espacios, lower() pasa a minúscula
        if tipo in ("max", "min"):
            tipo_optimizacion = tipo
            break
        print("  Error: ingrese 'max' o 'min'.")

    # --- Restricciones ---

    # Avisamos que x1 >= 0 y x2 >= 0 se agregan solas para que el usuario no las duplique
    print("\nNota: las restricciones de no negatividad (x1 >= 0, x2 >= 0)")
    print("      se agregan automáticamente. No las ingrese.")

    # Pedimos la cantidad de restricciones que ingresará el usuario
    while True:
        try:
            n_rest = int(input("\n¿Cuántas restricciones tiene el problema (sin contar no negatividad)? "))
            break
        except ValueError:
            print("  Error: ingrese un número entero.")

    restricciones = []  # Lista que acumulará todas las restricciones ingresadas
    for i in range(1, n_rest + 1):  # Iteramos una vez por cada restricción
        print(f"\n  Restricción {i}:")

        # Coeficiente de x1 en esta restricción
        while True:
            try:
                a = float(input("    Coeficiente de x1: "))
                break
            except ValueError:
                print("    Error: ingrese un número.")

        # Coeficiente de x2 en esta restricción
        while True:
            try:
                b = float(input("    Coeficiente de x2: "))
                break
            except ValueError:
                print("    Error: ingrese un número.")

        # Lado derecho (LD) de la restricción: el valor constante después del signo
        while True:
            try:
                c = float(input("    Lado derecho (LD): "))
                break
            except ValueError:
                print("    Error: ingrese un número.")

        # Signo de la restricción: solo se aceptan <=, >= o =
        while True:
            signo = input("    Signo (<=, >= o =): ").strip()
            if signo in ("<=", ">=", "="):
                break
            print("    Error: ingrese '<=', '>=' o '='.")

        # Guardamos la restricción como lista [a, b, c, signo]
        restricciones.append([a, b, c, signo])

    # Agregamos automáticamente las restricciones de no negatividad al final
    restricciones.append([1, 0, 0, ">="])  # x1 >= 0: las variables no pueden ser negativas
    restricciones.append([0, 1, 0, ">="])  # x2 >= 0

    return coef_objetivo, tipo_optimizacion, restricciones


# Llamamos a pedir_datos() y guardamos los tres valores que retorna
coef_objetivo, tipo_optimizacion, restricciones = pedir_datos()

# =========================================================
# FUNCIONES
# Aquí se definen todas las operaciones reutilizables del programa.
# =========================================================

def funcion_objetivo(punto, coef):
    """
    Evalúa el valor de la función objetivo Z = c1*x1 + c2*x2 en un punto dado.

    Parámetros:
        punto : tupla (x1, x2) con las coordenadas del punto donde evaluar Z
        coef  : lista [c1, c2] con los coeficientes de la función objetivo

    Retorna:
        El valor numérico de Z en ese punto (un float)
    """
    x1, x2 = punto          # Desempaquetamos las coordenadas del punto
    return coef[0] * x1 + coef[1] * x2  # Calculamos Z = c1*x1 + c2*x2


def es_factible(punto, restricciones, tolerancia=1e-6):
    """
    Verifica si un punto (x1, x2) cumple todas las restricciones del problema.

    Parámetros:
        punto        : tupla (x1, x2) con las coordenadas del punto a verificar
        restricciones: lista de restricciones, cada una en formato [a, b, c, signo]
        tolerancia   : margen de error permitido para comparaciones numéricas (default 1e-6)

    Retorna:
        True si el punto cumple todas las restricciones, False si viola alguna
    """
    x1, x2 = punto  # Separamos las coordenadas para usarlas individualmente

    for a, b, c, signo in restricciones:  # Recorremos cada restricción y verificamos si el punto la cumple
        valor = a * x1 + b * x2  # Evaluamos el lado izquierdo de la restricción en este punto

        # Para <= : el punto no puede superar c (con tolerancia para evitar falsos negativos por redondeo)
        if signo == "<=" and valor > c and not math.isclose(
            valor, c,              # Los dos valores que comparamos
            rel_tol=tolerancia,    # Tolerancia relativa: escala según el tamaño de los números
            abs_tol=tolerancia     # Tolerancia absoluta: mínima diferencia aceptable cuando ambos son casi cero
        ):
            return False

        # Para >= : el punto no puede ser menor que c (con tolerancia)
        elif signo == ">=" and valor < c and not math.isclose(
            valor, c,
            rel_tol=tolerancia,
            abs_tol=tolerancia
        ):
            return False

        # Para = : el punto debe estar prácticamente igual a c
        elif signo == "=" and not math.isclose(
            valor, c,
            rel_tol=tolerancia,
            abs_tol=tolerancia
        ):
            return False

    return True  # Si pasó todos los filtros, el punto es factible


def ordenar_poligono(puntos):
    """
    Ordena una lista de puntos en sentido antihorario alrededor de su centroide.
    Esto es necesario para que matplotlib dibuje el polígono correctamente sin líneas cruzadas.

    Parámetros:
        puntos: lista de tuplas (x, y) que forman los vértices del polígono

    Retorna:
        Lista de tuplas ordenadas angularmente alrededor del centroide
    """
    # Calculamos el centroide: promedio de todas las coordenadas x e y
    cx = sum(p[0] for p in puntos) / len(puntos)  # Coordenada x del centro del polígono
    cy = sum(p[1] for p in puntos) / len(puntos)  # Coordenada y del centro del polígono

    # Ordenamos por ángulo usando arctan2: calcula el ángulo de cada punto respecto al centroide
    # arctan2(dy, dx) devuelve el ángulo en radianes entre -π y π
    return sorted(puntos, key=lambda p: np.arctan2(
        p[1] - cy,  # Diferencia en y entre el vértice y el centroide
        p[0] - cx   # Diferencia en x entre el vértice y el centroide
    ))


def quitar_duplicados(puntos, tolerancia=1e-6):
    """
    Elimina puntos repetidos o casi iguales de una lista, comparando con tolerancia numérica.
    Dos puntos se consideran el mismo si tanto su x como su y son prácticamente iguales.

    Parámetros:
        puntos    : lista de tuplas (x, y) que puede contener duplicados
        tolerancia: margen de error para considerar dos coordenadas iguales (default 1e-6)

    Retorna:
        Lista de tuplas sin duplicados
    """
    unicos = []  # Acumulamos aquí solo los puntos que no estén repetidos
    for p in puntos:
        repetido = False
        for q in unicos:
            # Comparamos cada coordenada con tolerancia relativa y absoluta
            if math.isclose(p[0], q[0], rel_tol=tolerancia, abs_tol=tolerancia) and \
               math.isclose(p[1], q[1], rel_tol=tolerancia, abs_tol=tolerancia):
                repetido = True  # Este punto ya existe en la lista
                break
        if not repetido:
            unicos.append(p)  # Solo agregamos el punto si no es duplicado
    return unicos


def texto_restriccion(a, b, c, signo):
    """
    Genera un string legible de la restricción para mostrar en consola y en la leyenda del gráfico.

    Parámetros:
        a    : coeficiente de x1
        b    : coeficiente de x2
        c    : lado derecho (valor constante)
        signo: operador de comparación ('<=', '>=' o '=')

    Retorna:
        String con el formato "ax1 + bx2 signo c"
    """
    return f"{a}x1 + {b}x2 {signo} {c}"


def limpiar_cero(valor, tolerancia=1e-6):
    """
    Corrige el problema del -0.0 que puede aparecer en operaciones con floats.
    Si el valor está suficientemente cerca de cero, retorna 0.0 exacto.

    Parámetros:
        valor     : número float a verificar
        tolerancia: margen para considerar que el valor es cero (default 1e-6)

    Retorna:
        0.0 si el valor es casi cero, o el valor original sin cambios si no lo es
    """
    return 0.0 if math.isclose(
        valor, 0,              # Comparamos el valor contra cero exacto
        rel_tol=tolerancia,    # Tolerancia relativa
        abs_tol=tolerancia     # Tolerancia absoluta (importante para comparar contra 0)
    ) else valor


def normalizar_restricciones(restricciones, tolerancia=1e-6):
    """
    Corrige restricciones cuyo lado derecho (LD) es negativo.
    En programación lineal, un LD negativo puede confundir los algoritmos,
    por lo que se multiplica toda la fila por -1 e invierte el signo de la desigualdad.
    Ejemplo: -x1 - x2 <= -4 se convierte en x1 + x2 >= 4 (equivalente matemáticamente).

    Parámetros:
        restricciones: lista de restricciones en formato [a, b, c, signo]
        tolerancia   : margen para detectar si c es estrictamente negativo (default 1e-6)

    Retorna:
        Nueva lista de restricciones con los LD negativos corregidos
    """
    normalizadas = []
    for i, (a, b, c, signo) in enumerate(restricciones, start=1):
        # Verificamos si el LD es negativo (y no es simplemente casi-cero)
        if c < 0 and not math.isclose(c, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            # Invertimos el signo de la desigualdad al multiplicar por -1
            signo_nuevo = ">=" if signo == "<=" else "<=" if signo == ">=" else signo
            normalizadas.append([-a, -b, -c, signo_nuevo])  # Multiplicamos todos los coeficientes por -1
            print(f"  [Normalización] R{i}: LD negativo → se multiplicó por -1 y el signo cambió a '{signo_nuevo}'")
        else:
            normalizadas.append([a, b, c, signo])  # La restricción queda igual
    return normalizadas


# =========================================================
# MOSTRAR DATOS DEL PROBLEMA
# Imprimimos en consola la función objetivo y las restricciones
# tal como las ingresó el usuario, antes de procesarlas.
# =========================================================

print("FUNCIÓN OBJETIVO:")
accion = "Maximizar" if tipo_optimizacion == "max" else "Minimizar"  # Texto descriptivo según el tipo
print(f"{accion} Z = {coef_objetivo[0]}*x1 + {coef_objetivo[1]}*x2")

print("\nRESTRICCIONES:")
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    print(f"R{i}: {texto_restriccion(a, b, c, signo)}")  # Mostramos cada restricción en formato legible

# =========================================================
# NORMALIZAR RESTRICCIONES
# Corregimos restricciones con LD negativo antes de operar
# sobre ellas, para evitar errores en los cálculos.
# =========================================================

print("\nNORMALIZACIÓN DE RESTRICCIONES:")
restricciones = normalizar_restricciones(restricciones, tolerancia)  # Reemplazamos la lista original con la corregida

# =========================================================
# CALCULAR INTERSECCIONES
# Encontramos todos los puntos donde se cruzan dos restricciones.
# Estos puntos son candidatos a ser vértices de la región factible.
# =========================================================

intersecciones = []  # Lista que acumulará todos los puntos de cruce

# Tomamos cada par de restricciones (i, j) para encontrar su intersección
for i in range(len(restricciones)):
    for j in range(i + 1, len(restricciones)):  # j siempre mayor que i para no repetir pares
        a1, b1, c1, _ = restricciones[i]  # Coeficientes de la restricción i (ignoramos el signo con _)
        a2, b2, c2, _ = restricciones[j]  # Coeficientes de la restricción j

        # Calculamos el determinante del sistema 2x2. Si es 0, las rectas son paralelas y no se cruzan
        D = a1 * b2 - a2 * b1

        # Solo calculamos la intersección si el determinante no es cero
        if not math.isclose(D, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            # Aplicamos la Regla de Cramer para resolver el sistema de 2 ecuaciones con 2 incógnitas
            # Fórmula: x = (c1*b2 - c2*b1) / D,  y = (a1*c2 - a2*c1) / D
            x = (c1 * b2 - c2 * b1) / D
            y = (a1 * c2 - a2 * c1) / D
            # Limpiamos posibles -0.0 antes de guardar el punto
            intersecciones.append((limpiar_cero(x, tolerancia), limpiar_cero(y, tolerancia)))

intersecciones = quitar_duplicados(intersecciones, tolerancia)  # Eliminamos puntos repetidos que pueden surgir de múltiples combinaciones

print("\nINTERSECCIONES:")
for p in intersecciones:
    print(f"({p[0]:.4f}, {p[1]:.4f})")  # Mostramos cada punto con 4 decimales

# =========================================================
# FILTRAR PUNTOS FACTIBLES
# De todos los puntos de intersección, nos quedamos solo con
# los que cumplen TODAS las restricciones simultáneamente.
# Esos son los vértices de la región factible.
# =========================================================

# Filtramos usando comprensión de listas: solo conservamos los puntos factibles
puntos_factibles = [p for p in intersecciones if es_factible(p, restricciones, tolerancia)]

# El origen (0,0) no siempre surge de intersecciones, lo revisamos por separado
if es_factible((0, 0), restricciones, tolerancia):
    puntos_factibles.append((0, 0))  # Lo agregamos si cumple todas las restricciones

puntos_factibles = quitar_duplicados(puntos_factibles, tolerancia)  # Eliminamos duplicados que puedan haber quedado

print("\nPUNTOS FACTIBLES:")
for p in puntos_factibles:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# =========================================================
# ORDENAR VÉRTICES FACTIBLES
# Ordenamos los vértices en sentido antihorario para poder
# dibujar el contorno del polígono correctamente.
# =========================================================

if len(puntos_factibles) >= 3:  # Con menos de 3 puntos no hay polígono, no es necesario ordenar
    puntos_ordenados = ordenar_poligono(puntos_factibles)
else:
    puntos_ordenados = puntos_factibles[:]  # Copiamos la lista tal cual con [:]

print("\nVÉRTICES FACTIBLES ORDENADOS:")
for p in puntos_ordenados:
    print(f"({p[0]:.4f}, {p[1]:.4f})")

# =========================================================
# EVALUAR FUNCIÓN OBJETIVO
# Calculamos el valor de Z en cada vértice factible.
# El método gráfico garantiza que el óptimo siempre está
# en uno de los vértices de la región factible.
# =========================================================

mejor_punto = None
# Valor inicial: -infinito para max (cualquier Z será mayor), +infinito para min (cualquier Z será menor)
mejor_valor = -float("inf") if tipo_optimizacion == "max" else float("inf")

print("\nEVALUACIÓN DE LA FUNCIÓN OBJETIVO:")
for p in puntos_factibles:
    z = funcion_objetivo(p, coef_objetivo)  # Calculamos Z en este vértice
    print(f"Punto ({p[0]:.4f}, {p[1]:.4f}) -> Z = {z:.2f}")

    # Actualizamos el mejor punto si encontramos un Z mejor según el tipo de optimización
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
# Calculamos los límites del área visible del gráfico,
# con un margen extra (holgura) para que nada quede cortado.
# =========================================================

# Reunimos todas las coordenadas x e y relevantes para calcular los extremos del gráfico
todos_x = [p[0] for p in intersecciones] + [0, mejor_punto[0]]  # Incluimos el origen y el punto óptimo
todos_y = [p[1] for p in intersecciones] + [0, mejor_punto[1]]

xmin = min(todos_x)  # Límite izquierdo del gráfico
xmax = max(todos_x)  # Límite derecho del gráfico
ymin = min(todos_y)  # Límite inferior del gráfico
ymax = max(todos_y)  # Límite superior del gráfico

# Calculamos el ancho y alto del rango. Si todos los puntos tienen el mismo x o y, usamos 1 para evitar rango cero
rango_x = xmax - xmin if xmax != xmin else 1
rango_y = ymax - ymin if ymax != ymin else 1

# Expandimos los límites añadiendo un porcentaje de margen en cada dirección
xmin -= rango_x * holgura  # Margen izquierdo
xmax += rango_x * holgura  # Margen derecho
ymin -= rango_y * holgura  # Margen inferior
ymax += rango_y * holgura  # Margen superior

# =========================================================
# CREAR MALLA PARA LA REGIÓN FACTIBLE
# Generamos una grilla de puntos que cubre toda la ventana
# y marcamos cuáles están dentro de la región factible.
# Esto permite colorear el área factible en el gráfico.
# =========================================================

# np.meshgrid crea dos matrices 2D: una con todos los valores de x y otra con todos los de y
# combinándolos para cubrir cada punto (x, y) de la grilla
xx, yy = np.meshgrid(
    np.linspace(xmin, xmax, resolucion),  # 'resolucion' valores igualmente espaciados en x
    np.linspace(ymin, ymax, resolucion)   # 'resolucion' valores igualmente espaciados en y
)

# Comenzamos asumiendo que todos los puntos de la grilla son factibles (True)
region = np.ones_like(xx, dtype=bool)

# Aplicamos cada restricción sobre toda la grilla a la vez (operación vectorizada)
for a, b, c, signo in restricciones:
    if signo == "<=":
        # Un punto es factible si a*x + b*y <= c (con tolerancia para puntos sobre la frontera)
        region &= (a * xx + b * yy <= c + tolerancia)
    elif signo == ">=":
        # Un punto es factible si a*x + b*y >= c (con tolerancia)
        region &= (a * xx + b * yy >= c - tolerancia)
    elif signo == "=":
        # Un punto es factible si está prácticamente sobre la recta a*x + b*y = c
        region &= (np.abs(a * xx + b * yy - c) <= tolerancia)

# =========================================================
# GRAFICAR
# Dibujamos todos los elementos visuales: región factible,
# rectas de restricciones, función objetivo óptima,
# vértices con etiquetas, polígono y punto óptimo.
# =========================================================

plt.figure(figsize=(11, 8))  # Creamos la figura con tamaño 11x8 pulgadas

# Coloreamos la región factible usando contourf (relleno entre niveles)
plt.contourf(
    xx, yy,              # Coordenadas de la grilla
    region,              # Matriz booleana: True donde el punto es factible
    levels=[0.5, 1],     # Rellenamos solo donde region > 0.5 (es decir, donde es True)
    colors=["limegreen"],# Color del relleno
    alpha=0.35           # Transparencia: 0 = invisible, 1 = sólido
)

# Arreglo de valores de x para evaluar y graficar cada recta
x_vals = np.linspace(xmin, xmax, resolucion)

# Dibujamos una recta por cada restricción
for i, (a, b, c, signo) in enumerate(restricciones, start=1):
    etiqueta = f"R{i}: {texto_restriccion(a, b, c, signo)}"  # Texto para la leyenda

    # Si b != 0, la recta no es vertical: despejamos x2 = (c - a*x1) / b
    if not math.isclose(b, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        y_vals = (c - a * x_vals) / b  # Calculamos los y correspondientes a cada x
        plt.plot(x_vals, y_vals, linewidth=2, label=etiqueta)
    else:
        # Si b == 0, la recta es vertical: x1 = c/a (línea recta paralela al eje y)
        x_recta = c / a
        plt.axvline(x=x_recta, linewidth=2, label=etiqueta)  # axvline dibuja una línea vertical

# =========================================================
# FUNCIÓN OBJETIVO ÓPTIMA
# Dibujamos la recta Z = mejor_valor para mostrar visualmente
# dónde toca la región factible la función objetivo en su óptimo.
# =========================================================

# Solo graficamos si el coeficiente de x2 no es cero (para poder despejar x2)
if not math.isclose(coef_objetivo[1], 0, rel_tol=tolerancia, abs_tol=tolerancia):
    # Despejamos x2 de Z = c1*x1 + c2*x2 → x2 = (Z - c1*x1) / c2
    y_obj = (mejor_valor - coef_objetivo[0] * x_vals) / coef_objetivo[1]
    plt.plot(
        x_vals,
        y_obj,
        'b-.',        # Línea azul con punto y guion (estilo dash-dot)
        linewidth=2.8,
        label=f"Z óptima = {mejor_valor:.0f}"
    )

# =========================================================
# DIBUJAR SOLO VÉRTICES FACTIBLES CON ETIQUETAS
# Marcamos cada vértice con un punto rojo y una etiqueta con
# sus coordenadas. La etiqueta se coloca hacia afuera del
# polígono para no superponerse con las rectas interiores.
# =========================================================

# Calculamos el centroide del polígono para saber en qué dirección apunta "hacia afuera" desde cada vértice
cx = sum(p[0] for p in puntos_ordenados) / len(puntos_ordenados)  # Coordenada x del centro
cy = sum(p[1] for p in puntos_ordenados) / len(puntos_ordenados)  # Coordenada y del centro

OFFSET_PX = 48  # Distancia en puntos de pantalla entre el vértice y su etiqueta

for p in puntos_ordenados:
    plt.plot(p[0], p[1], 'ro', markersize=7)  # Punto rojo en el vértice

    # El punto óptimo tiene su propia etiqueta en el bloque siguiente, no la dibujamos aquí
    if math.isclose(p[0], mejor_punto[0], rel_tol=tolerancia, abs_tol=tolerancia) and \
       math.isclose(p[1], mejor_punto[1], rel_tol=tolerancia, abs_tol=tolerancia):
        continue  # Saltamos este vértice y pasamos al siguiente

    # Calculamos el vector desde el centroide hacia el vértice (apunta "hacia afuera" del polígono)
    vx = p[0] - cx
    vy = p[1] - cy

    # Normalizamos el vector dividiéndolo por su longitud para que tenga módulo 1
    norma = np.hypot(vx, vy)  # np.hypot calcula sqrt(vx² + vy²), la longitud del vector
    if not math.isclose(norma, 0, rel_tol=tolerancia, abs_tol=tolerancia):
        vx, vy = vx / norma, vy / norma  # Vector unitario: misma dirección, longitud 1
    else:
        vx, vy = 1.0, 0.0  # Si el vértice está en el centroide, usamos dirección derecha por defecto

    # Calculamos el desplazamiento en píxeles multiplicando el vector unitario por la distancia deseada
    dx = int(vx * OFFSET_PX)
    dy = int(vy * OFFSET_PX)

    plt.annotate(
        f"({p[0]:.2f}, {p[1]:.2f})",  # Texto de la etiqueta con las coordenadas del vértice
        (p[0], p[1]),                  # Punto en el gráfico al que apunta la flecha
        textcoords="offset points",    # El desplazamiento xytext se mide en puntos de pantalla
        xytext=(dx, dy),               # Desplazamiento (en puntos) desde el punto anotado hasta el texto
        fontsize=9,
        ha="center",                   # Alineación horizontal del texto: centrado sobre el ancla
        bbox=dict(
            boxstyle="round,pad=0.2", # Fondo con bordes redondeados y pequeño margen interior
            fc="white",               # Color de fondo blanco para que se lea sobre cualquier línea
            ec="none",                # Sin borde visible alrededor del recuadro
            alpha=0.7                 # Transparencia del fondo: levemente transparente
        ),
        arrowprops=dict(
            arrowstyle="->",          # Flecha simple apuntando al vértice
            linewidth=0.8             # Grosor de la flecha
        )
    )

# =========================================================
# POLÍGONO FACTIBLE
# Dibujamos el contorno del polígono factible uniendo los
# vértices en orden. El último punto se conecta al primero
# para cerrar la figura.
# =========================================================

if len(puntos_ordenados) >= 3:  # Necesitamos al menos 3 puntos para formar un polígono
    # Extraemos las coordenadas x e y de los vértices y cerramos el polígono repitiendo el primero al final
    pol_x = [p[0] for p in puntos_ordenados] + [puntos_ordenados[0][0]]
    pol_y = [p[1] for p in puntos_ordenados] + [puntos_ordenados[0][1]]
    plt.plot(pol_x, pol_y, 'r--', linewidth=2, label="Región factible")  # Línea roja discontinua

# =========================================================
# PUNTO ÓPTIMO
# Marcamos visualmente la solución óptima con un punto azul
# y una etiqueta que muestra sus coordenadas y el valor de Z.
# =========================================================

plt.plot(mejor_punto[0], mejor_punto[1], 'bo', markersize=12, label="Punto óptimo")  # Punto azul grande

# Calculamos la dirección de la etiqueta: hacia afuera del centroide, igual que los demás vértices
vx_opt = mejor_punto[0] - cx  # Componente x del vector centroide → óptimo
vy_opt = mejor_punto[1] - cy  # Componente y del vector centroide → óptimo

norma_opt = np.hypot(vx_opt, vy_opt)  # Longitud del vector
if not math.isclose(norma_opt, 0, rel_tol=tolerancia, abs_tol=tolerancia):
    vx_opt, vy_opt = vx_opt / norma_opt, vy_opt / norma_opt  # Normalizamos a longitud 1
else:
    vx_opt, vy_opt = 1.0, 0.0  # Dirección por defecto si el óptimo está en el centroide

plt.annotate(
    f"({mejor_punto[0]:.2f}, {mejor_punto[1]:.2f})\nÓptimo  Z={mejor_valor:.0f}",  # Coordenadas y valor óptimo de Z
    (mejor_punto[0], mejor_punto[1]),                                                # Punto al que apunta la flecha
    textcoords="offset points",                                                      # Desplazamiento en puntos de pantalla
    xytext=(int(vx_opt * OFFSET_PX), int(vy_opt * OFFSET_PX)),                      # Posición del texto respecto al punto
    fontsize=10,
    color="blue",    # Texto en azul para diferenciarlo de los otros vértices
    ha="center",     # Centrado horizontalmente
    bbox=dict(
        boxstyle="round,pad=0.2",
        fc="white",  # Fondo blanco para legibilidad
        ec="none",
        alpha=0.7
    ),
    arrowprops=dict(
        arrowstyle="->",
        color="blue",   # Flecha azul igual que el texto
        linewidth=0.8
    )
)

# =========================================================
# DETALLES FINALES
# Configuramos los ejes, la grilla, los títulos y mostramos
# el gráfico completo con todos los elementos dibujados.
# =========================================================

plt.axhline(0, color='black', linewidth=0.8)  # Eje horizontal (y = 0)
plt.axvline(0, color='black', linewidth=0.8)  # Eje vertical (x = 0)
plt.xlim(xmin, xmax)   # Fijamos los límites del eje x con el margen calculado
plt.ylim(ymin, ymax)   # Fijamos los límites del eje y con el margen calculado
plt.grid(True)         # Activamos la grilla de fondo para facilitar la lectura
plt.xlabel("x1")       # Etiqueta del eje horizontal
plt.ylabel("x2")       # Etiqueta del eje vertical
plt.title(f"Método gráfico - {'Maximización' if tipo_optimizacion == 'max' else 'Minimización'}")  # Título dinámico según tipo
plt.legend()           # Mostramos la leyenda con los nombres de cada elemento graficado
plt.show()             # Renderizamos y mostramos la ventana con el gráfico
