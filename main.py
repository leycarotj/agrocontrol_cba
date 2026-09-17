import os
import json
from pathlib import Path
from datetime import datetime

# Rutas de almacenamiento
DATA_DIR = Path("data")
PRODUCTOS_FILE = DATA_DIR / "productos.json"
LOTES_FILE = DATA_DIR / "lotes.json"
MOVIMIENTOS_FILE = DATA_DIR / "movimientos.json"
VENTAS_FILE = DATA_DIR / "ventas.json"

# Estructuras globales en memoria
productos = []
lotes = []
movimientos = []
ventas = []

# --- PERSISTENCIA JSON ---

def garantizar_directorio():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def cargar_json(ruta_archivo):
    if not ruta_archivo.exists():
        return []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

def guardar_json(datos, ruta_archivo):
    garantizar_directorio()
    with open(ruta_archivo, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=4)

def cargar_todos_los_datos():
    global productos, lotes, movimientos, ventas
    productos = cargar_json(PRODUCTOS_FILE)
    lotes = cargar_json(LOTES_FILE)
    movimientos = cargar_json(MOVIMIENTOS_FILE)
    ventas = cargar_json(VENTAS_FILE)

def guardar_todos_los_datos():
    guardar_json(productos, PRODUCTOS_FILE)
    guardar_json(lotes, LOTES_FILE)
    guardar_json(movimientos, MOVIMIENTOS_FILE)
    guardar_json(ventas, VENTAS_FILE)

# --- AUXILIARES E INTERFAZ ---

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPresione Enter para continuar...")

def buscar_producto(codigo):
    codigo = codigo.strip().upper()
    for prod in productos:
        if prod["codigo"] == codigo:
            return prod
    return None

def buscar_lote(id_lote):
    id_lote = id_lote.strip().upper()
    for l in lotes:
        if l["id_lote"] == id_lote:
            return l
    return None

def generar_id_movimiento():
    siguiente_num = len(movimientos) + 1
    return f"M{siguiente_num:04d}"

def generar_id_venta():
    siguiente_num = len(ventas) + 1
    return f"V{siguiente_num:04d}"

def calcular_stock(codigo_producto):
    codigo_producto = codigo_producto.strip().upper()
    stock = 0.0
    for m in movimientos:
        if m["producto_codigo"] == codigo_producto:
            if m["tipo"] == "ENTRADA":
                stock += m["cantidad"]
            elif m["tipo"] == "SALIDA":
                stock -= m["cantidad"]
    return stock

# --- MÓDULO PRODUCTOS ---

def registrar_producto():
    print("--- [RF01] Registrar Producto ---")
    codigo = input("Código del producto (ej. P001): ").strip().upper()
    if not codigo:
        print("Error: El código no puede estar vacío.")
        return
    
    if buscar_producto(codigo):
        print(f"Error (PF001): El producto con código '{codigo}' ya existe.")
        return

    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("Error: El nombre no puede estar vacío.")
        return

    categoria = input("Categoría (ej. Hortalizas, Frutas): ").strip()
    unidad = input("Unidad de medida (ej. unidad, kg, lb): ").strip()

    try:
        precio = float(input("Precio de venta ($): "))
        if precio <= 0:
            print("Error (PF002): El precio debe ser un número mayor a 0.")
            return
    except ValueError:
        print("Error (PF002): Debe ingresar un valor numérico válido para el precio.")
        return

    try:
        stock_minimo = float(input("Stock mínimo de seguridad: "))
        if stock_minimo < 0:
            print("Error: El stock mínimo no puede ser negativo.")
            return
    except ValueError:
        print("Error: Debe ingresar un valor numérico para el stock mínimo.")
        return

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True
    }

    productos.append(nuevo_producto)
    guardar_todos_los_datos()
    print(f"\n¡Producto '{nombre}' ({codigo}) registrado exitosamente!")

