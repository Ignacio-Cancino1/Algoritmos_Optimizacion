import math

# ==========================================================
# METODO SIMPLEX CON DETECCION AUTOMATICA DE DOS FASES
# ==========================================================


# ----------------------------------------------------------
# FUNCION: detectar que metodo corresponde
# ----------------------------------------------------------
def detectar_metodo(signos, b, tolerancia=1e-6):
    """
    Detecta automaticamente si el problema debe resolverse con:
    - simplex normal
    - metodo de dos fases

    Reglas:
    - Si aparece >= o =  --> dos fases
    - Si algun LD es negativo --> por seguridad dos fases

    Parametros:
        signos    : lista de signos de restricciones ["<=", ">=", ...]
        b         : lista de lados derechos
        tolerancia: margen de error numerico (default 1e-6)

    Retorna:
        "simplex" o "dos_fases"
    """
    for signo in signos:
        if signo == ">=" or signo == "=":
            return "dos_fases"

    for lado_derecho in b:
        if lado_derecho < 0 and not math.isclose(lado_derecho, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            return "dos_fases"

    return "simplex"


# ----------------------------------------------------------
# FUNCION: construir tabla inicial simplex normal
# ----------------------------------------------------------
def construir_tabla_inicial(c, A, b):
    """
    Construye la tabla inicial del simplex normal para:
    - maximizacion
    - restricciones <=
    - lados derechos positivos
    """

    n = len(c)   # numero de variables de decision
    m = len(A)   # numero de restricciones

    # Encabezados
    columnas = ["VB", "Z"]

    # Variables de decision: x1, x2, ...
    for i in range(n):
        columnas.append(f"x{i+1}")

    # Variables de holgura: h1, h2, ...
    for i in range(m):
        columnas.append(f"h{i+1}")

    # Lado derecho
    columnas.append("LD")

    # Fila Z
    fila_z = ["Z", 1]

    # Coeficientes negativos de la funcion objetivo
    for coef in c:
        fila_z.append(-coef)

    # Ceros en las holguras
    for _ in range(m):
        fila_z.append(0)

    # LD de la funcion objetivo
    fila_z.append(0)

    tabla = [fila_z]

    # Filas de restricciones
    for i in range(m):
        fila = [f"h{i+1}", 0]

        # Coeficientes de x
        for valor in A[i]:
            fila.append(valor)

        # Matriz identidad para holguras
        for j in range(m):
            if i == j:
                fila.append(1)
            else:
                fila.append(0)

        # LD
        fila.append(b[i])

        tabla.append(fila)

    return columnas, tabla


# ----------------------------------------------------------
# FUNCION: imprimir tabla
# ----------------------------------------------------------
def imprimir_tabla(columnas, tabla, titulo="TABLA SIMPLEX"):
    ancho = 10

    print(f"\n{titulo}:\n")

    for col in columnas:
        print(f"{col:>{ancho}}", end="")
    print()

    print("-" * (ancho * len(columnas)))

    for fila in tabla:
        for j, valor in enumerate(fila):
            if j == 0:
                print(f"{str(valor):>{ancho}}", end="")
            else:
                if isinstance(valor, float):
                    print(f"{valor:>{ancho}.2f}", end="")
                else:
                    print(f"{str(valor):>{ancho}}", end="")
        print()


# ----------------------------------------------------------
# FUNCION: encontrar columna pivote
# ----------------------------------------------------------
def encontrar_columna_pivote(tabla, columnas, tolerancia=1e-6):
    """
    Busca la columna con el valor mas negativo en la fila objetivo (Z o W).
    Si no hay negativos, retorna -1.

    Parametros:
        tabla     : tabla simplex actual
        columnas  : lista de nombres de columnas
        tolerancia: margen para considerar un valor como cero (default 1e-6)
    """
    fila_z = tabla[0]

    # Desde x1 hasta antes de LD
    inicio = 2
    fin = len(columnas) - 1

    menor_valor = 0
    indice_pivote = -1

    for j in range(inicio, fin):
        valor = fila_z[j]
        # Solo consideramos el valor si es estrictamente negativo (fuera de tolerancia)
        if valor < menor_valor and not math.isclose(valor, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            menor_valor = valor
            indice_pivote = j

    return indice_pivote


# ----------------------------------------------------------
# FUNCION: encontrar fila pivote
# ----------------------------------------------------------
def encontrar_fila_pivote(tabla, columna_pivote, tolerancia=1e-6):
    """
    Busca la fila pivote usando la minima razon positiva:
    LD / valor_columna_pivote

    Parametros:
        tabla         : tabla simplex actual
        columna_pivote: indice de la columna pivote
        tolerancia    : margen para considerar un valor como cero (default 1e-6)
    """

    indice_ld = len(tabla[0]) - 1
    menor_razon = float("inf")
    fila_pivote = -1

    print("\nCALCULO DE RAZONES:")

    for i in range(1, len(tabla)):
        valor_columna = tabla[i][columna_pivote]
        lado_derecho = tabla[i][indice_ld]

        # Solo participan filas con valor positivo en la columna pivote (fuera de tolerancia)
        if valor_columna > tolerancia:
            razon = lado_derecho / valor_columna
            print(f"  Fila {tabla[i][0]}: {lado_derecho} / {valor_columna} = {razon}")

            if razon < menor_razon:
                menor_razon = razon
                fila_pivote = i
        else:
            print(f"  Fila {tabla[i][0]}: no participa porque {valor_columna} no es > 0")

    return fila_pivote, menor_razon


# ----------------------------------------------------------
# FUNCION: hacer pivoteo
# ----------------------------------------------------------
def pivotear(tabla, fila_pivote, columna_pivote, columnas, tolerancia=1e-6):
    """
    Realiza el pivoteo:
    1. Divide la fila pivote por el pivote
    2. Hace ceros en el resto de filas
    3. Cambia la variable basica

    Parametros:
        tabla         : tabla simplex actual
        fila_pivote   : indice de la fila pivote
        columna_pivote: indice de la columna pivote
        columnas      : lista de nombres de columnas
        tolerancia    : margen para considerar un valor como cero (default 1e-6)
    """

    # Copia manual de la tabla
    nueva_tabla = []
    for fila in tabla:
        nueva_fila = []
        for valor in fila:
            nueva_fila.append(valor)
        nueva_tabla.append(nueva_fila)

    pivote = nueva_tabla[fila_pivote][columna_pivote]

    # Dividir fila pivote por el pivote
    for j in range(1, len(nueva_tabla[fila_pivote])):
        nueva_tabla[fila_pivote][j] = nueva_tabla[fila_pivote][j] / pivote

    # Actualizar variable basica
    nueva_tabla[fila_pivote][0] = columnas[columna_pivote]

    # Hacer ceros en las demas filas
    for i in range(len(nueva_tabla)):
        if i != fila_pivote:
            factor = nueva_tabla[i][columna_pivote]

            # Solo operamos si el factor es distinto de cero (fuera de tolerancia)
            if abs(factor) > tolerancia:
                for j in range(1, len(nueva_tabla[i])):
                    nueva_tabla[i][j] = nueva_tabla[i][j] - factor * nueva_tabla[fila_pivote][j]

    return nueva_tabla


# ----------------------------------------------------------
# FUNCION: extraer solucion final
# ----------------------------------------------------------
def obtener_solucion(columnas, tabla):
    """
    Extrae el valor final de todas las variables y de Z.
    """
    solucion = {}

    # Variables entre x1 ... h_m
    nombres_variables = columnas[2:-1]

    # Inicialmente todas valen 0
    for var in nombres_variables:
        solucion[var] = 0

    indice_ld = len(columnas) - 1

    # Si una variable esta en la base, vale lo que esta en LD
    for i in range(1, len(tabla)):
        variable_basica = tabla[i][0]
        if variable_basica in solucion:
            solucion[variable_basica] = tabla[i][indice_ld]

    # Valor final de Z
    solucion["Z"] = tabla[0][indice_ld]

    return solucion


# ----------------------------------------------------------
# FUNCION: resolver con simplex normal
# ----------------------------------------------------------
def resolver_simplex(c, A, b, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Resuelve completamente el problema por simplex normal.
    """

    es_min = (tipo_optimizacion == "min")
    if es_min:
        c = [-coef for coef in c]

    columnas, tabla = construir_tabla_inicial(c, A, b)

    print("\n" + "=" * 70)
    print("SE USARA EL METODO SIMPLEX NORMAL")
    print("=" * 70)

    imprimir_tabla(columnas, tabla, "TABLA INICIAL")

    iteracion = 1

    while True:
        print(f"\n{'=' * 25} ITERACION {iteracion} {'=' * 25}")

        columna_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        # Si no hay negativos en Z, se detiene
        if columna_pivote == -1:
            print("\nYa no hay coeficientes negativos en la fila Z.")
            print("La solucion actual es optima.")
            break

        print(f"\nVariable entrante: {columnas[columna_pivote]}")
        print(f"Columna pivote (indice Python): {columna_pivote}")
        print(f"Valor en Z: {tabla[0][columna_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, columna_pivote, tolerancia)

        if fila_pivote == -1:
            print("\nNo existe fila pivote.")
            print("El problema puede ser no acotado.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][columna_pivote]}")

        tabla = pivotear(tabla, fila_pivote, columna_pivote, columnas, tolerancia)

        imprimir_tabla(columnas, tabla, f"TABLA DESPUES DE ITERACION {iteracion}")

        iteracion += 1

    solucion = obtener_solucion(columnas, tabla)

    if es_min:
        solucion["Z"] = -solucion["Z"]

    print("\n" + "=" * 70)
    print("SOLUCION FINAL")
    print("=" * 70)

    for variable, valor in solucion.items():
        if isinstance(valor, float):
            print(f"{variable} = {valor:.2f}")
        else:
            print(f"{variable} = {valor}")

    return solucion


# ----------------------------------------------------------
# FUNCION: resolver con dos fases
# ----------------------------------------------------------
def resolver_dos_fases(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Resuelve el problema de programacion lineal usando el metodo de dos fases.
    Se usa cuando hay restricciones >= o = que requieren variables artificiales.

    Parametros:
        c                : lista de coeficientes de la funcion objetivo
        A                : matriz de coeficientes de las restricciones
        b                : lista de lados derechos
        signos           : lista de signos ["<=", ">=", "="]
        tipo_optimizacion: "max" o "min" (default "max")
        tolerancia       : margen de error numerico (default 1e-6)
    """

    print("\n" + "=" * 70)
    print("SE USARA EL METODO DE DOS FASES")
    print("=" * 70)

    n = len(c)
    m = len(A)

    # ----------------------------------------------------------
    # PREPARACION PREVIA
    # Si es minimizacion, convertimos a maximizacion internamente
    # multiplicando los coeficientes por -1. Al final revertimos el signo de Z.
    # ----------------------------------------------------------
    es_min = (tipo_optimizacion == "min")
    if es_min:
        c = [-coef for coef in c]

    # ----------------------------------------------------------
    # PASO 1 - Identificar que variables agregar por restriccion
    # <= : variable de holgura h (coef +1)
    # >= : variable de exceso e (coef -1) + variable artificial a (coef +1)
    # =  : solo variable artificial a (coef +1)
    # ----------------------------------------------------------

    # Mapeamos cada restriccion con las variables que le corresponden
    # Cada elemento es (indice_restriccion, nombre_variable)
    h_asignaciones = []  # holguras
    e_asignaciones = []  # excesos
    a_asignaciones = []  # artificiales

    h_num = 0
    e_num = 0
    a_num = 0

    for i, signo in enumerate(signos):
        if signo == "<=":
            h_num += 1
            h_asignaciones.append((i, f"h{h_num}"))
        elif signo == ">=":
            e_num += 1
            a_num += 1
            e_asignaciones.append((i, f"e{e_num}"))
            a_asignaciones.append((i, f"a{a_num}"))
        elif signo == "=":
            a_num += 1
            a_asignaciones.append((i, f"a{a_num}"))

    # ----------------------------------------------------------
    # PASO 2 - Construir columnas y tabla de Fase 1
    # Orden: VB, W, x1..xn, h1..hh, e1..ee, a1..aa, LD
    # ----------------------------------------------------------
    columnas = ["VB", "W"]
    for i in range(n):
        columnas.append(f"x{i+1}")
    for (_, nombre) in h_asignaciones:
        columnas.append(nombre)
    for (_, nombre) in e_asignaciones:
        columnas.append(nombre)
    for (_, nombre) in a_asignaciones:
        columnas.append(nombre)
    columnas.append("LD")

    # Fila W: coef 1 en W, 0 en x/h/e, 1 en cada artificial, 0 en LD
    fila_w = ["W", 1]
    for _ in range(n):
        fila_w.append(0)
    for _ in h_asignaciones:
        fila_w.append(0)
    for _ in e_asignaciones:
        fila_w.append(0)
    for _ in a_asignaciones:
        fila_w.append(1)
    fila_w.append(0)

    tabla = [fila_w]

    # Filas de restricciones
    for i in range(m):
        # Variable basica inicial: artificial si >= o =, holgura si <=
        if signos[i] == "<=":
            vb = next(nombre for (ri, nombre) in h_asignaciones if ri == i)
        else:
            vb = next(nombre for (ri, nombre) in a_asignaciones if ri == i)

        fila = [vb, 0]  # VB y columna W (siempre 0 en restricciones)

        # Coeficientes de las variables de decision
        for j in range(n):
            fila.append(float(A[i][j]))

        # Coeficientes de holguras: 1 si es la holgura de esta fila, 0 si no
        for (ri, _) in h_asignaciones:
            fila.append(1.0 if ri == i else 0.0)

        # Coeficientes de excesos: -1 si es el exceso de esta fila, 0 si no
        for (ri, _) in e_asignaciones:
            fila.append(-1.0 if ri == i else 0.0)

        # Coeficientes de artificiales: 1 si es la artificial de esta fila, 0 si no
        for (ri, _) in a_asignaciones:
            fila.append(1.0 if ri == i else 0.0)

        fila.append(float(b[i]))  # Lado derecho
        tabla.append(fila)

    # ----------------------------------------------------------
    # PASO 3 - Eliminacion gaussiana en fila W
    # Para cada artificial que esta en la base, restamos su fila de W
    # multiplicada por el coeficiente de esa artificial en W.
    # Esto asegura que las variables basicas tengan coeficiente 0 en W.
    # ----------------------------------------------------------
    for i in range(1, len(tabla)):
        vb_actual = tabla[i][0]
        es_artificial = any(nombre == vb_actual for (_, nombre) in a_asignaciones)
        if es_artificial:
            col_idx = columnas.index(vb_actual)
            coef_en_w = tabla[0][col_idx]
            if not math.isclose(coef_en_w, 0, rel_tol=tolerancia, abs_tol=tolerancia):
                for j in range(1, len(tabla[0])):
                    tabla[0][j] = tabla[0][j] - coef_en_w * tabla[i][j]

    imprimir_tabla(columnas, tabla, "TABLA INICIAL FASE 1 (tras eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 4 - Iterar simplex en Fase 1
    # Iteramos hasta que no haya negativos en la fila W.
    # ----------------------------------------------------------
    iteracion = 1
    while True:
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en W. Fin de Fase 1.")
            break

        print(f"\nVariable entrante: {columnas[col_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado en Fase 1.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Razon minima positiva: {razon_minima}")

        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 1 - ITERACION {iteracion}")
        iteracion += 1

    # ----------------------------------------------------------
    # PASO 5 - Verificar factibilidad
    # Si el valor de W al final no es (casi) cero, no hay solucion factible.
    # ----------------------------------------------------------
    w_final = tabla[0][-1]
    if abs(w_final) > tolerancia:
        print("\nEl problema no tiene solucion factible")
        return None

    # ----------------------------------------------------------
    # PASO 6 - Construir tabla de Fase 2
    # Eliminamos las columnas artificiales y reemplazamos la fila W por Z.
    # ----------------------------------------------------------
    nombres_artificiales = [nombre for (_, nombre) in a_asignaciones]
    indices_artificiales = [columnas.index(nombre) for nombre in nombres_artificiales]

    # Conservamos solo las columnas que no sean artificiales
    indices_a_conservar = [j for j in range(len(columnas)) if j not in indices_artificiales]

    columnas_f2 = [columnas[j] for j in indices_a_conservar]
    columnas_f2[1] = "Z"  # Reemplazamos "W" por "Z"

    tabla_f2 = []
    for fila in tabla:
        nueva_fila = [fila[j] for j in indices_a_conservar]
        tabla_f2.append(nueva_fila)

    # Construimos la nueva fila Z con los coeficientes originales de la funcion objetivo
    # Formato: Z=1 en columna Z, -c[i] en cada xi, 0 en holguras y excesos, 0 en LD
    fila_z = ["Z", 1]
    for coef in c:
        fila_z.append(-coef)
    for _ in h_asignaciones:
        fila_z.append(0)
    for _ in e_asignaciones:
        fila_z.append(0)
    fila_z.append(0)  # LD

    tabla_f2[0] = fila_z

    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (antes de eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 7 - Eliminacion gaussiana en fila Z
    # Para cada variable de decision que este en la base, limpiamos su
    # columna en la fila Z restando la fila correspondiente.
    # ----------------------------------------------------------
    for i in range(1, len(tabla_f2)):
        vb_actual = tabla_f2[i][0]
        if vb_actual in columnas_f2:
            col_idx = columnas_f2.index(vb_actual)
            coef_en_z = tabla_f2[0][col_idx]
            if not math.isclose(coef_en_z, 0, rel_tol=tolerancia, abs_tol=tolerancia):
                for j in range(1, len(tabla_f2[0])):
                    tabla_f2[0][j] = tabla_f2[0][j] - coef_en_z * tabla_f2[i][j]

    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (tras eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 8 - Iterar simplex en Fase 2
    # ----------------------------------------------------------
    columnas = columnas_f2
    tabla = tabla_f2

    iteracion = 1
    while True:
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en Z. Solucion optima encontrada.")
            break

        print(f"\nVariable entrante: {columnas[col_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Razon minima positiva: {razon_minima}")

        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 2 - ITERACION {iteracion}")
        iteracion += 1

    # ----------------------------------------------------------
    # PASO 9 - Extraer y mostrar solucion
    # Si era minimizacion, el Z interno es el negativo del real, lo revertimos.
    # ----------------------------------------------------------
    solucion = obtener_solucion(columnas, tabla)

    if es_min:
        solucion["Z"] = -solucion["Z"]

    print("\n" + "=" * 70)
    print("SOLUCION FINAL")
    print("=" * 70)

    for variable, valor in solucion.items():
        if isinstance(valor, float):
            print(f"{variable} = {valor:.2f}")
        else:
            print(f"{variable} = {valor}")

    return solucion


# ----------------------------------------------------------
# FUNCION PRINCIPAL DEL PROGRAMA
# ----------------------------------------------------------
def resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Decide automaticamente que metodo usar y lo ejecuta.

    Parametros:
        c                : coeficientes de la funcion objetivo
        A                : matriz de restricciones
        b                : lados derechos
        signos           : lista de signos de cada restriccion
        tipo_optimizacion: "max" o "min" (default "max")
        tolerancia       : margen de error numerico (default 1e-6)
    """

    metodo = detectar_metodo(signos, b, tolerancia)

    print("\n" + "=" * 70)
    print("DETECCION AUTOMATICA DEL METODO")
    print("=" * 70)
    print(f"Metodo detectado: {metodo}")

    if metodo == "simplex":
        return resolver_simplex(c, A, b, tipo_optimizacion, tolerancia)
    else:
        return resolver_dos_fases(c, A, b, signos, tipo_optimizacion, tolerancia)


# ==========================================================
# EJEMPLO 1: CASO SIMPLEX NORMAL
# Resultado esperado: x1=2, x2=6, Z=360000
# ==========================================================

c = [30000, 50000]

A = [
    [1, 0],
    [0, 2],
    [3, 2]
]

b = [4, 12, 18]

signos = ["<=", "<=", "<="]

resolver_programacion_lineal(c, A, b, signos)


# ==========================================================
# EJEMPLO 2: DOS FASES MINIMIZACION
# Resultado esperado: x1=3, x2=2, Z=0.66
# ==========================================================

c = [0.12, 0.15]

A = [
    [60, 60],
    [12, 6],
    [10, 30]
]

b = [300, 36, 90]

signos = [">=", ">=", ">="]

resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion="min")
