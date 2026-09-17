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
    """Asegura que la carpeta data exista."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def cargar_json(ruta_archivo):
    """Carga datos desde un archivo JSON. Retorna lista vacía si no existe o está corrupto."""
    if not ruta_archivo.exists():
        return []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

def guardar_json(datos, ruta_archivo):
    """Guarda una estructura de datos en el archivo JSON correspondiente."""
    garantizar_directorio()
    with open(ruta_archivo, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=4)

def cargar_todos_los_datos():
    """Carga todos los datos al iniciar la aplicación (RF17)."""
    global productos, lotes, movimientos, ventas
    productos = cargar_json(PRODUCTOS_FILE)
    lotes = cargar_json(LOTES_FILE)
    movimientos = cargar_json(MOVIMIENTOS_FILE)
    ventas = cargar_json(VENTAS_FILE)

def guardar_todos_los_datos():
    """Guarda el estado global actual en los archivos JSON (RF16)."""
    guardar_json(productos, PRODUCTOS_FILE)
    guardar_json(lotes, LOTES_FILE)
    guardar_json(movimientos, MOVIMIENTOS_FILE)
    guardar_json(ventas, VENTAS_FILE)

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPresione Enter para continuar...")

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
            print("\n--- [1] Gestión de productos ---")
            pausar()
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