# Archivo: motor/logica.py
# Contiene la lógica central del Sistema Experto:
# 1. Carga y valida la Base de Conocimiento desde 'base_conocimiento.json'.
# 2. Proporciona funciones para acceder a los Hechos (síntomas) y Categorías.
# 3. Implementa el Motor de Inferencia basado en reglas SI...ENTONCES...
# 4. Incluye una simulación de Módulo ML como fallback.

import json
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional, Any

# --- 1. Definición de la Estructura de la Base de Conocimiento ---
# Usamos Pydantic para definir cómo deben ser los datos en el JSON.

class Hecho(BaseModel):
    """Representa un síntoma o 'hecho' observable."""
    id: str         # Identificador único (ej: "pc_no_enciende")
    pregunta: str   # Texto a mostrar al usuario (ej: "La PC no enciende...")
    categoria: str  # Categoría a la que pertenece (ej: "hardware", "software")

class Regla(BaseModel):
    """Representa una regla SI...ENTONCES..."""
    diagnostico: str   # El texto del diagnóstico (conclusión)
    condiciones: List[str] # Lista de IDs de Hechos que deben cumplirse (ej: ["pc_no_enciende", "NOT:hace_pitidos"])

class BaseConocimiento(BaseModel):
    """Modelo principal que valida la estructura completa del archivo JSON."""
    hechos: List[Hecho]
    reglas: List[Regla]
    # Diccionario opcional para sugerencias rápidas con un solo síntoma ambiguo
    diagnosticos_sintoma_unico: Optional[Dict[str, str]] = Field(default_factory=dict)

    # Validador avanzado: Se ejecuta después de validar 'hechos', 'reglas', etc.
    # Verifica que las IDs usadas en 'reglas' y 'diagnosticos_sintoma_unico' existan en 'hechos'.
    @model_validator(mode='after')
    def validar_referencias_cruzadas(self) -> 'BaseConocimiento':
        """Asegura que todas las IDs de hechos usadas en reglas y diagnósticos únicos existan."""
        hechos_ids = {h.id for h in self.hechos} # Conjunto con todas las IDs válidas

        # Validar condiciones de las reglas
        for i, regla in enumerate(self.reglas):
            for cond in regla.condiciones:
                cond_id = cond.replace("NOT:", "") # Obtener el ID base
                if cond_id not in hechos_ids:
                    # Si una ID no existe, lanza un error claro que detiene la carga
                    raise ValueError(f"Error en JSON - Regla {i+1} ('{regla.diagnostico[:30]}...'): La condición '{cond_id}' no corresponde a ningún hecho definido.")

        # Validar IDs en diagnosticos_sintoma_unico
        if self.diagnosticos_sintoma_unico:
            for sintoma_id in self.diagnosticos_sintoma_unico.keys():
                 if sintoma_id not in hechos_ids:
                      raise ValueError(f"Error en JSON - diagnosticos_sintoma_unico: La ID '{sintoma_id}' no corresponde a ningún hecho definido.")
                      
        print("Validación cruzada de IDs en JSON completada con éxito.")
        return self # Devuelve el objeto validado

# --- 2. Carga de la Base de Conocimiento desde JSON ---

