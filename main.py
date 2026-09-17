import os
import json
from pathlib import Path

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

# --- AUXILIARES INTERFAZ ---

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

# --- MÓDULO PRODUCTOS (RF01 - RF04) ---

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
            print("\n--- [2] Gestión de lotes productivos ---")
            pausar()
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