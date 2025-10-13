from pydantic import BaseModel

class SintomasPC(BaseModel):
    """
    Define la estructura de los hechos (síntomas) que se recibirán.
    Cada síntoma es un booleano, donde 'True' significa que el síntoma está presente.
    """
    pc_no_enciende: bool = False
    pantalla_sin_video: bool = False
    sistema_operativo_lento: bool = False
    ruidos_extranos_hdd: bool = False
    periferico_no_funciona: bool = False
    hace_pitidos_al_arrancar: bool = False
    mensajes_de_error_os: bool = False

def motor_de_inferencia(sintomas: SintomasPC) -> str:
    """
    Motor de Inferencia mejorado con reglas más específicas.
    """
    # --- Base de Conocimiento (Reglas Mejoradas) ---

    # Regla 1: Falla de RAM o Tarjeta de Video (muy específica)
    if sintomas.pc_no_enciende and sintomas.hace_pitidos_al_arrancar:
        return ("Diagnóstico: Falla crítica de hardware detectada (RAM o Video). "
                "La secuencia de pitidos al arrancar es un código de error. "
                "Consulta el manual de tu placa base para interpretar el código y localizar el componente dañado.")

    # Regla 2: Falla de Fuente de Poder (más precisa)
    if sintomas.pc_no_enciende and not sintomas.hace_pitidos_al_arrancar:
        return ("Diagnóstico: Falla de alimentación. La PC no recibe energía. "
                "Verifica que el cable de alimentación esté bien conectado a la pared y a la PC. "
                "Si todo está correcto, la fuente de poder es la causa más probable.")

    # Regla 3: Problema de Conexión de Video (más clara)
    if not sintomas.pc_no_enciende and sintomas.pantalla_sin_video:
        return ("Diagnóstico: Problema de señal de video. La PC enciende pero no envía imagen al monitor. "
                "Asegúrate de que el monitor esté encendido y que el cable de video (HDMI, DisplayPort, etc.) "
                "esté firmemente conectado en ambos extremos.")

    # Regla 4: Falla de Disco Duro (crítica)
    if sintomas.sistema_operativo_lento and sintomas.ruidos_extranos_hdd:
        return ("Diagnóstico: ¡ALERTA! Falla mecánica del disco duro. "
                "Los ruidos y la lentitud son síntomas de una falla inminente. "
                "Realiza una copia de seguridad de tus datos importantes de inmediato y reemplaza el disco.")

    # Regla 5: Problema de Sistema Operativo (software)
    if sintomas.sistema_operativo_lento and sintomas.mensajes_de_error_os:
        return ("Diagnóstico: Falla grave del sistema operativo. "
                "Las 'pantallas azules' o errores similares pueden ser causados por drivers corruptos, "
                "actualizaciones fallidas o malware. Considera restaurar el sistema a un punto anterior.")

    # Regla 6: Falla de Periféricos (general)
    if (sintomas.periferico_no_funciona and
            not sintomas.pc_no_enciende and
            not sintomas.pantalla_sin_video and
            not sintomas.sistema_operativo_lento):
        return ("Diagnóstico: Falla de un periférico. "
                "Prueba conectando el dispositivo (mouse, teclado, etc.) en otro puerto USB. "
                "Si es inalámbrico, comprueba las baterías o el receptor.")

    # Regla por defecto
    return ("Diagnóstico: No se pudo determinar la falla con los síntomas proporcionados. "
            "Si los problemas persisten, se recomienda una revisión técnica profesional.")