def cargar_base_conocimiento(archivo_json: str = "base_conocimiento.json") -> BaseConocimiento:
    """
    Carga y valida la base de conocimiento desde el archivo JSON especificado.
    Utiliza los modelos Pydantic para asegurar la estructura correcta.
    """
    print(f"Intentando cargar la base de conocimiento desde: {archivo_json}")
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            # Pydantic valida la estructura y las referencias cruzadas al crear el objeto
            base = BaseConocimiento(**datos) 
            print(f"Base de conocimiento cargada y validada: {len(base.hechos)} hechos, {len(base.reglas)} reglas.")
            return base
    except FileNotFoundError:
        # Error crítico si no se encuentra el archivo
        print(f"Error CRÍTICO: No se encontró el archivo de base de conocimiento '{archivo_json}'. La aplicación no puede continuar.")
        raise SystemExit(f"Archivo no encontrado: {archivo_json}") # Detiene la ejecución
    except json.JSONDecodeError as e:
        # Error si el JSON está mal formado
        print(f"Error CRÍTICO: El archivo '{archivo_json}' tiene un formato JSON inválido. Revisa la sintaxis cerca de: {e}")
        raise SystemExit(f"JSON inválido: {archivo_json}")
    except ValueError as e: # Captura errores de validación de Pydantic (lanzados desde el model_validator)
        # Error si las IDs no coinciden o la estructura es incorrecta
        print(f"Error CRÍTICO al validar la estructura de '{archivo_json}': {e}")
        raise SystemExit(f"Error de validación en JSON: {e}")
    except Exception as e: 
        # Captura cualquier otro error inesperado durante la carga/validación
        print(f"Error CRÍTICO inesperado al cargar la base de conocimiento: {e}")
        raise SystemExit(f"Error inesperado: {e}")

# --- Instancia Global de la Base de Conocimiento ---
# Se carga una sola vez cuando se importa este módulo.
# Si hay un error aquí, la aplicación se detendrá.
BASE_CONOCIMIENTO = cargar_base_conocimiento() 
# Diccionario para acceder rápidamente a los detalles de un hecho por su ID
HECHOS_POR_ID: Dict[str, Hecho] = {hecho.id: hecho for hecho in BASE_CONOCIMIENTO.hechos}

# --- 3. Funciones Auxiliares para la Interfaz de Usuario ---

def get_hechos_por_categoria(categoria: str) -> List[Hecho]:
    """Devuelve la lista de Hechos (síntomas) que pertenecen a una categoría específica."""
    return [hecho for hecho in BASE_CONOCIMIENTO.hechos if hecho.categoria == categoria]

def get_categorias() -> List[str]:
    """Devuelve una lista única y ordenada de todas las categorías disponibles."""
    # Usamos un set para obtener categorías únicas y luego lo ordenamos
    return sorted(list(set(hecho.categoria for hecho in BASE_CONOCIMIENTO.hechos)))

# --- 4. Simulación del Módulo de Machine Learning (Fallback) ---

