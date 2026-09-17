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
    """Genera IDs secuenciales para movimientos de inventario (ej. M0001)."""
    siguiente_num = len(movimientos) + 1
    return f"M{siguiente_num:04d}"

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

    print("\n" + "="*80)
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<25} | {'CATEGORÍA':<15} | {'PRECIO ($)':<12} | {'STK MIN':<8}")
    print("="*80)
    for p in encontrados:
        print(f"{p['codigo']:<10} | {p['nombre']:<25} | {p['categoria']:<15} | {p['precio']:<12.2f} | {p['stock_minimo']:<8.1f}")
    print("="*80)

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

# --- MÓDULO LOTES PRODUCTIVOS (RF05 - RF07) ---

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

    # Actualizar estado del lote
    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    # Generar ENTRADA automática de inventario
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
    print(f"Se generó automáticamente el movimiento de entrada {nuevo_movimiento['id']} de {cantidad} unidades para el producto {lote['producto_codigo']}.")

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
            print("\n--- [3] Movimientos de inventario ---")
            pausar()
        elif opcion == "4":
            print("\n--- [4] Registrar venta ---")
            pausar()
        elif opcion == "5":
            print("\n--- [5] Consultar ventas ---")
            pausar()
        elif opcion == "6":
            print("\n--- [6] Alertas de stock ---")
            pausar()
        elif opcion == "7":
            print("\n--- [7] Reportes ---")
            pausar()
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