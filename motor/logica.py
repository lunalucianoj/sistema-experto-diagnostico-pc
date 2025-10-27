# Archivo: motor/logica.py (Versión 3.1 - Validadores Corregidos para Pydantic v2)

import json
from pydantic import BaseModel, Field, field_validator, model_validator # Importamos model_validator
from typing import List, Dict, Optional, Any

# --- Modelos Pydantic (sin cambios) ---
class Hecho(BaseModel):
    id: str
    pregunta: str
    categoria: str

class Regla(BaseModel):
    diagnostico: str
    condiciones: List[str]

# --- Modelo Principal con Validadores CORREGIDOS ---
class BaseConocimiento(BaseModel):
    hechos: List[Hecho]
    reglas: List[Regla]
    diagnosticos_sintoma_unico: Optional[Dict[str, str]] = Field(default_factory=dict)

    # Usamos model_validator para validar dependencias entre campos
    @model_validator(mode='after') # Se ejecuta después de validar hechos, reglas, etc. individualmente
    def validar_referencias_cruzadas(self) -> 'BaseConocimiento':
        hechos_ids = {h.id for h in self.hechos}

        # Validar condiciones de las reglas
        for i, regla in enumerate(self.reglas):
            for cond in regla.condiciones:
                cond_id = cond.replace("NOT:", "")
                if cond_id not in hechos_ids:
                    raise ValueError(f"Regla {i+1} ('{regla.diagnostico[:30]}...') usa condición '{cond_id}' que no existe en los hechos.")

        # Validar IDs en diagnosticos_sintoma_unico
        if self.diagnosticos_sintoma_unico: # Verificar si el diccionario existe y no está vacío
            for sintoma_id in self.diagnosticos_sintoma_unico.keys():
                 if sintoma_id not in hechos_ids:
                      raise ValueError(f"diagnosticos_sintoma_unico usa ID '{sintoma_id}' que no existe en los hechos.")
                      
        return self # Importante: el validador debe devolver el objeto validado

# --- Carga de la Base de Conocimiento (sin cambios) ---
def cargar_base_conocimiento(archivo_json: str = "base_conocimiento.json") -> BaseConocimiento:
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            base = BaseConocimiento(**datos) # La validación ocurre aquí
            print(f"Base de conocimiento cargada y validada desde '{archivo_json}'...")
            return base
    except FileNotFoundError:
        print(f"Error CRÍTICO: No se encontró el archivo '{archivo_json}'")
        raise
    except json.JSONDecodeError:
        print(f"Error CRÍTICO: El archivo '{archivo_json}' tiene un formato JSON inválido.")
        raise
    except Exception as e: # Captura errores de validación de Pydantic y otros
        print(f"Error CRÍTICO al cargar o validar la base de conocimiento: {e}")
        raise

BASE_CONOCIMIENTO = cargar_base_conocimiento()
HECHOS_POR_ID: Dict[str, Hecho] = {hecho.id: hecho for hecho in BASE_CONOCIMIENTO.hechos}

# --- Funciones para la Interfaz (sin cambios) ---
def get_hechos_por_categoria(categoria: str) -> List[Hecho]:
    return [hecho for hecho in BASE_CONOCIMIENTO.hechos if hecho.categoria == categoria]

def get_categorias() -> List[str]:
    return sorted(list(set(hecho.categoria for hecho in BASE_CONOCIMIENTO.hechos)))