def consultar_productos():
    print("--- [RF02] Consultar / Listar Productos ---")
    filtro = input("Ingrese código o parte del nombre para buscar (dejar vacío para listar todos): ").strip().lower()

    encontrados = [
        p for p in productos
        if (p["activo"] and (not filtro or filtro in p["codigo"].lower() or filtro in p["nombre"].lower()))
    ]

    if not encontrados:
        print("\nNo se encontraron productos activos que coincidan con la búsqueda.")
        return

    print("\n" + "="*95)
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<25} | {'CATEGORÍA':<15} | {'PRECIO ($)':<12} | {'STK MIN':<8} | {'STOCK ACTUAL':<12}")
    print("="*95)
    for p in encontrados:
        stk_actual = calcular_stock(p["codigo"])
        print(f"{p['codigo']:<10} | {p['nombre']:<25} | {p['categoria']:<15} | {p['precio']:<12.2f} | {p['stock_minimo']:<8.1f} | {stk_actual:<12.1f}")
    print("="*95)

def actualizar_producto():
    print("--- [RF03] Actualizar Producto ---")
    codigo = input("Ingrese el código del producto a actualizar: ").strip().upper()
    prod = buscar_producto(codigo)

    if not prod:
        print(f"Error: No existe un producto registrado con el código '{codigo}'.")
        return

    print(f"\nModificando producto: {prod['nombre']} ({prod['codigo']})")
    print("Deje el campo en blanco si no desea modificar su valor actual.")

    nuevo_nombre = input(f"Nombre [{prod['nombre']}]: ").strip()
    nueva_cat = input(f"Categoría [{prod['categoria']}]: ").strip()
    nueva_unidad = input(f"Unidad [{prod['unidad']}]: ").strip()

    nuevo_precio_str = input(f"Precio [{prod['precio']}]: ").strip()
    nuevo_stock_min_str = input(f"Stock mínimo [{prod['stock_minimo']}]: ").strip()

    if nuevo_nombre:
        prod["nombre"] = nuevo_nombre
    if nueva_cat:
        prod["categoria"] = nueva_cat
    if nueva_unidad:
        prod["unidad"] = nueva_unidad

    if nuevo_precio_str:
        try:
            val = float(nuevo_precio_str)
            if val > 0:
                prod["precio"] = val
            else:
                print("Precio inválido. Se conserva el valor anterior.")
        except ValueError:
            print("Formato numérico incorrecto. Se conserva el valor anterior.")

    if nuevo_stock_min_str:
        try:
            val = float(nuevo_stock_min_str)
            if val >= 0:
                prod["stock_minimo"] = val
            else:
                print("Stock mínimo inválido. Se conserva el valor anterior.")
        except ValueError:
            print("Formato numérico incorrecto. Se conserva el valor anterior.")

    guardar_todos_los_datos()
    print(f"\n¡Producto '{prod['codigo']}' actualizado con éxito!")

def desactivar_producto():
    print("--- [RF04] Desactivar Producto ---")
    codigo = input("Ingrese el código del producto a desactivar: ").strip().upper()
    prod = buscar_producto(codigo)

    if not prod:
        print(f"Error: No existe el producto '{codigo}'.")
        return

    if not prod["activo"]:
        print("El producto ya se encuentra desactivado.")
        return

    confirmacion = input(f"¿Está segura/o de desactivar el producto '{prod['nombre']}'? (s/n): ").strip().lower()
    if confirmacion == 's':
        prod["activo"] = False
        guardar_todos_los_datos()
        print(f"\n¡Producto '{codigo}' desactivado correctamente! (Se conserva en el historial).")

