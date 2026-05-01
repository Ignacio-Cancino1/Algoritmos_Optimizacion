import math


# Decide si usar simplex normal o dos fases segun los signos y lados derechos
def detectar_metodo(signos, b, tolerancia=1e-6):
    for signo in signos:
        if signo == ">=" or signo == "=":
            return "dos_fases"
    for lado_derecho in b:
        if lado_derecho < 0 and not math.isclose(lado_derecho, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            return "dos_fases"
    return "simplex"


# Arma la tabla inicial del simplex para restricciones <= con LD positivo
def construir_tabla_inicial(c, A, b):
    n = len(c)  # numero de variables de decision
    m = len(A)  # numero de restricciones

    # Encabezados: VB, Z, x1..xn, h1..hm, LD
    columnas = ["VB", "Z"]
    for i in range(n):
        columnas.append(f"x{i+1}")
    for i in range(m):
        columnas.append(f"h{i+1}")
    columnas.append("LD")

    # Fila Z: coeficientes negados porque la ecuacion es Z - c1*x1 - ... = 0
    fila_z = ["Z", 1]
    for coef in c:
        fila_z.append(-coef)
    for _ in range(m):
        fila_z.append(0)
    fila_z.append(0)

    tabla = [fila_z]

    # Una fila por restriccion, con holguras formando una matriz identidad
    for i in range(m):
        fila = [f"h{i+1}", 0]
        for valor in A[i]:
            fila.append(valor)
        for j in range(m):
            fila.append(1 if i == j else 0)
        fila.append(b[i])
        tabla.append(fila)

    return columnas, tabla


# Imprime la tabla con columnas alineadas
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


# Busca la columna con el coeficiente mas negativo en la fila objetivo (criterio de entrada)
def encontrar_columna_pivote(tabla, columnas, tolerancia=1e-6):
    fila_z = tabla[0]
    inicio = 2          # salta VB y Z/W
    fin = len(columnas) - 1  # salta LD

    menor_valor = 0
    indice_pivote = -1  # -1 significa que no hay candidato (solucion optima)

    for j in range(inicio, fin):
        valor = fila_z[j]
        if valor < menor_valor and not math.isclose(valor, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            menor_valor = valor
            indice_pivote = j

    return indice_pivote


# Busca la fila con la minima razon LD/columna_pivote (criterio de salida)
def encontrar_fila_pivote(tabla, columna_pivote, tolerancia=1e-6):
    indice_ld = len(tabla[0]) - 1
    menor_razon = float("inf")
    fila_pivote = -1

    print("\nCALCULO DE RAZONES:")
    for i in range(1, len(tabla)):
        valor_columna = tabla[i][columna_pivote]
        lado_derecho = tabla[i][indice_ld]

        if valor_columna > tolerancia:
            razon = lado_derecho / valor_columna
            print(f"  Fila {tabla[i][0]}: {lado_derecho} / {valor_columna} = {razon}")
            if razon < menor_razon:
                menor_razon = razon
                fila_pivote = i
        else:
            print(f"  Fila {tabla[i][0]}: no participa porque {valor_columna} no es > 0")

    return fila_pivote, menor_razon


# Realiza el pivoteo de Gauss-Jordan para actualizar la tabla
def pivotear(tabla, fila_pivote, columna_pivote, columnas, tolerancia=1e-6):
    nueva_tabla = [[valor for valor in fila] for fila in tabla]

    pivote = nueva_tabla[fila_pivote][columna_pivote]

    # Paso 1: dividir la fila pivote por el pivote para dejar un 1
    for j in range(1, len(nueva_tabla[fila_pivote])):
        nueva_tabla[fila_pivote][j] = nueva_tabla[fila_pivote][j] / pivote

    # Actualizar el nombre de la variable basica en la fila pivote
    nueva_tabla[fila_pivote][0] = columnas[columna_pivote]

    # Paso 2: hacer cero en la columna pivote para todas las demas filas
    for i in range(len(nueva_tabla)):
        if i != fila_pivote:
            factor = nueva_tabla[i][columna_pivote]
            if abs(factor) > tolerancia:
                for j in range(1, len(nueva_tabla[i])):
                    nueva_tabla[i][j] = nueva_tabla[i][j] - factor * nueva_tabla[fila_pivote][j]

    return nueva_tabla


# Lee los valores de las variables desde la tabla final
def obtener_solucion(columnas, tabla):
    solucion = {}
    nombres_variables = columnas[2:-1]

    # Las variables no basicas valen 0
    for var in nombres_variables:
        solucion[var] = 0

    indice_ld = len(columnas) - 1

    # Las variables basicas toman el valor de su LD
    for i in range(1, len(tabla)):
        variable_basica = tabla[i][0]
        if variable_basica in solucion:
            solucion[variable_basica] = tabla[i][indice_ld]

    solucion["Z"] = tabla[0][indice_ld]
    return solucion


# Muestra el sistema de ecuaciones con las variables auxiliares agregadas
def imprimir_forma_aumentada(c_original, A, b, h_asignaciones, e_asignaciones, a_asignaciones, tipo_optimizacion):
    n = len(c_original)
    tipo_str = "Maximizar" if tipo_optimizacion == "max" else "Minimizar"

    print(f"\nFORMA AUMENTADA:")
    print(f"{tipo_str} Z")
    print("Sujeto a:")

    # Fila de la funcion objetivo
    terminos_obj = []
    for i in range(n):
        coef = c_original[i]
        if not math.isclose(coef, 0, abs_tol=1e-9):
            terminos_obj.append(f"- {coef}·x{i+1}")
    print(f"  Z {' '.join(terminos_obj)} = 0")

    # Una ecuacion por restriccion
    for i in range(len(A)):
        terminos = []
        for j in range(n):
            coef = A[i][j]
            if math.isclose(coef, 0, abs_tol=1e-9):
                continue
            if math.isclose(coef, 1.0, abs_tol=1e-9):
                terminos.append(f"x{j+1}")
            elif math.isclose(coef, -1.0, abs_tol=1e-9):
                terminos.append(f"-x{j+1}")
            else:
                terminos.append(f"{coef}·x{j+1}")

        for (ri, nombre) in h_asignaciones:
            if ri == i:
                terminos.append(f"+ {nombre}")
        for (ri, nombre) in e_asignaciones:
            if ri == i:
                terminos.append(f"- {nombre}")
        for (ri, nombre) in a_asignaciones:
            if ri == i:
                terminos.append(f"+ {nombre}")

        print(f"  {' + '.join(terminos[:1])}{(' ' + ' '.join(terminos[1:])) if len(terminos) > 1 else ''} = {b[i]}")


# Si algun LD es negativo, multiplica esa restriccion por -1 e invierte su signo
def normalizar_lados_derechos(A, b, signos):
    inversion_signo = {"<=": ">=", ">=": "<=", "=": "="}

    A_nuevo = []
    b_nuevo = []
    signos_nuevo = []

    for i in range(len(b)):
        if b[i] < 0:
            signo_anterior = signos[i]
            signo_nuevo = inversion_signo[signo_anterior]
            A_nuevo.append([-coef for coef in A[i]])
            b_nuevo.append(-b[i])
            signos_nuevo.append(signo_nuevo)
            print(f"  [Normalizacion] Restriccion {i+1}: LD negativo → se multiplico por -1 y el signo cambio de '{signo_anterior}' a '{signo_nuevo}'")
        else:
            A_nuevo.append(A[i][:])
            b_nuevo.append(b[i])
            signos_nuevo.append(signos[i])

    return A_nuevo, b_nuevo, signos_nuevo


# Resuelve el problema usando simplex estandar (solo restricciones <=)
def resolver_simplex(c, A, b, tipo_optimizacion="max", tolerancia=1e-6):
    c_original = c[:]

    # Para minimizar: se niega c y se maximiza; al final se revierte el signo de Z
    es_min = (tipo_optimizacion == "min")
    if es_min:
        c = [-coef for coef in c]

    A, b, signos_normalizados = normalizar_lados_derechos(A, b, ["<="] * len(b))
    if any(s != "<=" for s in signos_normalizados):
        print("\nTras normalizar LDs negativos, hay restricciones >= que requieren dos fases.")
        print("Redirigiendo automaticamente al metodo de dos fases...")
        return resolver_dos_fases(c_original, A, b, signos_normalizados, tipo_optimizacion, tolerancia)

    print("\nPREPARACION DE VARIABLES:")
    for i in range(len(b)):
        print(f"  Restriccion {i+1} (<=): se agrega variable de holgura h{i+1}")

    nombres_h = [f"h{i+1}" for i in range(len(b))]
    print(f"\n  Variables de holgura agregadas: {', '.join(nombres_h)}")
    print(f"  Variables de exceso agregadas : ninguna")
    print(f"  Variables artificiales agregadas: ninguna")

    terminos_z = ' + '.join(f"{c_original[i]}·x{i+1}" for i in range(len(c_original)))
    tipo_str = "Maximizar" if not es_min else "Minimizar"
    print(f"\nRESOLVIENDO: {tipo_str} Z = {terminos_z}")

    columnas, tabla = construir_tabla_inicial(c, A, b)

    print("\n" + "=" * 70)
    print("SE USARA EL METODO SIMPLEX NORMAL")
    print("=" * 70)

    h_asign_simplex = [(i, f"h{i+1}") for i in range(len(b))]
    imprimir_forma_aumentada(c_original, A, b, h_asign_simplex, [], [], tipo_optimizacion)
    imprimir_tabla(columnas, tabla, "TABLA INICIAL")

    iteracion = 1
    while True:
        print(f"\n{'=' * 25} ITERACION {iteracion} {'=' * 25}")

        # Buscar variable entrante (columna pivote)
        columna_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        if columna_pivote == -1:
            print("\nYa no hay coeficientes negativos en la fila Z.")
            print("La solucion actual es optima.")
            break

        print(f"\nVariable entrante: {columnas[columna_pivote]}")
        print(f"Columna pivote (indice Python): {columna_pivote}")
        print(f"Valor en Z: {tabla[0][columna_pivote]}")

        # Buscar variable saliente (fila pivote)
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


# Resuelve el problema usando el metodo de dos fases (para restricciones >= o =)
def resolver_dos_fases(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    print("\n" + "=" * 70)
    print("SE USARA EL METODO DE DOS FASES")
    print("=" * 70)

    n = len(c)
    m = len(A)

    c_original = c[:]
    es_min = (tipo_optimizacion == "min")
    if es_min:
        c = [-coef for coef in c]

    A, b, signos = normalizar_lados_derechos(A, b, signos)

    # Clasificar que variables auxiliares agregar segun el tipo de restriccion
    h_asignaciones = []  # holguras  para <=
    e_asignaciones = []  # excesos   para >=
    a_asignaciones = []  # artificiales para >= y =

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

    print("\nPREPARACION DE VARIABLES:")
    for i, signo in enumerate(signos):
        if signo == "<=":
            nombre_h = next(nombre for (ri, nombre) in h_asignaciones if ri == i)
            print(f"  Restriccion {i+1} (<=): se agrega variable de holgura {nombre_h}")
        elif signo == ">=":
            nombre_e = next(nombre for (ri, nombre) in e_asignaciones if ri == i)
            nombre_a = next(nombre for (ri, nombre) in a_asignaciones if ri == i)
            print(f"  Restriccion {i+1} (>=): se agrega variable de exceso {nombre_e} y variable artificial {nombre_a}")
        elif signo == "=":
            nombre_a = next(nombre for (ri, nombre) in a_asignaciones if ri == i)
            print(f"  Restriccion {i+1} (=): se agrega variable artificial {nombre_a}")

    nombres_h = [nombre for (_, nombre) in h_asignaciones]
    nombres_e = [nombre for (_, nombre) in e_asignaciones]
    nombres_a = [nombre for (_, nombre) in a_asignaciones]

    print(f"\n  Variables de holgura agregadas  : {', '.join(nombres_h) if nombres_h else 'ninguna'}")
    print(f"  Variables de exceso agregadas   : {', '.join(nombres_e) if nombres_e else 'ninguna'}")
    print(f"  Variables artificiales agregadas: {', '.join(nombres_a) if nombres_a else 'ninguna'}")

    terminos_w = ' + '.join(nombres_a)
    print(f"\nFASE 1: Minimizar W = {terminos_w}")

    # --- Construir tabla de Fase 1 ---
    # Orden de columnas: VB, W, x1..xn, holguras, excesos, artificiales, LD
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

    # Fila W: coeficiente 1 en cada artificial (W = suma de artificiales)
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

    # Filas de restricciones: base inicial con holguras (<=) o artificiales (>= y =)
    for i in range(m):
        if signos[i] == "<=":
            vb = next(nombre for (ri, nombre) in h_asignaciones if ri == i)
        else:
            vb = next(nombre for (ri, nombre) in a_asignaciones if ri == i)

        fila = [vb, 0]
        for j in range(n):
            fila.append(float(A[i][j]))
        for (ri, _) in h_asignaciones:
            fila.append(1.0 if ri == i else 0.0)
        for (ri, _) in e_asignaciones:
            fila.append(-1.0 if ri == i else 0.0)  # exceso resta en la ecuacion
        for (ri, _) in a_asignaciones:
            fila.append(1.0 if ri == i else 0.0)
        fila.append(float(b[i]))
        tabla.append(fila)

    imprimir_forma_aumentada(c_original, A, b, h_asignaciones, e_asignaciones, a_asignaciones, tipo_optimizacion)
    imprimir_tabla(columnas, tabla, "TABLA INICIAL FASE 1 (antes de eliminacion gaussiana)")

    # Eliminacion gaussiana en fila W: anular columnas de artificiales que estan en la base
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

    # --- Fase 1: iterar simplex sobre W hasta que W = 0 ---
    iteracion = 1
    while True:
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en W. Fin de Fase 1.")
            print("\nRESULTADO FASE 1:")
            w_final_preview = tabla[0][-1]
            if abs(w_final_preview) <= tolerancia:
                print(f"  W = {w_final_preview:.4f} → El problema ES factible, se puede continuar a Fase 2.")
            else:
                print(f"  W = {w_final_preview:.4f} → El problema NO es factible, no existe solucion.")
            break

        print(f"\nVariable entrante: {columnas[col_pivote]}")
        print(f"Columna pivote (indice Python): {col_pivote}")
        print(f"Valor en fila objetivo: {tabla[0][col_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado en Fase 1.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][col_pivote]}")

        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 1 - ITERACION {iteracion}")
        iteracion += 1

    # Si W > 0 al terminar, no existe solucion factible
    w_final = tabla[0][-1]
    if abs(w_final) > tolerancia:
        print("\nEl problema no tiene solucion factible")
        return None

    # --- Transicion a Fase 2 ---
    # Se eliminan las columnas artificiales y se reemplaza la fila W por la fila Z real
    print("\nTRANSICION A FASE 2:")
    print(f"  Se eliminan las columnas artificiales: {', '.join(nombres_a)}")

    tipo_str = "Maximizar" if not es_min else "Minimizar"
    c_original = [-coef for coef in c] if es_min else c
    terminos_z = ' + '.join(f"{c_original[i]}·x{i+1}" for i in range(n))
    print(f"  Se restaura la funcion objetivo original: {tipo_str} Z = {terminos_z}")
    print(f"  Se aplica eliminacion gaussiana en fila Z para limpiar variables basicas en la base...")
    print("\nFASE 2: Optimizar funcion objetivo original")

    # Filtrar columnas artificiales de la tabla
    nombres_artificiales = [nombre for (_, nombre) in a_asignaciones]
    indices_artificiales = [columnas.index(nombre) for nombre in nombres_artificiales]
    indices_a_conservar = [j for j in range(len(columnas)) if j not in indices_artificiales]

    columnas_f2 = [columnas[j] for j in indices_a_conservar]
    columnas_f2[1] = "Z"

    tabla_f2 = []
    for fila in tabla:
        nueva_fila = [fila[j] for j in indices_a_conservar]
        tabla_f2.append(nueva_fila)

    # Nueva fila Z con los coeficientes de la funcion objetivo original
    fila_z = ["Z", 1]
    for coef in c:
        fila_z.append(-coef)
    for _ in h_asignaciones:
        fila_z.append(0)
    for _ in e_asignaciones:
        fila_z.append(0)
    fila_z.append(0)

    tabla_f2[0] = fila_z

    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (antes de eliminacion gaussiana)")

    # Eliminacion gaussiana en fila Z: limpiar columnas de variables que ya estan en la base
    for i in range(1, len(tabla_f2)):
        vb_actual = tabla_f2[i][0]
        if vb_actual in columnas_f2:
            col_idx = columnas_f2.index(vb_actual)
            coef_en_z = tabla_f2[0][col_idx]
            if not math.isclose(coef_en_z, 0, rel_tol=tolerancia, abs_tol=tolerancia):
                for j in range(1, len(tabla_f2[0])):
                    tabla_f2[0][j] = tabla_f2[0][j] - coef_en_z * tabla_f2[i][j]

    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (tras eliminacion gaussiana)")

    columnas = columnas_f2
    tabla = tabla_f2

    # --- Fase 2: optimizar Z partiendo de la solucion factible de Fase 1 ---
    iteracion = 1
    while True:
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en Z. Solucion optima encontrada.")
            break

        print(f"\nVariable entrante: {columnas[col_pivote]}")
        print(f"Columna pivote (indice Python): {col_pivote}")
        print(f"Valor en fila objetivo: {tabla[0][col_pivote]}")

        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado.")
            return None

        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][col_pivote]}")

        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 2 - ITERACION {iteracion}")
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


# Punto de entrada: detecta el metodo y llama al solver correspondiente
def resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    metodo = detectar_metodo(signos, b, tolerancia)

    print("\n" + "=" * 70)
    print("DETECCION AUTOMATICA DEL METODO")
    print("=" * 70)
    print(f"Metodo detectado: {metodo}")

    if metodo == "simplex":
        return resolver_simplex(c, A, b, tipo_optimizacion, tolerancia)
    else:
        return resolver_dos_fases(c, A, b, signos, tipo_optimizacion, tolerancia)


# Pide todos los datos del problema al usuario por consola con validacion
def pedir_datos():
    print("\n" + "=" * 70)
    print("INGRESO DE DATOS DEL PROBLEMA")
    print("=" * 70)

    while True:
        try:
            n = int(input("\nNumero de variables de decision: "))
            if n > 0:
                break
            print("  Debe ser un entero positivo.")
        except ValueError:
            print("  Entrada invalida. Ingrese un entero positivo.")

    # Coeficientes de la funcion objetivo
    c = []
    for i in range(n):
        while True:
            try:
                coef = float(input(f"  Coeficiente de x{i+1} en la funcion objetivo: "))
                c.append(coef)
                break
            except ValueError:
                print("  Entrada invalida. Ingrese un numero.")

    while True:
        tipo = input("\nTipo de optimizacion (max / min): ").strip().lower()
        if tipo in ("max", "min"):
            tipo_optimizacion = tipo
            break
        print("  Opcion invalida. Ingrese 'max' o 'min'.")

    while True:
        try:
            m = int(input("\nNumero de restricciones: "))
            if m > 0:
                break
            print("  Debe ser un entero positivo.")
        except ValueError:
            print("  Entrada invalida. Ingrese un entero positivo.")

    A = []
    b = []
    signos = []

    # Datos de cada restriccion
    for i in range(m):
        print(f"\n  Restriccion {i+1}:")
        fila = []
        for j in range(n):
            while True:
                try:
                    coef = float(input(f"    Coeficiente de x{j+1}: "))
                    fila.append(coef)
                    break
                except ValueError:
                    print("    Entrada invalida. Ingrese un numero.")
        A.append(fila)

        while True:
            try:
                ld = float(input(f"    Lado derecho (LD): "))
                b.append(ld)
                break
            except ValueError:
                print("    Entrada invalida. Ingrese un numero.")

        while True:
            signo = input(f"    Signo (<=, >= o =): ").strip()
            if signo in ("<=", ">=", "="):
                signos.append(signo)
                break
            print("    Signo invalido. Ingrese '<=', '>=' o '='.")

    return c, A, b, signos, tipo_optimizacion


c, A, b, signos, tipo_optimizacion = pedir_datos()
resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion)