def _llamar_modulo_ml(hechos_activos_ids: List[str]) -> str:
     """
     Función placeholder que simula la intervención de un módulo de Machine Learning.
     Se activa cuando las reglas SI-ENTONCES no son concluyentes.
     Intenta dar una sugerencia basada en palabras clave de los síntomas activos.
     """
     print(f"INFO: Las reglas SI-ENTONCES no fueron concluyentes para los síntomas: {hechos_activos_ids}. Pasando a Módulo ML (simulado).")
     
     set_hechos_activos = set(hechos_activos_ids)
     sintomas_texto = " ".join(HECHOS_POR_ID[id_hecho].pregunta for id_hecho in hechos_activos_ids if id_hecho in HECHOS_POR_ID).lower()
     
     # Lógica simulada de ML: busca patrones simples y ofrece sugerencias contextuales
     sugerencia_ml = "investigar posibles conflictos de software generales o drivers recientes." # Sugerencia por defecto

     # --- Lógica específica para combinaciones comunes sin regla ---
     if "sistema_lento" in set_hechos_activos and ("no_conecta_wifi" in set_hechos_activos or "wifi_conectado_sin_internet" in set_hechos_activos):
         sugerencia_ml = "revisar si hay software consumiendo mucho ancho de banda (actualizaciones, P2P), buscar malware que afecte la red, o considerar problemas con el router/proveedor que impacten el rendimiento general."
     elif "sistema_lento" in set_hechos_activos and ("programas_cierran" in set_hechos_activos or "mensajes_error_frecuentes" in set_hechos_activos or "pantalla_azul" in set_hechos_activos):
         sugerencia_ml = "buscar actualizaciones del sistema operativo y de las aplicaciones que fallan, verificar la integridad de los archivos del sistema (ejecutar 'sfc /scannow' en CMD como admin), o considerar problemas de RAM."
     elif "imagen_congelada_o_artefactos" in set_hechos_activos and ("sistema_lento" in set_hechos_activos or "programas_cierran" in set_hechos_activos):
          sugerencia_ml = "realizar una instalación limpia de los drivers de la tarjeta gráfica (usando DDU si es necesario), monitorizar las temperaturas de la GPU, o verificar si la fuente de poder es suficiente."
          
     # --- Lógica para síntomas individuales sin regla ni sugerencia única específica ---
     elif "sistema_lento" in set_hechos_activos and not {"ruidos_hdd", "sobrecalentamiento", "programas_cierran", "publicidad_excesiva", "no_conecta_wifi", "wifi_conectado_sin_internet", "pantalla_azul", "mensajes_error_frecuentes", "imagen_congelada_o_artefactos"} & set_hechos_activos:
         sugerencia_ml = "optimizar el sistema operativo (programas de inicio, espacio en disco, desfragmentar HDD), buscar malware o verificar el estado del disco duro/SSD."
     elif ("no_conecta_wifi" in set_hechos_activos or "wifi_conectado_sin_internet" in set_hechos_activos) and not {"sistema_lento"} & set_hechos_activos:
         sugerencia_ml = "revisar la configuración de red (IP/DNS), reiniciar router/módem, actualizar drivers de red o contactar al proveedor de internet."
     elif "imagen_congelada_o_artefactos" in set_hechos_activos and not {"sistema_lento", "programas_cierran"} & set_hechos_activos:
          sugerencia_ml = "actualizar los drivers de la tarjeta gráfica, verificar las conexiones de video o monitorizar temperaturas de la GPU."
     # (Se podrían añadir más 'elif' aquí para otras palabras clave o combinaciones)

     # Construye el mensaje final indicando que es una sugerencia ML simulada
     return (f"Diagnóstico: Las reglas exactas no coinciden. Un análisis avanzado (ML) sugiere {sugerencia_ml} "
             "Considere proporcionar más detalles en la sección 'Otro Problema'. (Módulo ML simulado)")

# --- 5. Motor de Inferencia Principal ---

