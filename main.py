# Archivo: main.py (Versión Final Web-Only)

from api_server import iniciar_api

def main():
    """
    Función principal que inicia directamente el servidor web.
    """
    print("Iniciando el Sistema Experto (Servidor Web)...")
    try:
        iniciar_api()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"\nError al iniciar el servidor: {e}")
    finally:
        print("Aplicación cerrada. ¡Hasta luego!")


if __name__ == "__main__":
    main()