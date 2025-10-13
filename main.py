from motor import logica_reglas, logica_pesos
from gui.app_gui import iniciar_aplicacion
from api_server import iniciar_api

def seleccionar_motor():
    """ Pide al usuario que elija qué motor de inferencia usar. """
    while True:
        print("\n--- Selección del Motor de Inferencia ---")
        print("1. Motor Simple (Basado en Reglas SI/ENTONCES)")
        print("2. Motor Avanzado (Basado en Puntuación/Pesos)")
        opcion = input("Seleccione el motor a utilizar > ").strip()
        if opcion == "1":
            print("\n✅ Usando el motor de REGLAS.")
            return logica_reglas
        elif opcion == "2":
            print("\n✅ Usando el motor de PUNTUACIÓN.")
            return logica_pesos
        else:
            print("Opción no válida.")

def main():
    """ Función principal que permite al usuario elegir el motor y la interfaz. """
    motor_seleccionado = seleccionar_motor()

    while True:
        print("\n--- Lanzador del Sistema Experto ---")
        print("1. Ejecutar como Aplicación de Escritorio (GUI)")
        print("2. Ejecutar como Servidor Web (API)")
        print("3. Cambiar de motor")
        print("4. Salir")

        opcion = input("Seleccione una opción > ").strip()

        if opcion == "1":
            print("\nIniciando la aplicación de escritorio...")
            # Le pasamos el motor seleccionado a la GUI
            iniciar_aplicacion(motor_seleccionado)
        elif opcion == "2":
            print("\nIniciando el servidor web...")
            try:
                # Le pasamos el motor seleccionado a la API
                iniciar_api(motor_seleccionado)
            except KeyboardInterrupt:
                print("\nServidor detenido.")
        elif opcion == "3":
            motor_seleccionado = seleccionar_motor()
        elif opcion == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()