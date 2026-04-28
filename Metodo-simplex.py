import math

# ==========================================================
# METODO SIMPLEX CON DETECCION AUTOMATICA DE DOS FASES
# ==========================================================


# ----------------------------------------------------------
# FUNCION: detectar que metodo corresponde
# Analiza las restricciones para decidir si basta con el
# simplex estandar o si se necesita el metodo de dos fases.
# ----------------------------------------------------------
def detectar_metodo(signos, b, tolerancia=1e-6):
    """
    Detecta automaticamente si el problema debe resolverse con
    simplex normal o con el metodo de dos fases.

    El simplex normal solo funciona cuando TODAS las restricciones
    son <= con lado derecho positivo, porque en ese caso las variables
    de holgura forman una base inicial factible de forma directa.
    Cualquier >= o = rompe esa propiedad y obliga a usar dos fases.

    Parametros:
        signos    : lista de signos de restricciones ["<=", ">=", ...]
        b         : lista de lados derechos de las restricciones
        tolerancia: margen para comparaciones numericas (default 1e-6)

    Retorna:
        "simplex"   si todas las restricciones son <= con LD positivo
        "dos_fases" si hay alguna >= o = o algun LD negativo
    """
    # Recorremos todos los signos buscando >= o =.
    # Estas restricciones requieren variables artificiales para
    # tener una base inicial, lo que obliga al metodo de dos fases.
    for signo in signos:
        if signo == ">=" or signo == "=":
            return "dos_fases"

    # Si algun lado derecho es negativo (y no es practicamente cero),
    # la restriccion tampoco tiene base factible directa.
    for lado_derecho in b:
        if lado_derecho < 0 and not math.isclose(lado_derecho, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            return "dos_fases"

    # Si ninguna condicion anterior se cumplio, el simplex normal es suficiente.
    return "simplex"


# ----------------------------------------------------------
# FUNCION: construir tabla inicial simplex normal
# Arma la tabla simplex con holguras para problemas
# de maximizacion con restricciones <= y LD positivos.
# ----------------------------------------------------------
def construir_tabla_inicial(c, A, b):
    """
    Construye la tabla inicial del metodo simplex para problemas
    de maximizacion con restricciones <= y lados derechos positivos.

    En el simplex, trabajamos con una tabla donde:
    - La primera fila es la funcion objetivo Z (con coeficientes negados).
    - Las demas filas son las restricciones ampliadas con variables de holgura.
    - La primera columna (VB) indica que variable esta en la base en cada fila.

    Parametros:
        c : lista de coeficientes de la funcion objetivo  [c1, c2, ...]
        A : matriz de coeficientes de las restricciones   [[a11, a12], ...]
        b : lista de lados derechos de las restricciones  [b1, b2, ...]

    Retorna:
        columnas : lista con los nombres de cada columna de la tabla
        tabla    : lista de filas (cada fila es una lista de numeros)
    """

    n = len(c)   # numero de variables de decision (x1, x2, ...)
    m = len(A)   # numero de restricciones (una fila por restriccion)

    # Construimos los encabezados de la tabla en el orden correcto:
    # VB (variable basica), Z (columna de la funcion objetivo),
    # x1..xn (variables de decision), h1..hm (holguras), LD (lado derecho)
    columnas = ["VB", "Z"]

    # Agregamos una columna por cada variable de decision
    for i in range(n):
        columnas.append(f"x{i+1}")

    # Agregamos una columna por cada variable de holgura.
    # Hay una holgura por restriccion (una por fila).
    for i in range(m):
        columnas.append(f"h{i+1}")

    # La ultima columna siempre es el lado derecho (LD)
    columnas.append("LD")

    # Construimos la fila Z (funcion objetivo).
    # En la tabla simplex, la fila Z se escribe como:
    #   Z - c1*x1 - c2*x2 - ... = 0
    # Por eso los coeficientes de las xi van negados.
    # El 1 en la columna Z indica que es la fila objetivo.
    fila_z = ["Z", 1]

    # Negamos cada coeficiente de la funcion objetivo.
    # Si maximizamos Z = 30000*x1 + 50000*x2, en la tabla
    # la fila Z queda: Z - 30000*x1 - 50000*x2 = 0
    for coef in c:
        fila_z.append(-coef)

    # Las holguras no aparecen en la funcion objetivo, su coeficiente es 0
    for _ in range(m):
        fila_z.append(0)

    # El valor inicial de Z es 0 (punto de partida en el origen)
    fila_z.append(0)

    # Iniciamos la tabla con la fila Z como primera fila
    tabla = [fila_z]

    # Construimos una fila por cada restriccion
    for i in range(m):
        # La variable basica inicial de esta restriccion es su holgura h_i.
        # Esto es valido porque para restricciones <=, la holgura representa
        # cuanto "sobra" y empieza valiendo todo el lado derecho.
        fila = [f"h{i+1}", 0]  # VB = holgura, columna Z = 0 (no aparece en restricciones)

        # Copiamos los coeficientes de las variables de decision para esta restriccion
        for valor in A[i]:
            fila.append(valor)

        # Agregamos la matriz identidad para las holguras.
        # La holgura de la restriccion i tiene coeficiente 1 en su fila
        # y 0 en todas las demas. Esto forma la base inicial factible.
        for j in range(m):
            if i == j:
                fila.append(1)   # coeficiente 1: esta es la holgura de esta restriccion
            else:
                fila.append(0)   # coeficiente 0: la holgura de otra restriccion

        # Copiamos el lado derecho de esta restriccion
        fila.append(b[i])

        tabla.append(fila)

    return columnas, tabla


# ----------------------------------------------------------
# FUNCION: imprimir tabla
# Muestra la tabla simplex en formato de columnas alineadas.
# ----------------------------------------------------------
def imprimir_tabla(columnas, tabla, titulo="TABLA SIMPLEX"):
    """
    Imprime la tabla simplex con el titulo indicado, alineando
    cada valor en columnas de ancho fijo para facilitar la lectura.

    Los enteros se muestran sin decimales y los flotantes con 2 decimales.

    Parametros:
        columnas: lista de nombres de columnas (encabezados)
        tabla   : lista de filas con los valores numericos
        titulo  : texto que se imprime como encabezado de la tabla
    """
    # Ancho fijo para cada columna en caracteres
    ancho = 10

    print(f"\n{titulo}:\n")

    # Imprimimos los encabezados de columna, alineados a la derecha
    for col in columnas:
        print(f"{col:>{ancho}}", end="")
    print()

    # Linea separadora entre encabezados y datos
    print("-" * (ancho * len(columnas)))

    # Imprimimos cada fila de la tabla
    for fila in tabla:
        for j, valor in enumerate(fila):
            if j == 0:
                # La primera columna (VB) es siempre un string (nombre de variable)
                print(f"{str(valor):>{ancho}}", end="")
            else:
                # Las demas columnas son numericas
                if isinstance(valor, float):
                    # Los flotantes se muestran con 2 decimales
                    print(f"{valor:>{ancho}.2f}", end="")
                else:
                    # Los enteros (como los 0 y 1 iniciales) sin decimales
                    print(f"{str(valor):>{ancho}}", end="")
        print()


# ----------------------------------------------------------
# FUNCION: encontrar columna pivote
# Elige la variable que entrara a la base en esta iteracion.
# ----------------------------------------------------------
def encontrar_columna_pivote(tabla, columnas, tolerancia=1e-6):
    """
    Busca la columna con el coeficiente mas negativo en la fila objetivo
    (fila Z en simplex, fila W en Fase 1). Esa columna corresponde a la
    variable que mas rapidamente mejora el valor de Z (o W) al entrar
    a la base.

    Si no hay ningun coeficiente negativo en la fila objetivo, la solucion
    actual ya es optima y no hay que seguir iterando.

    Parametros:
        tabla     : tabla simplex actual con todas sus filas
        columnas  : lista de nombres de columnas (para saber el rango valido)
        tolerancia: margen para no tomar como negativo un valor casi cero

    Retorna:
        indice de la columna pivote, o -1 si no hay coeficientes negativos
    """
    # La fila objetivo siempre es la primera fila de la tabla (fila 0)
    fila_z = tabla[0]

    # Buscamos solo entre las columnas de variables (no VB, no Z/W, no LD).
    # El indice 2 salta VB y Z/W; el ultimo indice salta LD.
    inicio = 2
    fin = len(columnas) - 1

    # Iniciamos con 0 como umbral: solo nos interesa algo mas negativo que 0
    menor_valor = 0
    indice_pivote = -1  # -1 significa "no encontrado"

    for j in range(inicio, fin):
        valor = fila_z[j]
        # La columna pivote es la que tiene el valor mas negativo.
        # Usamos math.isclose para no confundir un cero flotante con un negativo.
        # Solo actualizamos si el valor es estrictamente menor que el minimo actual.
        if valor < menor_valor and not math.isclose(valor, 0, rel_tol=tolerancia, abs_tol=tolerancia):
            menor_valor = valor      # nuevo minimo
            indice_pivote = j        # guardamos el indice de esa columna

    return indice_pivote


# ----------------------------------------------------------
# FUNCION: encontrar fila pivote
# Elige la variable que saldra de la base en esta iteracion
# usando la regla de la minima razon positiva.
# ----------------------------------------------------------
def encontrar_fila_pivote(tabla, columna_pivote, tolerancia=1e-6):
    """
    Busca la fila pivote usando la regla de la minima razon positiva:
        razon = LD / valor_en_columna_pivote

    Esta regla garantiza que al introducir la nueva variable basica,
    ninguna variable basica actual se vuelva negativa (infactible).
    Solo participan filas donde el valor en la columna pivote es positivo,
    porque una division por un valor negativo o cero daria resultados invalidos.

    Parametros:
        tabla         : tabla simplex actual con todas sus filas
        columna_pivote: indice de la columna seleccionada como pivote
        tolerancia    : valor minimo para considerar positivo el coeficiente

    Retorna:
        fila_pivote : indice de la fila con la minima razon positiva
        menor_razon : valor numerico de esa razon minima
    """

    # El lado derecho (LD) esta siempre en la ultima posicion de cada fila
    indice_ld = len(tabla[0]) - 1

    # Iniciamos la menor razon como infinito para que cualquier valor la reemplace
    menor_razon = float("inf")
    fila_pivote = -1   # -1 significa "no encontrada"

    print("\nCALCULO DE RAZONES:")

    # Recorremos solo las filas de restricciones (desde la fila 1, saltando Z/W)
    for i in range(1, len(tabla)):
        valor_columna = tabla[i][columna_pivote]   # coeficiente en la columna pivote
        lado_derecho = tabla[i][indice_ld]         # valor del lado derecho de esta fila

        # Solo participan filas con coeficiente estrictamente positivo en la columna pivote.
        # Si el coeficiente es 0 o negativo, la variable no puede entrar por esa fila.
        if valor_columna > tolerancia:
            # La razon LD/columna_pivote indica cuanto puede crecer la variable entrante
            # antes de que esta variable basica se vuelva 0 (su limite de crecimiento)
            razon = lado_derecho / valor_columna
            print(f"  Fila {tabla[i][0]}: {lado_derecho} / {valor_columna} = {razon}")

            # Nos quedamos con la fila que tiene la razon mas pequena (regla del minimo)
            if razon < menor_razon:
                menor_razon = razon
                fila_pivote = i
        else:
            # Esta fila no puede ser pivote porque el coeficiente no es positivo
            print(f"  Fila {tabla[i][0]}: no participa porque {valor_columna} no es > 0")

    return fila_pivote, menor_razon


# ----------------------------------------------------------
# FUNCION: hacer pivoteo
# Transforma la tabla para que la nueva variable basica
# quede en forma canonica (1 en su fila, 0 en las demas).
# ----------------------------------------------------------
def pivotear(tabla, fila_pivote, columna_pivote, columnas, tolerancia=1e-6):
    """
    Realiza el pivoteo de Gauss-Jordan sobre el elemento pivote.

    El pivoteo tiene tres pasos:
    1. Divide la fila pivote por el elemento pivote -> deja un 1 en la posicion pivote.
    2. Resta multiplos de la fila pivote de todas las demas filas -> deja 0 en esa columna.
    3. Actualiza el nombre de la variable basica en la fila pivote.

    El resultado es que la tabla queda en forma canonica para la nueva variable basica,
    lo que permite leer directamente la solucion al final del algoritmo.

    Parametros:
        tabla         : tabla simplex actual
        fila_pivote   : indice de la fila seleccionada como pivote
        columna_pivote: indice de la columna seleccionada como pivote
        columnas      : lista de nombres de columnas (para actualizar VB)
        tolerancia    : margen para no operar cuando el factor es practicamente cero

    Retorna:
        nueva_tabla: tabla actualizada despues del pivoteo
    """

    # Hacemos una copia profunda de la tabla para no modificar la original
    # mientras calculamos los nuevos valores.
    nueva_tabla = []
    for fila in tabla:
        nueva_fila = []
        for valor in fila:
            nueva_fila.append(valor)
        nueva_tabla.append(nueva_fila)

    # El elemento pivote es el valor en la interseccion fila-columna pivote
    pivote = nueva_tabla[fila_pivote][columna_pivote]

    # PASO 1: Dividimos cada elemento de la fila pivote por el pivote.
    # Esto convierte el elemento pivote en 1, que es lo requerido en forma canonica.
    # Empezamos desde j=1 para no tocar la columna VB (j=0 es el nombre).
    for j in range(1, len(nueva_tabla[fila_pivote])):
        nueva_tabla[fila_pivote][j] = nueva_tabla[fila_pivote][j] / pivote

    # PASO 3: Actualizamos el nombre de la variable basica en esta fila.
    # La variable que entra (columna pivote) reemplaza a la que sale (fila pivote).
    nueva_tabla[fila_pivote][0] = columnas[columna_pivote]

    # PASO 2: Para cada fila distinta de la fila pivote, hacemos cero en la columna pivote.
    # La operacion es: fila_i = fila_i - factor * fila_pivote
    # donde factor es el valor que tiene la fila_i en la columna pivote.
    for i in range(len(nueva_tabla)):
        if i != fila_pivote:   # no tocamos la fila pivote que ya procesamos
            factor = nueva_tabla[i][columna_pivote]

            # Solo operamos si el factor es distinto de cero (no tiene sentido restar 0)
            if abs(factor) > tolerancia:
                for j in range(1, len(nueva_tabla[i])):
                    # Restamos el multiplo de la fila pivote para anular este coeficiente
                    nueva_tabla[i][j] = nueva_tabla[i][j] - factor * nueva_tabla[fila_pivote][j]

    return nueva_tabla


# ----------------------------------------------------------
# FUNCION: extraer solucion final
# Lee los valores de las variables directamente desde la
# tabla cuando el algoritmo ha terminado.
# ----------------------------------------------------------
def obtener_solucion(columnas, tabla):
    """
    Extrae los valores finales de todas las variables y del objetivo Z
    a partir de la tabla simplex en su estado final.

    En la tabla final (forma canonica):
    - Las variables basicas (en la columna VB) valen lo que dice su LD.
    - Las variables no basicas valen 0 (no estan en la base).
    - El valor de Z esta en el LD de la fila 0.

    Parametros:
        columnas: lista de nombres de columnas de la tabla final
        tabla   : tabla simplex en su estado optimo

    Retorna:
        solucion: diccionario {nombre_variable: valor, "Z": valor_optimo}
    """
    solucion = {}

    # Las variables del problema son las columnas entre Z/W y LD (indices 2 a -1)
    nombres_variables = columnas[2:-1]

    # Por defecto todas las variables valen 0 (no estan en la base)
    for var in nombres_variables:
        solucion[var] = 0

    # El indice del lado derecho es siempre el ultimo
    indice_ld = len(columnas) - 1

    # Recorremos las filas de restricciones (fila 0 es Z/W, no una variable)
    for i in range(1, len(tabla)):
        variable_basica = tabla[i][0]   # nombre de la variable en la base de esta fila
        # Si esta variable pertenece al problema, leemos su valor del LD
        if variable_basica in solucion:
            solucion[variable_basica] = tabla[i][indice_ld]

    # El valor optimo de Z esta en el LD de la fila objetivo (fila 0)
    solucion["Z"] = tabla[0][indice_ld]

    return solucion


# ----------------------------------------------------------
# FUNCION: imprimir forma aumentada del problema
# Muestra las ecuaciones del sistema ampliado antes de
# construir la tabla, para que el estudiante vea de donde
# salen los valores de la tabla inicial.
# ----------------------------------------------------------
def imprimir_forma_aumentada(c_original, A, b, h_asignaciones, e_asignaciones, a_asignaciones, tipo_optimizacion):
    """
    Imprime el sistema de ecuaciones en forma aumentada.

    La forma aumentada convierte las desigualdades en igualdades
    agregando variables auxiliares segun el tipo de restriccion:
    - Para <=: se agrega una holgura (h) que absorbe el "sobrante" hasta el limite.
    - Para >=: se resta un exceso (e) para eliminar el "sobrante" y se agrega
               una artificial (a) como variable de base inicial valida.
    - Para =:  ya es igualdad, solo se agrega artificial como base inicial.

    Parametros:
        c_original      : coeficientes originales de Z (antes de negar para minimizacion)
        A               : matriz de coeficientes de las restricciones
        b               : lados derechos de las restricciones
        h_asignaciones  : lista de (indice_restriccion, nombre_holgura)
        e_asignaciones  : lista de (indice_restriccion, nombre_exceso)
        a_asignaciones  : lista de (indice_restriccion, nombre_artificial)
        tipo_optimizacion: "max" o "min", para mostrar el encabezado correcto
    """
    n = len(c_original)
    # Texto del tipo de optimizacion para mostrar al usuario
    tipo_str = "Maximizar" if tipo_optimizacion == "max" else "Minimizar"

    print(f"\nFORMA AUMENTADA:")
    print(f"{tipo_str} Z")
    print("Sujeto a:")

    # Construimos la linea de la funcion objetivo.
    # Se pasa Z al lado izquierdo y los ci*xi al derecho con signo negativo:
    # Z - c1*x1 - c2*x2 - ... = 0
    terminos_obj = []
    for i in range(n):
        coef = c_original[i]
        # Solo incluimos el termino si el coeficiente no es (practicamente) cero
        if not math.isclose(coef, 0, abs_tol=1e-9):
            terminos_obj.append(f"- {coef}·x{i+1}")
    print(f"  Z {' '.join(terminos_obj)} = 0")

    # Construimos una linea por cada restriccion del problema
    for i in range(len(A)):
        terminos = []
        for j in range(n):
            coef = A[i][j]
            # Omitimos terminos con coeficiente cero (no aportan nada)
            if math.isclose(coef, 0, abs_tol=1e-9):
                continue
            # Si el coeficiente es exactamente 1, solo escribimos "x1" (no "1·x1")
            if math.isclose(coef, 1.0, abs_tol=1e-9):
                terminos.append(f"x{j+1}")
            # Si es exactamente -1, escribimos "-x1" (no "-1·x1")
            elif math.isclose(coef, -1.0, abs_tol=1e-9):
                terminos.append(f"-x{j+1}")
            else:
                terminos.append(f"{coef}·x{j+1}")

        # Agregamos la holgura de esta restriccion (si la tiene).
        # La holgura suma al lado izquierdo para convertir <= en =
        for (ri, nombre) in h_asignaciones:
            if ri == i:
                terminos.append(f"+ {nombre}")

        # Agregamos el exceso de esta restriccion (si lo tiene).
        # El exceso resta porque convierte >= en = (el exceso es lo que "sobra")
        for (ri, nombre) in e_asignaciones:
            if ri == i:
                terminos.append(f"- {nombre}")

        # Agregamos la artificial de esta restriccion (si la tiene).
        # La artificial siempre suma con coeficiente +1
        for (ri, nombre) in a_asignaciones:
            if ri == i:
                terminos.append(f"+ {nombre}")

        # Imprimimos la ecuacion completa de esta restriccion
        print(f"  {' + '.join(terminos[:1])}{(' ' + ' '.join(terminos[1:])) if len(terminos) > 1 else ''} = {b[i]}")


# ----------------------------------------------------------
# FUNCION: normalizar lados derechos negativos
# Si algun lado derecho es negativo, multiplica esa restriccion
# por -1 e invierte su signo para dejar todos los LD >= 0.
# ----------------------------------------------------------
def normalizar_lados_derechos(A, b, signos):
    """
    Preprocesa las restricciones para garantizar que todos los lados
    derechos sean no negativos, condicion necesaria para construir
    una tabla simplex con una base inicial valida.

    Si b[i] < 0, multiplicar la restriccion por -1 invierte el signo:
      a*x <= -k  ->  -a*x >= k
      a*x >= -k  ->  -a*x <= k
      a*x  = -k  ->  -a*x  = k

    Parametros:
        A     : matriz de coeficientes de las restricciones
        b     : lista de lados derechos
        signos: lista de signos de cada restriccion

    Retorna:
        A_nuevo, b_nuevo, signos_nuevo con todos los LD >= 0
    """
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


# ----------------------------------------------------------
# FUNCION: resolver con simplex normal
# Aplica el algoritmo simplex clasico para problemas
# de maximizacion con restricciones <= y LD positivo.
# ----------------------------------------------------------
def resolver_simplex(c, A, b, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Resuelve un problema de programacion lineal usando el metodo simplex estandar.

    El metodo simplex funciona iterando entre vertices de la region factible,
    moviendose siempre hacia el que mejora el valor de la funcion objetivo,
    hasta que ninguna mejora es posible (optimo encontrado).

    Para minimizacion, el truco es negar los coeficientes internamente y
    maximizar, luego negar Z al final para obtener el minimo real.

    Parametros:
        c                : lista de coeficientes de la funcion objetivo
        A                : matriz de coeficientes de las restricciones
        b                : lista de lados derechos (todos positivos para este metodo)
        tipo_optimizacion: "max" o "min" (default "max")
        tolerancia       : margen de error numerico (default 1e-6)

    Retorna:
        solucion: diccionario con el valor de cada variable y de Z, o None si no acotado
    """

    # Guardamos los coeficientes originales para mostrarlos al usuario.
    # Mas adelante podemos negar c para minimizacion, pero el usuario
    # siempre debe ver los coeficientes tal como los ingreso.
    c_original = c[:]

    # Si el problema es de minimizacion, lo convertimos a maximizacion internamente.
    # Minimizar Z = c*x  es equivalente a  Maximizar Z' = -c*x
    # Al final revertimos el signo para mostrar el minimo real.
    es_min = (tipo_optimizacion == "min")
    if es_min:
        c = [-coef for coef in c]   # negamos todos los coeficientes

    A, b, signos_normalizados = normalizar_lados_derechos(A, b, ["<="] * len(b))
    if any(s != "<=" for s in signos_normalizados):
        print("\nTras normalizar LDs negativos, hay restricciones >= que requieren dos fases.")
        print("Redirigiendo automaticamente al metodo de dos fases...")
        return resolver_dos_fases(c_original, A, b, signos_normalizados, tipo_optimizacion, tolerancia)

    # Informamos al usuario que variables auxiliares se agregaron.
    # En simplex normal todas las restricciones son <= y solo se agregan holguras.
    print("\nPREPARACION DE VARIABLES:")
    for i in range(len(b)):
        print(f"  Restriccion {i+1} (<=): se agrega variable de holgura h{i+1}")

    # Resumen de variables auxiliares para que el estudiante comprenda la tabla
    nombres_h = [f"h{i+1}" for i in range(len(b))]
    print(f"\n  Variables de holgura agregadas: {', '.join(nombres_h)}")
    print(f"  Variables de exceso agregadas : ninguna")
    print(f"  Variables artificiales agregadas: ninguna")

    # Mostramos la funcion objetivo con los coeficientes originales
    terminos_z = ' + '.join(f"{c_original[i]}·x{i+1}" for i in range(len(c_original)))
    tipo_str = "Maximizar" if not es_min else "Minimizar"
    print(f"\nRESOLVIENDO: {tipo_str} Z = {terminos_z}")

    # Construimos la tabla inicial del simplex con los coeficientes (ya negados si es min)
    columnas, tabla = construir_tabla_inicial(c, A, b)

    print("\n" + "=" * 70)
    print("SE USARA EL METODO SIMPLEX NORMAL")
    print("=" * 70)

    # Construimos las asignaciones de holgura para mostrar la forma aumentada.
    # Cada elemento indica que la holgura h_{i+1} pertenece a la restriccion i.
    h_asign_simplex = [(i, f"h{i+1}") for i in range(len(b))]
    # Mostramos las ecuaciones del sistema ampliado antes de la tabla
    imprimir_forma_aumentada(c_original, A, b, h_asign_simplex, [], [], tipo_optimizacion)

    # Mostramos la tabla inicial antes de empezar las iteraciones
    imprimir_tabla(columnas, tabla, "TABLA INICIAL")

    # Contador de iteraciones para etiquetar cada tabla intermedia
    iteracion = 1

    # Bucle principal del simplex: en cada iteracion mejoramos Z un paso
    while True:
        print(f"\n{'=' * 25} ITERACION {iteracion} {'=' * 25}")

        # Buscamos la columna con el coeficiente mas negativo en la fila Z.
        # Esa variable es la que mas mejora Z al entrar a la base.
        columna_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        # Si no hay coeficientes negativos en Z, la solucion actual es optima.
        # El criterio de optimalidad dice que no podemos mejorar mas.
        if columna_pivote == -1:
            print("\nYa no hay coeficientes negativos en la fila Z.")
            print("La solucion actual es optima.")
            break

        # Mostramos informacion de la variable que entra a la base
        print(f"\nVariable entrante: {columnas[columna_pivote]}")
        print(f"Columna pivote (indice Python): {columna_pivote}")
        print(f"Valor en Z: {tabla[0][columna_pivote]}")

        # Buscamos la fila con la minima razon positiva (LD / columna_pivote).
        # Esa es la variable que sale de la base para ceder su lugar.
        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, columna_pivote, tolerancia)

        # Si no hay fila pivote valida, el problema es no acotado (Z crece infinitamente)
        if fila_pivote == -1:
            print("\nNo existe fila pivote.")
            print("El problema puede ser no acotado.")
            return None

        # Mostramos informacion de la variable que sale de la base
        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][columna_pivote]}")

        # Realizamos el pivoteo: transforma la tabla para que la nueva variable
        # basica tenga coeficiente 1 en su fila y 0 en todas las demas
        tabla = pivotear(tabla, fila_pivote, columna_pivote, columnas, tolerancia)

        # Mostramos la tabla actualizada despues de este pivoteo
        imprimir_tabla(columnas, tabla, f"TABLA DESPUES DE ITERACION {iteracion}")

        iteracion += 1

    # Extraemos los valores finales de todas las variables desde la tabla optima
    solucion = obtener_solucion(columnas, tabla)

    # Si el problema original era de minimizacion, revertimos el signo de Z.
    # Recordar: maximizamos Z' = -Z, entonces Z_min = -Z'_max
    if es_min:
        solucion["Z"] = -solucion["Z"]

    print("\n" + "=" * 70)
    print("SOLUCION FINAL")
    print("=" * 70)

    # Mostramos el valor de cada variable con 2 decimales si es flotante
    for variable, valor in solucion.items():
        if isinstance(valor, float):
            print(f"{variable} = {valor:.2f}")
        else:
            print(f"{variable} = {valor}")

    return solucion


# ----------------------------------------------------------
# FUNCION: resolver con dos fases
# Implementa el metodo de dos fases para problemas con
# restricciones >= o = que requieren variables artificiales.
# ----------------------------------------------------------
def resolver_dos_fases(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Resuelve el problema de programacion lineal usando el metodo de dos fases.

    Se necesitan dos fases cuando hay restricciones >= o = porque no existe
    una base inicial factible obvia. Las variables artificiales actuan como
    "punto de partida" y deben eliminarse en la Fase 1 antes de optimizar Z.

    FASE 1: Minimizar W = suma de variables artificiales.
            Si al terminar W = 0, todas las artificiales salieron de la base
            y encontramos una solucion basica factible inicial.
            Si W > 0, el problema no tiene solucion factible.

    FASE 2: Partiendo de la solucion factible de Fase 1, optimizamos la
            funcion objetivo original Z usando el simplex normal.

    Para minimizacion, igual que en simplex, negamos c internamente y
    revertimos el signo de Z al final.

    Parametros:
        c                : lista de coeficientes de la funcion objetivo
        A                : matriz de coeficientes de las restricciones
        b                : lista de lados derechos
        signos           : lista de signos de cada restriccion ["<=", ">=", "="]
        tipo_optimizacion: "max" o "min" (default "max")
        tolerancia       : margen de error numerico (default 1e-6)

    Retorna:
        solucion: diccionario con el valor de cada variable y de Z,
                  o None si el problema no es factible o no esta acotado
    """

    print("\n" + "=" * 70)
    print("SE USARA EL METODO DE DOS FASES")
    print("=" * 70)

    n = len(c)   # numero de variables de decision
    m = len(A)   # numero de restricciones

    # ----------------------------------------------------------
    # PREPARACION PREVIA
    # Si es minimizacion, convertimos a maximizacion internamente
    # multiplicando los coeficientes por -1. Al final revertimos el signo de Z.
    # ----------------------------------------------------------

    # Guardamos los coeficientes originales para mostrar la forma aumentada
    # y el mensaje de transicion a Fase 2 con los valores reales del usuario.
    c_original = c[:]

    # Detectamos si es minimizacion para recordarlo al final
    es_min = (tipo_optimizacion == "min")
    if es_min:
        # Negamos los coeficientes: minimizar Z = c*x  <=>  maximizar Z' = -c*x
        c = [-coef for coef in c]

    A, b, signos = normalizar_lados_derechos(A, b, signos)

    # ----------------------------------------------------------
    # PASO 1 - Identificar que variables agregar por restriccion
    # Segun el tipo de restriccion, se necesitan variables distintas:
    # <= : solo holgura h  (absorbe el sobrante, coeficiente +1)
    # >= : exceso e (resta el sobrante, coef -1) + artificial a (base inicial, coef +1)
    # =  : solo artificial a (ya es igualdad, no necesita holgura ni exceso, coef +1)
    # ----------------------------------------------------------

    # Listas de asignaciones: cada elemento es (indice_restriccion, nombre_variable).
    # Usamos listas separadas para poder construir la tabla en el orden correcto.
    h_asignaciones = []  # (i, "h1"), (j, "h2"), ...  una por cada restriccion <=
    e_asignaciones = []  # (i, "e1"), (j, "e2"), ...  una por cada restriccion >=
    a_asignaciones = []  # (i, "a1"), (j, "a2"), ...  una por cada restriccion >= o =

    # Contadores para numerar las variables de forma consecutiva
    h_num = 0
    e_num = 0
    a_num = 0

    # Recorremos cada restriccion y asignamos las variables que le corresponden
    for i, signo in enumerate(signos):
        if signo == "<=":
            # Solo holgura: convierte a1*x1 + a2*x2 <= b  en  a1*x1 + a2*x2 + h = b
            h_num += 1
            h_asignaciones.append((i, f"h{h_num}"))
        elif signo == ">=":
            # Exceso y artificial: a1*x1 + a2*x2 >= b  ->  a1*x1 + a2*x2 - e + a = b
            e_num += 1
            a_num += 1
            e_asignaciones.append((i, f"e{e_num}"))
            a_asignaciones.append((i, f"a{a_num}"))
        elif signo == "=":
            # Solo artificial: a1*x1 + a2*x2 = b  ->  a1*x1 + a2*x2 + a = b
            a_num += 1
            a_asignaciones.append((i, f"a{a_num}"))

    # Mostramos al usuario que variables se agregaron en cada restriccion
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

    # Extraemos solo los nombres para mostrarlos en el resumen
    nombres_h = [nombre for (_, nombre) in h_asignaciones]
    nombres_e = [nombre for (_, nombre) in e_asignaciones]
    nombres_a = [nombre for (_, nombre) in a_asignaciones]

    # Resumen de todas las variables auxiliares agregadas al problema
    print(f"\n  Variables de holgura agregadas  : {', '.join(nombres_h) if nombres_h else 'ninguna'}")
    print(f"  Variables de exceso agregadas   : {', '.join(nombres_e) if nombres_e else 'ninguna'}")
    print(f"  Variables artificiales agregadas: {', '.join(nombres_a) if nombres_a else 'ninguna'}")

    # La funcion W de Fase 1 es la suma de todas las variables artificiales.
    # Minimizar W = 0 significa que todas las artificiales saldran de la base.
    terminos_w = ' + '.join(nombres_a)
    print(f"\nFASE 1: Minimizar W = {terminos_w}")

    # ----------------------------------------------------------
    # PASO 2 - Construir columnas y tabla de Fase 1
    # La tabla de Fase 1 usa W como funcion objetivo en lugar de Z.
    # Orden de columnas: VB, W, x1..xn, h1..hh, e1..ee, a1..aa, LD
    # ----------------------------------------------------------

    # Construimos la lista de nombres de columnas en el orden estandar
    columnas = ["VB", "W"]           # variable basica y funcion W
    for i in range(n):
        columnas.append(f"x{i+1}")   # variables de decision
    for (_, nombre) in h_asignaciones:
        columnas.append(nombre)      # variables de holgura
    for (_, nombre) in e_asignaciones:
        columnas.append(nombre)      # variables de exceso
    for (_, nombre) in a_asignaciones:
        columnas.append(nombre)      # variables artificiales
    columnas.append("LD")            # lado derecho siempre al final

    # Construimos la fila W (funcion objetivo de Fase 1).
    # W = suma de artificiales, por eso W tiene coeficiente 1 en W,
    # 0 en todas las variables de decision, holguras y excesos,
    # y 1 en cada artificial (son los terminos de W).
    fila_w = ["W", 1]          # "W" en VB, 1 en la columna W (es la fila objetivo)
    for _ in range(n):
        fila_w.append(0)       # coeficiente 0 para cada xi en W inicial
    for _ in h_asignaciones:
        fila_w.append(0)       # coeficiente 0 para cada holgura en W
    for _ in e_asignaciones:
        fila_w.append(0)       # coeficiente 0 para cada exceso en W
    for _ in a_asignaciones:
        fila_w.append(1)       # coeficiente 1 para cada artificial (son los terminos de W)
    fila_w.append(0)           # LD = 0 (W arranca en 0 antes de la eliminacion gaussiana)

    # La tabla empieza con la fila W como primera fila
    tabla = [fila_w]

    # Construimos una fila por cada restriccion del problema
    for i in range(m):
        # La variable basica inicial depende del tipo de restriccion.
        # Para <=: la holgura es factible como base inicial (vale b_i >= 0).
        # Para >= y =: usamos la artificial como base inicial (es el "truco" de Fase 1).
        if signos[i] == "<=":
            vb = next(nombre for (ri, nombre) in h_asignaciones if ri == i)
        else:
            vb = next(nombre for (ri, nombre) in a_asignaciones if ri == i)

        fila = [vb, 0]   # VB = variable basica elegida, columna W = 0 (no es la fila objetivo)

        # Copiamos los coeficientes de las variables de decision para esta restriccion
        for j in range(n):
            fila.append(float(A[i][j]))

        # Coeficiente de cada holgura: 1 si la holgura pertenece a esta restriccion, 0 si no
        for (ri, _) in h_asignaciones:
            fila.append(1.0 if ri == i else 0.0)

        # Coeficiente de cada exceso: -1 si el exceso pertenece a esta restriccion, 0 si no.
        # El signo negativo es porque el exceso resta en la ecuacion ampliada (>=)
        for (ri, _) in e_asignaciones:
            fila.append(-1.0 if ri == i else 0.0)

        # Coeficiente de cada artificial: 1 si la artificial pertenece a esta restriccion, 0 si no
        for (ri, _) in a_asignaciones:
            fila.append(1.0 if ri == i else 0.0)

        fila.append(float(b[i]))   # copiamos el lado derecho de esta restriccion
        tabla.append(fila)

    # ----------------------------------------------------------
    # PASO 3 - Eliminacion gaussiana en fila W
    # Antes de iterar, la fila W debe tener coeficiente 0 en todas
    # las columnas de las variables que estan en la base inicial.
    # Como las artificiales estan en la base y tienen coeficiente 1
    # en W, restamos sus filas de W para limpiarla.
    # ----------------------------------------------------------

    # Mostramos la forma aumentada antes de la tabla para que el estudiante
    # vea como se convirtieron las desigualdades en igualdades
    imprimir_forma_aumentada(c_original, A, b, h_asignaciones, e_asignaciones, a_asignaciones, tipo_optimizacion)

    # Mostramos la tabla tal como quedo antes de la eliminacion gaussiana
    imprimir_tabla(columnas, tabla, "TABLA INICIAL FASE 1 (antes de eliminacion gaussiana)")

    # Recorremos las filas de restricciones buscando las que tienen artificial en la base
    for i in range(1, len(tabla)):
        vb_actual = tabla[i][0]   # nombre de la variable basica en esta fila
        # Verificamos si esta variable es una de las artificiales
        es_artificial = any(nombre == vb_actual for (_, nombre) in a_asignaciones)
        if es_artificial:
            # Encontramos el indice de la columna de esta artificial
            col_idx = columnas.index(vb_actual)
            # Leemos el coeficiente que tiene esta artificial en la fila W
            coef_en_w = tabla[0][col_idx]
            # Si el coeficiente no es ya cero, restamos la fila para anularlo.
            # Operacion: fila_W = fila_W - coef_en_w * fila_restriccion
            if not math.isclose(coef_en_w, 0, rel_tol=tolerancia, abs_tol=tolerancia):
                for j in range(1, len(tabla[0])):
                    tabla[0][j] = tabla[0][j] - coef_en_w * tabla[i][j]

    # Mostramos la tabla despues de la eliminacion gaussiana (lista para iterar)
    imprimir_tabla(columnas, tabla, "TABLA INICIAL FASE 1 (tras eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 4 - Iterar simplex en Fase 1
    # Aplicamos el simplex sobre la fila W hasta que no queden
    # coeficientes negativos. El objetivo es hacer W = 0.
    # ----------------------------------------------------------

    # FASE 1: buscamos una solucion basica factible inicial.
    # Si la suma de artificiales llega a 0, encontramos un punto de partida valido
    # para Fase 2. Si no llega a 0, el problema no tiene solucion factible.
    iteracion = 1
    while True:
        # Buscamos el coeficiente mas negativo en la fila W (criterio de entrada)
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        # Si no hay negativos en W, el simplex de Fase 1 termino
        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en W. Fin de Fase 1.")
            # Revisamos el valor final de W para saber si el problema es factible
            print("\nRESULTADO FASE 1:")
            w_final_preview = tabla[0][-1]   # LD de la fila W al terminar
            if abs(w_final_preview) <= tolerancia:
                # W = 0: todas las artificiales salieron de la base, hay solucion factible
                print(f"  W = {w_final_preview:.4f} → El problema ES factible, se puede continuar a Fase 2.")
            else:
                # W > 0: alguna artificial sigue en la base, no hay solucion factible
                print(f"  W = {w_final_preview:.4f} → El problema NO es factible, no existe solucion.")
            break

        # Mostramos la variable que entra a la base en esta iteracion de Fase 1
        print(f"\nVariable entrante: {columnas[col_pivote]}")
        print(f"Columna pivote (indice Python): {col_pivote}")
        print(f"Valor en fila objetivo: {tabla[0][col_pivote]}")

        # Buscamos la fila con la minima razon (variable que sale de la base)
        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        # Si no hay fila pivote, el problema de Fase 1 no esta acotado (no deberia ocurrir normalmente)
        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado en Fase 1.")
            return None

        # Mostramos la variable que sale de la base en esta iteracion
        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][col_pivote]}")

        # Realizamos el pivoteo para actualizar la tabla
        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 1 - ITERACION {iteracion}")
        iteracion += 1

    # ----------------------------------------------------------
    # PASO 5 - Verificar factibilidad
    # Si el valor final de W no es (casi) cero, significa que alguna
    # variable artificial sigue en la base con valor positivo,
    # lo que indica que no existe ninguna solucion factible.
    # ----------------------------------------------------------

    # Leemos el LD de la fila W al final de Fase 1
    w_final = tabla[0][-1]
    if abs(w_final) > tolerancia:
        # W > 0: el problema original no tiene solucion feasible, terminamos aqui
        print("\nEl problema no tiene solucion factible")
        return None

    # El problema es factible. Informamos la transicion a Fase 2.
    print("\nTRANSICION A FASE 2:")
    # Las columnas artificiales ya no son necesarias; las eliminamos de la tabla
    print(f"  Se eliminan las columnas artificiales: {', '.join(nombres_a)}")

    # Preparamos el mensaje con la funcion objetivo original para mostrarlo al usuario
    tipo_str = "Maximizar" if not es_min else "Minimizar"
    # Si era minimizacion, c fue negado; recuperamos los coeficientes originales para mostrarlos
    c_original = [-coef for coef in c] if es_min else c
    terminos_z = ' + '.join(f"{c_original[i]}·x{i+1}" for i in range(n))
    print(f"  Se restaura la funcion objetivo original: {tipo_str} Z = {terminos_z}")
    print(f"  Se aplica eliminacion gaussiana en fila Z para limpiar variables basicas en la base...")

    print("\nFASE 2: Optimizar funcion objetivo original")

    # ----------------------------------------------------------
    # PASO 6 - Construir tabla de Fase 2
    # Eliminamos las columnas artificiales (ya cumplieron su rol en Fase 1)
    # y reemplazamos la fila W por la fila Z de la funcion objetivo real.
    # ----------------------------------------------------------

    # Obtenemos los nombres e indices de las columnas artificiales para eliminarlas
    nombres_artificiales = [nombre for (_, nombre) in a_asignaciones]
    indices_artificiales = [columnas.index(nombre) for nombre in nombres_artificiales]

    # Construimos la lista de indices de columnas que SI conservamos (todas menos las artificiales)
    indices_a_conservar = [j for j in range(len(columnas)) if j not in indices_artificiales]

    # Creamos la nueva lista de columnas sin las artificiales
    columnas_f2 = [columnas[j] for j in indices_a_conservar]
    # Reemplazamos "W" por "Z" porque ahora optimizamos la funcion objetivo real
    columnas_f2[1] = "Z"

    # Construimos la nueva tabla filtrando las columnas artificiales de cada fila
    tabla_f2 = []
    for fila in tabla:
        nueva_fila = [fila[j] for j in indices_a_conservar]
        tabla_f2.append(nueva_fila)

    # Construimos la nueva fila Z con los coeficientes de la funcion objetivo original.
    # Formato: 1 en columna Z (es la fila objetivo), -c_i en cada xi (coeficientes negados),
    # 0 en holguras y excesos (no aparecen en Z), 0 en LD (Z arranca en 0).
    fila_z = ["Z", 1]
    for coef in c:
        fila_z.append(-coef)   # negados porque Z - c1*x1 - c2*x2 = 0
    for _ in h_asignaciones:
        fila_z.append(0)       # holguras no tienen coeficiente en Z
    for _ in e_asignaciones:
        fila_z.append(0)       # excesos no tienen coeficiente en Z
    fila_z.append(0)           # LD inicial de Z es 0

    # Reemplazamos la primera fila (que era W) por la nueva fila Z
    tabla_f2[0] = fila_z

    # Mostramos la tabla de Fase 2 antes de la eliminacion gaussiana
    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (antes de eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 7 - Eliminacion gaussiana en fila Z
    # Al inicio de Fase 2, la fila Z puede tener coeficientes no nulos
    # en columnas de variables que ya estan en la base.
    # Debemos limpiarlos para que la tabla este en forma canonica.
    # La operacion es: fila_Z = fila_Z - coef_en_Z * fila_de_esa_variable
    # ----------------------------------------------------------

    # Recorremos las filas de restricciones para limpiar la fila Z
    for i in range(1, len(tabla_f2)):
        vb_actual = tabla_f2[i][0]   # variable basica en esta fila
        # Solo procesamos variables que existan en la tabla de Fase 2
        if vb_actual in columnas_f2:
            col_idx = columnas_f2.index(vb_actual)   # indice de la columna de esta variable
            coef_en_z = tabla_f2[0][col_idx]         # coeficiente que tiene en la fila Z
            # Si el coeficiente no es ya cero, aplicamos la eliminacion gaussiana
            if not math.isclose(coef_en_z, 0, rel_tol=tolerancia, abs_tol=tolerancia):
                for j in range(1, len(tabla_f2[0])):
                    # Restamos la fila de la variable para anular su columna en Z
                    tabla_f2[0][j] = tabla_f2[0][j] - coef_en_z * tabla_f2[i][j]

    # Mostramos la tabla de Fase 2 despues de la eliminacion gaussiana (lista para iterar)
    imprimir_tabla(columnas_f2, tabla_f2, "TABLA INICIAL FASE 2 (tras eliminacion gaussiana)")

    # ----------------------------------------------------------
    # PASO 8 - Iterar simplex en Fase 2
    # FASE 2: partiendo de la solucion factible de Fase 1,
    # optimizamos la funcion objetivo original usando el simplex estandar.
    # ----------------------------------------------------------

    # Reemplazamos las variables de tabla y columnas para reutilizar el bucle simplex
    columnas = columnas_f2
    tabla = tabla_f2

    iteracion = 1
    while True:
        # Buscamos el coeficiente mas negativo en la fila Z (criterio de entrada a la base)
        col_pivote = encontrar_columna_pivote(tabla, columnas, tolerancia)

        # Si no hay negativos en Z, la solucion optima de Fase 2 fue alcanzada
        if col_pivote == -1:
            print("\nNo hay coeficientes negativos en Z. Solucion optima encontrada.")
            break

        # Mostramos la variable que entra a la base en esta iteracion de Fase 2
        print(f"\nVariable entrante: {columnas[col_pivote]}")
        print(f"Columna pivote (indice Python): {col_pivote}")
        print(f"Valor en fila objetivo: {tabla[0][col_pivote]}")

        # Buscamos la fila con la minima razon (variable que sale de la base)
        fila_pivote, razon_minima = encontrar_fila_pivote(tabla, col_pivote, tolerancia)

        # Si no hay fila pivote, el problema no esta acotado en la direccion de Z
        if fila_pivote == -1:
            print("\nNo existe fila pivote. Problema no acotado.")
            return None

        # Mostramos la variable que sale de la base
        print(f"\nVariable saliente: {tabla[fila_pivote][0]}")
        print(f"Fila pivote (indice Python): {fila_pivote}")
        print(f"Razon minima positiva: {razon_minima}")
        print(f"Elemento pivote: {tabla[fila_pivote][col_pivote]}")

        # Realizamos el pivoteo para actualizar la tabla de Fase 2
        tabla = pivotear(tabla, fila_pivote, col_pivote, columnas, tolerancia)
        imprimir_tabla(columnas, tabla, f"TABLA FASE 2 - ITERACION {iteracion}")
        iteracion += 1

    # ----------------------------------------------------------
    # PASO 9 - Extraer y mostrar solucion
    # Leemos los valores finales de la tabla optima.
    # Si era minimizacion, revertimos el signo de Z para obtener el minimo real.
    # ----------------------------------------------------------

    # Extraemos los valores de todas las variables desde la tabla final de Fase 2
    solucion = obtener_solucion(columnas, tabla)

    # Revertimos la conversion: minimizar Z = c*x => Z_min = -Z'_max
    if es_min:
        solucion["Z"] = -solucion["Z"]

    print("\n" + "=" * 70)
    print("SOLUCION FINAL")
    print("=" * 70)

    # Mostramos cada variable con 2 decimales si es flotante
    for variable, valor in solucion.items():
        if isinstance(valor, float):
            print(f"{variable} = {valor:.2f}")
        else:
            print(f"{variable} = {valor}")

    return solucion


# ----------------------------------------------------------
# FUNCION PRINCIPAL DEL PROGRAMA
# Punto de entrada que decide que metodo usar y lo ejecuta.
# ----------------------------------------------------------
def resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion="max", tolerancia=1e-6):
    """
    Funcion principal que coordina la resolucion del problema de programacion lineal.

    Primero detecta automaticamente si el problema requiere simplex normal
    o el metodo de dos fases segun los signos de las restricciones y los
    lados derechos. Luego llama al metodo correspondiente.

    Parametros:
        c                : lista de coeficientes de la funcion objetivo
        A                : matriz de coeficientes de las restricciones (una lista por fila)
        b                : lista de lados derechos de las restricciones
        signos           : lista de signos de cada restriccion ["<=", ">=", "="]
        tipo_optimizacion: "max" para maximizar, "min" para minimizar (default "max")
        tolerancia       : margen de error numerico para comparaciones (default 1e-6)

    Retorna:
        solucion: diccionario con los valores optimos de las variables y de Z,
                  o None si el problema no tiene solucion o no esta acotado
    """

    # Detectamos automaticamente si el problema requiere dos fases o simplex normal
    metodo = detectar_metodo(signos, b, tolerancia)

    print("\n" + "=" * 70)
    print("DETECCION AUTOMATICA DEL METODO")
    print("=" * 70)
    print(f"Metodo detectado: {metodo}")

    # Llamamos al metodo correspondiente segun la deteccion automatica
    if metodo == "simplex":
        # Simplex normal: todas las restricciones son <= con LD positivo
        return resolver_simplex(c, A, b, tipo_optimizacion, tolerancia)
    else:
        # Dos fases: hay alguna restriccion >= o = que requiere variables artificiales
        return resolver_dos_fases(c, A, b, signos, tipo_optimizacion, tolerancia)


# ----------------------------------------------------------
# FUNCION: pedir datos por consola
# Solicita todos los datos del problema al usuario de forma
# interactiva con validacion de entradas.
# ----------------------------------------------------------
def pedir_datos():
    """
    Solicita al usuario todos los datos del problema de programacion lineal
    por consola, validando cada entrada antes de aceptarla.

    Se pide:
    - Numero de variables de decision (entero positivo)
    - Coeficiente de cada variable en la funcion objetivo (flotante)
    - Tipo de optimizacion: "max" o "min"
    - Numero de restricciones (entero positivo)
    - Por cada restriccion: coeficientes, lado derecho y signo (<=, >= o =)

    Las entradas numericas usan try/except para detectar valores invalidos.
    Las entradas de tipo texto usan bucles while que repiten la pregunta
    hasta que el usuario ingrese un valor valido.

    Retorna:
        c                : lista de coeficientes de la funcion objetivo
        A                : matriz de coeficientes de las restricciones
        b                : lista de lados derechos
        signos           : lista de signos de cada restriccion
        tipo_optimizacion: "max" o "min"
    """

    print("\n" + "=" * 70)
    print("INGRESO DE DATOS DEL PROBLEMA")
    print("=" * 70)

    # Pedimos el numero de variables de decision.
    # El bucle repite hasta obtener un entero positivo valido.
    while True:
        try:
            n = int(input("\nNumero de variables de decision: "))
            if n > 0:
                break   # entrada valida, salimos del bucle
            print("  Debe ser un entero positivo.")
        except ValueError:
            # El usuario ingreso algo que no es un entero (texto, decimal, etc.)
            print("  Entrada invalida. Ingrese un entero positivo.")

    # Pedimos el coeficiente de cada variable xi en la funcion objetivo.
    # Se acepta cualquier numero real (positivo, negativo o cero).
    c = []
    for i in range(n):
        while True:
            try:
                coef = float(input(f"  Coeficiente de x{i+1} en la funcion objetivo: "))
                c.append(coef)   # agregamos el coeficiente a la lista
                break
            except ValueError:
                print("  Entrada invalida. Ingrese un numero.")

    # Pedimos el tipo de optimizacion.
    # Solo se aceptan "max" o "min" (insensible a mayusculas/minusculas).
    while True:
        tipo = input("\nTipo de optimizacion (max / min): ").strip().lower()
        if tipo in ("max", "min"):
            tipo_optimizacion = tipo
            break   # entrada valida
        print("  Opcion invalida. Ingrese 'max' o 'min'.")

    # Pedimos el numero de restricciones del problema.
    while True:
        try:
            m = int(input("\nNumero de restricciones: "))
            if m > 0:
                break
            print("  Debe ser un entero positivo.")
        except ValueError:
            print("  Entrada invalida. Ingrese un entero positivo.")

    # Listas para almacenar los datos de las restricciones
    A = []       # matriz de coeficientes (una lista por restriccion)
    b = []       # lados derechos
    signos = []  # tipos de restriccion

    # Pedimos los datos de cada restriccion una por una
    for i in range(m):
        print(f"\n  Restriccion {i+1}:")

        # Pedimos el coeficiente de cada variable xi en esta restriccion
        fila = []
        for j in range(n):
            while True:
                try:
                    coef = float(input(f"    Coeficiente de x{j+1}: "))
                    fila.append(coef)
                    break
                except ValueError:
                    print("    Entrada invalida. Ingrese un numero.")
        A.append(fila)   # agregamos la fila completa a la matriz

        # Pedimos el lado derecho de esta restriccion
        while True:
            try:
                ld = float(input(f"    Lado derecho (LD): "))
                b.append(ld)
                break
            except ValueError:
                print("    Entrada invalida. Ingrese un numero.")

        # Pedimos el signo de esta restriccion.
        # Solo se aceptan "<=", ">=" o "=".
        while True:
            signo = input(f"    Signo (<=, >= o =): ").strip()
            if signo in ("<=", ">=", "="):
                signos.append(signo)
                break   # entrada valida
            print("    Signo invalido. Ingrese '<=', '>=' o '='.")

    # Retornamos todos los datos necesarios para llamar al solver
    return c, A, b, signos, tipo_optimizacion


# Pedimos los datos al usuario y resolvemos el problema
c, A, b, signos, tipo_optimizacion = pedir_datos()
resolver_programacion_lineal(c, A, b, signos, tipo_optimizacion)