def menu_productos():
    while True:
        limpiar_pantalla()
        print("==================== GESTIÓN DE PRODUCTOS ====================")
        print("1. Registrar nuevo producto")
        print("2. Consultar / Listar productos activos")
        print("3. Actualizar datos de producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")
        print("==============================================================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            limpiar_pantalla()
            registrar_producto()
            pausar()
        elif opcion == "2":
            limpiar_pantalla()
            consultar_productos()
            pausar()
        elif opcion == "3":
            limpiar_pantalla()
            actualizar_producto()
            pausar()
        elif opcion == "4":
            limpiar_pantalla()
            desactivar_producto()
            pausar()
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            pausar()

# --- MÓDULO LOTES PRODUCTIVOS ---

def registrar_lote():
    print("--- [RF05] Registrar Lote Productivo ---")
    id_lote = input("ID del lote (ej. L001): ").strip().upper()
    if not id_lote:
        print("Error: El ID del lote no puede estar vacío.")
        return

    if buscar_lote(id_lote):
        print(f"Error: El lote con ID '{id_lote}' ya está registrado.")
        return

    codigo_prod = input("Código del producto asociado: ").strip().upper()
    prod = buscar_producto(codigo_prod)

    if not prod:
        print(f"Error: El producto '{codigo_prod}' no existe.")
        return

    if not prod["activo"]:
        print(f"Error: El producto '{prod['nombre']}' se encuentra DESACTIVADO. No puede asociarse a nuevos lotes.")
        return

    fecha_siembra = input("Fecha de siembra (AAAA-MM-DD) [dejar vacío para fecha actual]: ").strip()
    if not fecha_siembra:
        fecha_siembra = datetime.now().strftime("%Y-%m-%d")

    try:
        area_m2 = float(input("Área en m²: "))
        if area_m2 <= 0:
            print("Error: El área debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Debe ingresar un valor numérico para el área.")
        return

    nuevo_lote = {
        "id_lote": id_lote,
        "producto_codigo": codigo_prod,
        "fecha_siembra": fecha_siembra,
        "area_m2": area_m2,
        "cantidad_producida": 0.0,
        "estado": "EN_PRODUCCION"
    }

    lotes.append(nuevo_lote)
    guardar_todos_los_datos()
    print(f"\n¡Lote '{id_lote}' asociado a '{prod['nombre']}' registrado exitosamente!")

def consultar_lotes():
    print("--- Consultar Lotes Productivos ---")
    if not lotes:
        print("\nNo hay lotes productivos registrados.")
        return

    print("\n" + "="*85)
    print(f"{'ID LOTE':<10} | {'PROD CÓD':<10} | {'SIEMBRA':<12} | {'ÁREA (m²)':<10} | {'CANT PROD':<10} | {'ESTADO':<15}")
    print("="*85)
    for l in lotes:
        print(f"{l['id_lote']:<10} | {l['producto_codigo']:<10} | {l['fecha_siembra']:<12} | {l['area_m2']:<10.1f} | {l['cantidad_producida']:<10.1f} | {l['estado']:<15}")
    print("="*85)

def cambiar_estado_lote():
    print("--- [RF06] Cambiar Estado de Lote ---")
    id_lote = input("Ingrese el ID del lote: ").strip().upper()
    lote = buscar_lote(id_lote)

    if not lote:
        print(f"Error (PF003): No existe el lote '{id_lote}'.")
        return

    if lote["estado"] == "COSECHADO":
        print("Error (PF004): El lote ya fue COSECHADO. No se puede modificar su estado.")
        return

    print(f"\nEstado actual del lote {id_lote}: {lote['estado']}")
    print("1. CANCELADO")
    print("2. Volver a EN_PRODUCCION")
    opc = input("Seleccione nuevo estado: ").strip()

    if opc == "1":
        lote["estado"] = "CANCELADO"
        guardar_todos_los_datos()
        print(f"\nLote '{id_lote}' cambiado a CANCELADO.")
    elif opc == "2":
        lote["estado"] = "EN_PRODUCCION"
        guardar_todos_los_datos()
        print(f"\nLote '{id_lote}' restablecido a EN_PRODUCCION.")
    else:
        print("Opción cancelada.")

def cosechar_lote():
    print("--- [RF07] Cosechar Lote Productivo ---")
    id_lote = input("Ingrese el ID del lote a cosechar: ").strip().upper()
    lote = buscar_lote(id_lote)

    if not lote:
        print(f"Error (PF003): El lote '{id_lote}' no existe.")
        return

    if lote["estado"] == "COSECHADO":
        print(f"Error (PF004): El lote '{id_lote}' ya fue cosechado previamente. Operación rechazada.")
        return

    if lote["estado"] == "CANCELADO":
        print(f"Error: El lote '{id_lote}' está CANCELADO. No se puede cosechar.")
        return

    try:
        cantidad = float(input("Cantidad cosechada / producida: "))
        if cantidad <= 0:
            print("Error: La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Debe ingresar un número válido para la cantidad.")
        return

    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    nuevo_movimiento = {
        "id": generar_id_movimiento(),
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha lote {id_lote}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    movimientos.append(nuevo_movimiento)
    guardar_todos_los_datos()
    print(f"\n¡Cosecha registrada con éxito!")
    print(f"Se generó automáticamente el movimiento {nuevo_movimiento['id']} (ENTRADA) por {cantidad} unidades.")

def menu_lotes():
    while True:
        limpiar_pantalla()
        print("==================== GESTIÓN DE LOTES ====================")
        print("1. Registrar lote productivo")
        print("2. Consultar lotes")
        print("3. Cambiar estado de lote")
        print("4. Cosechar lote")
        print("0. Volver al menú principal")
        print("==========================================================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            limpiar_pantalla()
            registrar_lote()
            pausar()
        elif opcion == "2":
            limpiar_pantalla()
            consultar_lotes()
            pausar()
        elif opcion == "3":
            limpiar_pantalla()
            cambiar_estado_lote()
            pausar()
        elif opcion == "4":
            limpiar_pantalla()
            cosechar_lote()
            pausar()
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            pausar()

# --- MÓDULO MOVIMIENTOS DE INVENTARIO ---

def registrar_entrada_inventario():
    print("--- [RF08] Registrar Entrada de Inventario Manual ---")
    codigo_prod = input("Código del producto: ").strip().upper()
    prod = buscar_producto(codigo_prod)

    if not prod:
        print(f"Error: No existe el producto '{codigo_prod}'.")
        return

    if not prod["activo"]:
        print(f"Error: El producto '{prod['nombre']}' está DESACTIVADO.")
        return

    try:
        cantidad = float(input("Cantidad a ingresar: "))
        if cantidad <= 0:
            print("Error: La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Debe ingresar un valor numérico.")
        return

    motivo = input("Motivo de la entrada (OBLIGATORIO): ").strip()
    if not motivo:
        print("Error: El motivo de la entrada es obligatorio.")
        return

    nuevo_movimiento = {
        "id": generar_id_movimiento(),
        "producto_codigo": codigo_prod,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    movimientos.append(nuevo_movimiento)
    guardar_todos_los_datos()
    stock_nuevo = calcular_stock(codigo_prod)
    print(f"\n¡Entrada {nuevo_movimiento['id']} registrada con éxito! Nuevo stock de {prod['nombre']}: {stock_nuevo}")

def registrar_salida_inventario():
    print("--- [RF09] Registrar Salida de Inventario Manual ---")
    codigo_prod = input("Código del producto: ").strip().upper()
    prod = buscar_producto(codigo_prod)

    if not prod:
        print(f"Error: No existe el producto '{codigo_prod}'.")
        return

    stock_disponible = calcular_stock(codigo_prod)
    print(f"Producto: {prod['nombre']} | Stock actual disponible: {stock_disponible}")

    try:
        cantidad = float(input("Cantidad a retirar: "))
        if cantidad <= 0:
            print("Error: La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Debe ingresar un valor numérico.")
        return

    if cantidad > stock_disponible:
        print(f"\nError (PF005): Stock insuficiente. Intenta retirar {cantidad} pero solo hay {stock_disponible} disponibles. Operación denegada.")
        return

    motivo = input("Motivo de la salida (ej. merma, donación, autoconsumo): ").strip()
    if not motivo:
        motivo = "Salida manual de inventario"

    nuevo_movimiento = {
        "id": generar_id_movimiento(),
        "producto_codigo": codigo_prod,
        "tipo": "SALIDA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    movimientos.append(nuevo_movimiento)
    guardar_todos_los_datos()
    stock_nuevo = calcular_stock(codigo_prod)
    print(f"\n¡Salida {nuevo_movimiento['id']} registrada con éxito! Stock restante de {prod['nombre']}: {stock_nuevo}")

def consultar_movimientos():
    print("--- Historial de Movimientos de Inventario ---")
    if not movimientos:
        print("\nNo existen movimientos de inventario registrados.")
        return

    print("\n" + "="*95)
    print(f"{'ID MOV':<8} | {'FECHA':<16} | {'CÓD PROD':<10} | {'TIPO':<10} | {'CANTIDAD':<10} | {'MOTIVO':<30}")
    print("="*95)
    for m in movimientos:
        print(f"{m['id']:<8} | {m['fecha']:<16} | {m['producto_codigo']:<10} | {m['tipo']:<10} | {m['cantidad']:<10.1f} | {m['motivo']:<30}")
    print("="*95)

def menu_movimientos():
    while True:
        limpiar_pantalla()
        print("==================== MOVIMIENTOS DE INVENTARIO ====================")
        print("1. Registrar Entrada manual")
        print("2. Registrar Salida manual")
        print("3. Consultar historial de movimientos")
        print("0. Volver al menú principal")
        print("===================================================================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            limpiar_pantalla()
            registrar_entrada_inventario()
            pausar()
        elif opcion == "2":
            limpiar_pantalla()
            registrar_salida_inventario()
            pausar()
        elif opcion == "3":
            limpiar_pantalla()
            consultar_movimientos()
            pausar()
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            pausar()

# --- MÓDULO VENTAS ---

def registrar_venta():
    print("--- [RF10 - RF11] Registrar Nueva Venta ---")
    items_venta = []
    total_venta = 0.0

    while True:
        codigo_prod = input("\nIngrese código de producto a agregar (o presione ENTER para finalizar): ").strip().upper()
        if not codigo_prod:
            break

        prod = buscar_producto(codigo_prod)
        if not prod:
            print(f"Error: Producto con código '{codigo_prod}' no existe.")
            continue

        if not prod["activo"]:
            print(f"Error: El producto '{prod['nombre']}' está DESACTIVADO.")
            continue

        stock_disponible = calcular_stock(codigo_prod)
        
        cant_ya_agregada = sum(item["codigo"] == codigo_prod for item in items_venta)
        cant_ya_agregada_val = sum(item["cantidad"] for item in items_venta if item["codigo"] == codigo_prod)
        stock_efectivo = stock_disponible - cant_ya_agregada_val

        print(f"Producto: {prod['nombre']} | Precio: ${prod['precio']:.2f} | Stock disponible: {stock_efectivo}")

        try:
            cantidad = float(input("Cantidad a vender: "))
            if cantidad <= 0:
                print("Error: La cantidad debe ser mayor a 0.")
                continue
        except ValueError:
            print("Error: Ingrese una cantidad numérica válida.")
            continue

        if cantidad > stock_efectivo:
            print(f"Error: Cantidad excede el stock disponible ({stock_efectivo}).")
            continue

        subtotal = cantidad * prod["precio"]
        
        items_venta.append({
            "codigo": prod["codigo"],
            "nombre": prod["nombre"],
            "cantidad": cantidad,
            "precio_unitario": prod["precio"],
            "subtotal": subtotal
        })

        total_venta += subtotal
        print(f"-> Agregado: {cantidad} x {prod['nombre']} = ${subtotal:.2f}")

        otra = input("¿Desea agregar otro producto a la venta? (s/n): ").strip().lower()
        if otra != 's':
            break

    if not items_venta:
        print("\nVenta cancelada: No se ingresó ningún producto válido.")
        return

    id_venta = generar_id_venta()
    fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M")

    nueva_venta = {
        "id": id_venta,
        "fecha": fecha_venta,
        "items": [
            {
                "codigo": it["codigo"],
                "cantidad": it["cantidad"],
                "precio_unitario": it["precio_unitario"]
            } for it in items_venta
        ],
        "total": total_venta
    }

    ventas.append(nueva_venta)

    for it in items_venta:
        mov = {
            "id": generar_id_movimiento(),
            "producto_codigo": it["codigo"],
            "tipo": "SALIDA",
            "cantidad": it["cantidad"],
            "motivo": f"Venta {id_venta}",
            "fecha": fecha_venta
        }
        movimientos.append(mov)

    guardar_todos_los_datos()

    print("\n" + "="*60)
    print(f"           COMPROBANTE DE VENTA {id_venta}")
    print(f"Fecha: {fecha_venta}")
    print("="*60)
    for it in items_venta:
        print(f"{it['nombre']:<25} | {it['cantidad']:>5.1f} x ${it['precio_unitario']:<8.2f} = ${it['subtotal']:>8.2f}")
    print("-" * 60)
    print(f"TOTAL DE LA VENTA: ${total_venta:.2f}")
    print("="*60)
    print("¡Venta registrada exitosamente!")

def consultar_ventas():
    print("--- [RF14] Consultar Ventas Registradas ---")
    if not ventas:
        print("\nNo existen ventas registradas en el sistema.")
        return

    print("\n" + "="*70)
    print(f"{'ID VENTA':<10} | {'FECHA':<18} | {'Nº ÍTEMS':<10} | {'TOTAL ($)':<15}")
    print("="*70)
    for v in ventas:
        num_items = len(v["items"])
        print(f"{v['id']:<10} | {v['fecha']:<18} | {num_items:<10} | ${v['total']:<15.2f}")
    print("="*70)

# --- MÓDULO ALERTAS Y REPORTES (RF12 - RF14) ---

def consultar_alertas_stock():
    print("--- [RF12] Alertas de Stock Bajo o Crítico ---")
    alertas = []

    for p in productos:
        if p["activo"]:
            stk_actual = calcular_stock(p["codigo"])
            if stk_actual <= p["stock_minimo"]:
                alertas.append((p, stk_actual))

    if not alertas:
        print("\n¡Excelente! Todos los productos activos tienen niveles de stock por encima del mínimo de seguridad.")
        return

    print("\n¡ATENCIÓN! Los siguientes productos requieren reabastecimiento urgente:")
    print("="*85)
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<25} | {'STOCK ACTUAL':<14} | {'STOCK MÍNIMO':<14} | {'ESTADO':<15}")
    print("="*85)
    for p, stk in alertas:
        estado = "AGOTADO" if stk == 0 else "STOCK BAJO"
        print(f"{p['codigo']:<10} | {p['nombre']:<25} | {stk:<14.1f} | {p['stock_minimo']:<14.1f} | {estado:<15}")
    print("="*85)

def reporte_ingresos_por_fecha():
    print("--- [RF13] Reporte de Ingresos por Rango de Fechas ---")
    if not ventas:
        print("\nNo hay ventas para analizar.")
        return

    f_inicio = input("Fecha inicial (AAAA-MM-DD) [dejar vacío para ver todo]: ").strip()
    f_fin = input("Fecha final (AAAA-MM-DD) [dejar vacío para ver todo]: ").strip()

    ventas_filtradas = []
    total_ingresos = 0.0

    for v in ventas:
        fecha_v_str = v["fecha"].split(" ")[0]  # Obtener AAAA-MM-DD
        cumple_inicio = (not f_inicio) or (fecha_v_str >= f_inicio)
        cumple_fin = (not f_fin) or (fecha_v_str <= f_fin)

        if cumple_inicio and cumple_fin:
            ventas_filtradas.append(v)
            total_ingresos += v["total"]

    if not ventas_filtradas:
        print("\nNo se registraron ventas en el rango de fechas especificado.")
        return

    print("\n" + "="*70)
    print(f"REPORTE DE INGRESOS ({f_inicio or 'Inicio'} al {f_fin or 'Actualidad'})")
    print("="*70)
    print(f"{'ID VENTA':<10} | {'FECHA / HORA':<18} | {'Nº ÍTEMS':<10} | {'TOTAL ($)':<15}")
    print("-" * 70)
    for v in ventas_filtradas:
        print(f"{v['id']:<10} | {v['fecha']:<18} | {len(v['items']):<10} | ${v['total']:<15.2f}")
    print("="*70)
    print(f"TOTAL INGRESOS GENERADOS: ${total_ingresos:.2f}")
    print("="*70)

def reporte_unidades_vendidas():
    print("--- [RF14] Reporte de Unidades Vendidas por Producto ---")
    if not ventas:
        print("\nNo hay ventas registradas.")
        return

    resumen_ventas = {}

    for v in ventas:
        for it in v["items"]:
            cod = it["codigo"]
            cant = it["cantidad"]
            subt = cant * it["precio_unitario"]

            if cod not in resumen_ventas:
                resumen_ventas[cod] = {"cantidad": 0.0, "recaudado": 0.0}

            resumen_ventas[cod]["cantidad"] += cant
            resumen_ventas[cod]["recaudado"] += subt

    print("\n" + "="*80)
    print(f"{'CÓDIGO':<10} | {'NOMBRE PRODUCTO':<25} | {'UNID VENDIDAS':<15} | {'RECAUDADO ($)':<15}")
    print("="*80)
    for cod, datos in resumen_ventas.items():
        prod = buscar_producto(cod)
        nombre = prod["nombre"] if prod else "Desconocido/Eliminado"
        print(f"{cod:<10} | {nombre:<25} | {datos['cantidad']:<15.1f} | ${datos['recaudado']:<15.2f}")
    print("="*80)

def menu_reportes():
    while True:
        limpiar_pantalla()
        print("==================== MÓDULO DE REPORTES ====================")
        print("1. Reporte de ingresos por rango de fechas [RF13]")
        print("2. Reporte de unidades vendidas por producto [RF14]")
        print("0. Volver al menú principal")
        print("============================================================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            limpiar_pantalla()
            reporte_ingresos_por_fecha()
            pausar()
        elif opcion == "2":
            limpiar_pantalla()
            reporte_unidades_vendidas()
            pausar()
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            pausar()

# --- MENÚ PRINCIPAL ---

def mostrar_menu():
    print("==================== AGROCONTROL CBA ====================")
    print("1. Gestión de productos")
    print("2. Gestión de lotes productivos")
    print("3. Movimientos de inventario")
    print("4. Registrar venta")
    print("5. Consultar ventas")
    print("6. Alertas de stock")
    print("7. Reportes")
    print("8. Guardar datos")
    print("0. Salir")
    print("=========================================================")

def main():
    cargar_todos_los_datos()
    while True:
        limpiar_pantalla()
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_lotes()
        elif opcion == "3":
            menu_movimientos()
        elif opcion == "4":
            limpiar_pantalla()
            registrar_venta()
            pausar()
        elif opcion == "5":
            limpiar_pantalla()
            consultar_ventas()
            pausar()
        elif opcion == "6":
            limpiar_pantalla()
            consultar_alertas_stock()
            pausar()
        elif opcion == "7":
            menu_reportes()
        elif opcion == "8":
            guardar_todos_los_datos()
            print("\n¡Datos guardados exitosamente en archivos JSON!")
            pausar()
        elif opcion == "0":
            guardar_todos_los_datos()
            print("\n¡Datos guardados! Gracias por usar AgroControl CBA.")
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            pausar()

if __name__ == "__main__":
    main()