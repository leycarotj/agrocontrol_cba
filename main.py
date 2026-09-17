import os

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
            print("\n--- [8] Guardar datos ---")
            pausar()
        elif opcion == "0":
            print("\n¡Gracias por usar AgroControl CBA!")
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            pausar()

if __name__ == "__main__":
    main()