def motor_de_inferencia(hechos_activos_ids: List[str]) -> Dict[str, Any]:
    """
    Motor de Inferencia principal (v3.3).
    1. Busca la regla SI-ENTONCES más específica que coincida significativamente.
    2. Si no la encuentra, busca una sugerencia para síntoma único.
    3. Si tampoco, llama a la simulación del módulo ML.
    Devuelve un diccionario con el diagnóstico y los síntomas considerados.
    """
    set_hechos_activos = set(hechos_activos_ids) # Convertir a set para eficiencia
    resultado_final: str = "Diagnóstico no determinado" # Valor por defecto

    # --- Manejo de Entrada Vacía ---
    if not set_hechos_activos:
        resultado_final = "Por favor, selecciona al menos un síntoma."
    else:
        # --- Búsqueda de la Mejor Regla Coincidente ---
        mejor_regla_encontrada = None
        # Guarda cuántos síntomas del usuario usa la mejor regla encontrada
        max_condiciones_positivas_coincidentes = -1 
        # Guarda cuántas condiciones tiene en total la mejor regla (para desempatar)
        max_especificidad_regla = -1 

        print(f"\n--- Iniciando Inferencia para: {set_hechos_activos} ---")
        for regla in BASE_CONOCIMIENTO.reglas:
            condiciones_cumplidas = True
            condiciones_positivas_coincidentes_actual = 0
            especificidad_actual = len(regla.condiciones)
            
            # Evaluar cada condición de la regla actual
            for cond in regla.condiciones:
                cond_base = cond.replace("NOT:", "")
                
                if cond.startswith("NOT:"):
                    # Si la condición es NEGADA y el hecho ESTÁ ACTIVO, la regla NO se cumple
                    if cond_base in set_hechos_activos:
                        condiciones_cumplidas = False; break
                else:
                    # Si la condición es POSITIVA y el hecho NO ESTÁ ACTIVO, la regla NO se cumple
                    if cond not in set_hechos_activos:
                        condiciones_cumplidas = False; break
                    else:
                        # Si la condición positiva se cumple, contarla
                        condiciones_positivas_coincidentes_actual += 1
            
            # Si la regla se cumplió completamente...
            if condiciones_cumplidas:
                print(f"Regla CUMPLIDA: '{regla.diagnostico[:40]}...' (Coincidencias: {condiciones_positivas_coincidentes_actual}, Especificidad: {especificidad_actual})")
                # ...verificar si es mejor que la que teníamos guardada
                # Prioridad 1: Que use MÁS síntomas del usuario
                if condiciones_positivas_coincidentes_actual > max_condiciones_positivas_coincidentes:
                    max_condiciones_positivas_coincidentes = condiciones_positivas_coincidentes_actual
                    max_especificidad_regla = especificidad_actual
                    mejor_regla_encontrada = regla
                    print(f"  -> Nueva mejor regla encontrada (más coincidencias).")
                # Prioridad 2 (Desempate): Si usan los mismos síntomas, preferir la que tiene MÁS condiciones en total (más específica)
                elif condiciones_positivas_coincidentes_actual == max_condiciones_positivas_coincidentes and especificidad_actual > max_especificidad_regla:
                    max_especificidad_regla = especificidad_actual
                    mejor_regla_encontrada = regla
                    print(f"  -> Nueva mejor regla encontrada (igual coincidencia, más específica).")
            # else: # Opcional: imprimir por qué falló una regla
            #    print(f"Regla DESCARTADA: '{regla.diagnostico[:40]}...'")

        # --- Decisión Final ---
        # Calcular los hechos activos que NO son condiciones 'NOT:' de la mejor regla
        hechos_activos_positivos_usuario = set_hechos_activos
        if mejor_regla_encontrada:
             condiciones_negadas_regla = {c.replace("NOT:","") for c in mejor_regla_encontrada.condiciones if c.startswith("NOT:")}
             hechos_activos_positivos_usuario = set_hechos_activos - condiciones_negadas_regla
        
        # Aceptar la regla solo si usa TODOS los síntomas POSITIVOS proporcionados por el usuario
        if mejor_regla_encontrada and max_condiciones_positivas_coincidentes == len(hechos_activos_positivos_usuario):
            print(f"-> DECISIÓN: Usar regla exacta: '{mejor_regla_encontrada.diagnostico[:40]}...'")
            resultado_final = mejor_regla_encontrada.diagnostico
        
        # Si no hay regla exacta adecuada, y es solo UN síntoma, buscar sugerencia
        elif len(set_hechos_activos) == 1:
            sintoma_unico_id = list(set_hechos_activos)[0]
            if BASE_CONOCIMIENTO.diagnosticos_sintoma_unico and sintoma_unico_id in BASE_CONOCIMIENTO.diagnosticos_sintoma_unico:
                print(f"-> DECISIÓN: Usar diagnóstico para síntoma único: '{sintoma_unico_id}'")
                resultado_final = BASE_CONOCIMIENTO.diagnosticos_sintoma_unico[sintoma_unico_id]
            else: 
                # Si es síntoma único pero sin sugerencia específica -> ML
                print(f"-> DECISIÓN: Síntoma único '{sintoma_unico_id}' sin sugerencia. Llamar a ML.")
                resultado_final = _llamar_modulo_ml(hechos_activos_ids)
        
        # Si hay múltiples síntomas pero ninguna regla los explica bien -> ML
        else:
             print(f"-> DECISIÓN: Múltiples síntomas sin regla adecuada. Llamar a ML.")
             resultado_final = _llamar_modulo_ml(hechos_activos_ids)
             
        print(f"--- Fin Inferencia ---")

    # --- Devolver el Resultado ---
    # Devuelve un diccionario compatible con la interfaz
    return {
        "diagnostico": resultado_final,
        "sintomas_pasados_ids": hechos_activos_ids # Devuelve los IDs originales
    }