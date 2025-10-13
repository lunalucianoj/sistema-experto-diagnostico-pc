from pydantic import BaseModel

# La definición de los hechos no cambia
class SintomasPC(BaseModel):
    pc_no_enciende: bool = False
    pantalla_sin_video: bool = False
    sistema_operativo_lento: bool = False
    ruidos_extranos_hdd: bool = False
    periferico_no_funciona: bool = False
    hace_pitidos_al_arrancar: bool = False
    mensajes_de_error_os: bool = False

# --- NUEVA BASE DE CONOCIMIENTO BASADA EN PESOS ---
# Aquí definimos cada posible diagnóstico y qué síntomas le aportan "puntos".
DIAGNOSTICOS = [
    {
        "nombre": "Falla Crítica de Hardware (RAM/Video)",
        "pesos": {
            "pc_no_enciende": 10,
            "hace_pitidos_al_arrancar": 20  # Síntoma clave, muy alto peso
        },
        "descripcion": "Diagnóstico: Falla crítica de hardware detectada (RAM o Video). La secuencia de pitidos al arrancar es un código de error. Consulta el manual de tu placa base."
    },
    {
        "nombre": "Falla de Fuente de Poder",
        "pesos": {
            "pc_no_enciende": 15, # Muy probable si no enciende y no hay pitidos
            "periferico_no_funciona": 2
        },
        "descripcion": "Diagnóstico: Falla de alimentación. Verifica el cable de alimentación. Si todo está correcto, la fuente de poder es la causa más probable."
    },
    {
        "nombre": "Falla de Disco Duro",
        "pesos": {
            "sistema_operativo_lento": 8,
            "ruidos_extranos_hdd": 25, # Síntoma clave, ¡casi definitivo!
            "mensajes_de_error_os": 5
        },
        "descripcion": "Diagnóstico: ¡ALERTA! Falla mecánica del disco duro. Realiza una copia de seguridad de tus datos de inmediato y reemplaza el disco."
    },
    {
        "nombre": "Problema del Sistema Operativo",
        "pesos": {
            "sistema_operativo_lento": 10,
            "mensajes_de_error_os": 15, # Síntoma clave
        },
        "descripcion": "Diagnóstico: Falla grave del sistema operativo (drivers, virus, etc.). Considera restaurar el sistema a un punto anterior o realizar un escaneo."
    },
    {
        "nombre": "Problema de Conexión de Video",
        "pesos": {
            "pantalla_sin_video": 15
        },
        "descripcion": "Diagnóstico: Problema de señal de video. Asegúrate de que el monitor esté encendido y el cable de video esté firmemente conectado."
    },
    {
        "nombre": "Falla de Periférico",
        "pesos": {
            "periferico_no_funciona": 15
        },
        "descripcion": "Diagnóstico: Falla de un periférico. Prueba conectando el dispositivo en otro puerto USB. Si es inalámbrico, comprueba las baterías."
    }
]

def motor_de_inferencia(sintomas: SintomasPC) -> str:
    """
    Motor de inferencia basado en un sistema de puntuación.
    Calcula el diagnóstico más probable.
    """
    puntajes = {diag["nombre"]: 0 for diag in DIAGNOSTICOS}
    sintomas_activos = {s for s, activo in sintomas.model_dump().items() if activo}

    # Si no se seleccionó ningún síntoma, no podemos diagnosticar.
    if not sintomas_activos:
        return "Por favor, selecciona al menos un síntoma para poder realizar el diagnóstico."

    # Calcular puntajes
    for sintoma in sintomas_activos:
        for diagnostico in DIAGNOSTICOS:
            if sintoma in diagnostico["pesos"]:
                puntajes[diagnostico["nombre"]] += diagnostico["pesos"][sintoma]

    # Encontrar el diagnóstico con el puntaje más alto
    diagnostico_mas_probable = max(puntajes, key=puntajes.get)
    puntaje_maximo = puntajes[diagnostico_mas_probable]

    # Umbral de confianza: si el puntaje máximo es muy bajo, la información es insuficiente.
    UMBRAL_MINIMO = 10
    if puntaje_maximo < UMBRAL_MINIMO:
        return ("Diagnóstico: La información es insuficiente para un diagnóstico preciso. "
                "Por favor, proporciona más síntomas si es posible.")

    # Devolver la descripción del diagnóstico ganador
    for diag in DIAGNOSTICOS:
        if diag["nombre"] == diagnostico_mas_probable:
            return diag["descripcion"]

    # Esto nunca debería pasar, pero es una salvaguarda.
    return "Error inesperado en el motor de inferencia."