def _llamar_modulo_ml(hechos_activos_ids: List[str]) -> str:
     """ Placeholder MEJORADO para la integración del módulo ML. """
     print(f"INFO: Reglas no concluyentes para {hechos_activos_ids}. Pasando a módulo ML (simulado).")
     
     # Lógica simulada simple: buscar palabras clave en los síntomas
     sintomas_texto = " ".join(HECHOS_POR_ID[id_hecho].pregunta for id_hecho in hechos_activos_ids if id_hecho in HECHOS_POR_ID).lower()
     
     sugerencia_ml = "investigar posibles conflictos de software o drivers recientes." # Sugerencia por defecto
     
     if "lento" in sintomas_texto and "disco" not in sintomas_texto and "caliente" not in sintomas_texto:
         sugerencia_ml = "optimizar el sistema operativo (programas de inicio, espacio en disco) o buscar malware."
     elif "wifi" in sintomas_texto or "internet" in sintomas_texto:
         sugerencia_ml = "revisar la configuración de red, reiniciar el router/módem o actualizar los drivers de red."
     elif "video" in sintomas_texto or "pantalla" in sintomas_texto or "imagen" in sintomas_texto:
          sugerencia_ml = "actualizar los drivers de la tarjeta gráfica o verificar las conexiones de video."
          
     return (f"Diagnóstico: Las reglas exactas no coinciden. Un análisis avanzado (ML) sugiere {sugerencia_ml} "
             "Considere proporcionar más detalles en la sección 'Otro Problema'. (Módulo ML simulado)")

def motor_de_inferencia(hechos_activos_ids: List[str]) -> Dict[str, Any]: # Cambiado para devolver un Diccionario
    """
    Motor de inferencia v3.1: Devuelve un diccionario con diagnóstico y síntomas.
    """
    set_hechos_activos = set(hechos_activos_ids)
    
    resultado_final: str = "Diagnóstico no determinado" # Valor inicial por defecto
    
    if not set_hechos_activos:
         resultado_final = "Por favor, selecciona al menos un síntoma."
    else:
        diagnostico_encontrado = None
        max_condiciones_cumplidas = -1

        # 1. Búsqueda de Regla Exacta
        for regla in BASE_CONOCIMIENTO.reglas:
            condiciones_cumplidas = True
            num_condiciones = 0
            condiciones_de_esta_regla = set() # Guardamos las condiciones para saber qué tan específica es

            for cond in regla.condiciones:
                num_condiciones += 1
                condiciones_de_esta_regla.add(cond.replace("NOT:", "")) # Añadimos el ID base
                if cond.startswith("NOT:"):
                    cond_id = cond.replace("NOT:", "")
                    if cond_id in set_hechos_activos:
                        condiciones_cumplidas = False; break
                else:
                    if cond not in set_hechos_activos:
                        condiciones_cumplidas = False; break
            
            # Si se cumplen y es más específica que la anterior encontrada
            if condiciones_cumplidas and num_condiciones > max_condiciones_cumplidas:
                 # ¡Importante! Asegurarse que la regla usa TODOS los síntomas activos para ser considerada la mejor
                 # Opcional: Podrías querer la regla que usa MÁS síntomas activos, incluso si no son todos.
                 # Por ahora, buscamos la regla más específica que se cumpla con los síntomas dados.
                max_condiciones_cumplidas = num_condiciones
                diagnostico_encontrado = regla.diagnostico

        # 2. Asignar resultado si se encontró regla
        if diagnostico_encontrado:
            resultado_final = diagnostico_encontrado
        # 3. Si no, y hay un solo síntoma ambiguo
        elif len(set_hechos_activos) == 1:
            sintoma_unico_id = list(set_hechos_activos)[0]
            if BASE_CONOCIMIENTO.diagnosticos_sintoma_unico and sintoma_unico_id in BASE_CONOCIMIENTO.diagnosticos_sintoma_unico:
                resultado_final = BASE_CONOCIMIENTO.diagnosticos_sintoma_unico[sintoma_unico_id]
            else: # Si es un síntoma único pero no está en los sugeridos, ir a ML
                 resultado_final = _llamar_modulo_ml(hechos_activos_ids)
        # 4. Si no aplican los anteriores (múltiples síntomas sin regla)
        else:
             resultado_final = _llamar_modulo_ml(hechos_activos_ids)

    # Devolver un diccionario con el diagnóstico y los IDs de los síntomas pasados
    return {
        "diagnostico": resultado_final,
        "sintomas_pasados_ids": hechos_activos_ids
    }