# ==========================================================
# METODO SIMPLEX CON DETECCION AUTOMATICA DE DOS FASES
# ==========================================================
# Esta version:
# 1. Detecta automaticamente si el problema usa:
#    - simplex normal
#    - metodo de dos fases
# 2. Resuelve completamente el caso simplex normal
# 3. Deja preparado el bloque para dos fases
# ==========================================================
#Determinar tipo de problema 
#verificar lados derechos (no negativos)
#agregar variables 
#Holgura 
#Exceso y artificiales 
#Tengo que aplicar notacion cientifica para calcular el tamaño de la tabla de manera automatica 
#metodo de 2 fases
# 
# ver el tema del casi cero 
# Si |A-B|< tolerancia Como parametro (Puede tener un valor por defecto) 

#Probar con valores grandes, ya sea elevados positivos o negativos 
# ----------------------------------------------------------
# FUNCION: detectar que metodo corresponde
# ----------------------------------------------------------
def detectar_metodo(signos, b):
    """
    Detecta automaticamente si el problema debe resolverse con:
    - simplex normal
    - metodo de dos fases

    Reglas:
    - Si aparece >= o =  --> dos fases
    - Si algun LD es negativo --> por seguridad dos fases

    Parametros:
        signos: lista de signos de restricciones
                Ejemplo: ["<=", "<=", ">="]
        b: lista de lados derechos

    Retorna:
        "simplex" o "dos_fases"
    """
    for signo in signos:
        if signo == ">=" or signo == "=":
            return "dos_fases"

    for lado_derecho in b:
        if lado_derecho < 0:
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
def encontrar_columna_pivote(tabla, columnas):
    """
    Busca la columna con el valor mas negativo en la fila Z.
    Si no hay negativos, retorna -1.
    """
    fila_z = tabla[0]

    # Desde x1 hasta antes de LD
    inicio = 2
    fin = len(columnas) - 1

    menor_valor = 0
    indice_pivote = -1

    for j in range(inicio, fin):
        valor = fila_z[j]
        if valor < menor_valor:
            menor_valor = valor
            indice_pivote = j

    return indice_pivote


# ----------------------------------------------------------
# FUNCION: encontrar fila pivote
# ----------------------------------------------------------
def encontrar_fila_pivote(tabla, columna_pivote):
    """
    Busca la fila pivote usando la minima razon positiva:
    LD / valor_columna_pivote
    """

    indice_ld = len(tabla[0]) - 1
    menor_razon = float("inf")
    fila_pivote = -1

    print("\nCALCULO DE RAZONES:")

    for i in range(1, len(tabla)):
        valor_columna = tabla[i][columna_pivote]
        lado_derecho = tabla[i][indice_ld]

        if valor_columna > 0:
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
def pivotear(tabla, fila_pivote, columna_pivote, columnas):
    """
    Realiza el pivoteo:
    1. Divide la fila pivote por el pivote
    2. Hace ceros en el resto de filas
    3. Cambia la variable basica
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

            if factor != 0:
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
def resolver_simplex(c, A, b):
    """
    Resuelve completamente el problema por simplex normal.
    """

    columnas, tabla = construir_tabla_inicial(c, A, b)

    print("\n" + "=" * 70)
    print("SE USARA EL METODO SIMPLEX NORMAL")
    print("=" * 70)

    imprimir_tabla(columnas, tabla, "TABLA INICIAL")

    iteracion = 1

    while True:
        print(f"\n{'=' * 25} ITERACION {iteracion} {'=' * 25}")

        columna_pivote = encontrar_columna_pivote(tabla, columnas)

        # Si no hay negativos en Z, se detiene
        if columna_pivote == -1:
            print("\nYa no hay coeficientes negativos en la fila Z.")
            print("La solucion actual es optima.")
            break

        print(f"\nVariable entrante: {columnas[columna_pivote]}")
        print(f"Columna pivote (indice Python): {columna_pivote}")
        print(f"Valor en Z: {tabla[0][columna_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, columna_pivote)

        if fila_pivote == -1:
            print("\nNo existe fila pivote.")
            print("El problema puede ser no acotado.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][columna_pivote]}")

        tabla = pivotear(tabla, fila_pivote, columna_pivote, columnas)

        imprimir_tabla(columnas, tabla, f"TABLA DESPUES DE ITERACION {iteracion}")

        iteracion += 1

    solucion = obtener_solucion(columnas, tabla)

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
def resolver_dos_fases(c, A, b, signos):
    """
    Bloque preparado para el metodo de dos fases.

    Por ahora solo informa que el problema requiere dos fases.
    La implementacion completa de fase 1 y fase 2 se haria despues.
    """

    print("\n" + "=" * 70)
    print("SE USARA EL METODO DE DOS FASES")
    print("=" * 70)

    print("\nEl problema tiene restricciones que requieren variables")
    print("artificiales o de exceso, por ejemplo '>=' o '='.")
    print("Por eso no puede partir con el simplex normal.")

    print("\nDatos recibidos:")
    print("Funcion objetivo:", c)
    print("Matriz A:")
    for fila in A:
        print(" ", fila)
    print("Signos:", signos)
    print("Lado derecho:", b)

    print("\nAVISO:")
    print("La deteccion automatica ya funciona, pero la resolucion")
    print("completa de fase 1 y fase 2 aun no esta implementada")
    print("en este codigo.")


# ----------------------------------------------------------
# FUNCION PRINCIPAL DEL PROGRAMA
# ----------------------------------------------------------
def resolver_programacion_lineal(c, A, b, signos):
    """
    Decide automaticamente que metodo usar y lo ejecuta.
    """

    metodo = detectar_metodo(signos, b)

    print("\n" + "=" * 70)
    print("DETECCION AUTOMATICA DEL METODO")
    print("=" * 70)
    print(f"Metodo detectado: {metodo}")

    if metodo == "simplex":
        return resolver_simplex(c, A, b)
    else:
        return resolver_dos_fases(c, A, b, signos)


# ==========================================================
# EJEMPLO 1: CASO SIMPLEX NORMAL
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
# SI QUIERES PROBAR DOS FASES, COMENTA EL BLOQUE DE ARRIBA
# Y DESCOMENTA ESTE:
# ==========================================================
"""""
c = [0.12, 0.15]

A = [
    [60, 60],
    [12, 6],
    [10, 30]
]

b = [300, 36, 90]

signos = [">=", ">=", ">="]

resolver_programacion_lineal(c, A, b, signos)
"""""