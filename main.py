# Archivo: main.py (Versión Final Web-Only)

from api_server import iniciar_api

def main():
    """
    Función principal que inicia directamente el servidor web.
    """
    print("Iniciando el Sistema Experto (Servidor Web)...")
    try:
        # Llama a la función que inicia el servidor FastAPI/Uvicorn
        iniciar_api()
    except KeyboardInterrupt:
        # Maneja la interrupción del usuario (Ctrl+C) de forma limpia
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        # Captura cualquier otro error que pueda ocurrir al iniciar el servidor
        print(f"\nError al iniciar el servidor: {e}")
    finally:
        # Este mensaje se imprime siempre al finalizar, ya sea normal o por error
        print("Aplicación cerrada. ¡Hasta luego!")


# Construcción estándar de Python:
# Asegura que la función main() solo se ejecute cuando
# este archivo ('main.py') es ejecutado directamente.
if __name__ == "__main__":
    main()