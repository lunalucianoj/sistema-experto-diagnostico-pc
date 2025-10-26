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

# --- Motor de Inferencia (sin cambios) ---
def _llamar_modulo_ml(hechos_activos_ids: List[str]) -> str:
     print(f"INFO: Reglas no concluyentes para {hechos_activos_ids}. Pasando a módulo ML (simulado).")
     return ("Diagnóstico: Las reglas no fueron suficientes. Un análisis más avanzado (ML) sugiere investigar posibles conflictos de software o drivers recientes. "
             "Considere proporcionar más detalles en la sección 'Otro Problema'. (Módulo ML simulado)")

def motor_de_inferencia(hechos_activos_ids: List[str]) -> str:
    set_hechos_activos = set(hechos_activos_ids)
    if not set_hechos_activos: return "Por favor, selecciona al menos un síntoma."
    diagnostico_encontrado = None
    max_condiciones_cumplidas = -1
    for regla in BASE_CONOCIMIENTO.reglas:
        condiciones_cumplidas = True
        num_condiciones = 0
        for cond in regla.condiciones:
            num_condiciones += 1
            if cond.startswith("NOT:"):
                cond_id = cond.replace("NOT:", "")
                if cond_id in set_hechos_activos:
                    condiciones_cumplidas = False; break
            else:
                if cond not in set_hechos_activos:
                    condiciones_cumplidas = False; break
        if condiciones_cumplidas and num_condiciones > max_condiciones_cumplidas:
            max_condiciones_cumplidas = num_condiciones
            diagnostico_encontrado = regla.diagnostico
    if diagnostico_encontrado: return diagnostico_encontrado
    if len(set_hechos_activos) == 1:
        sintoma_unico_id = list(set_hechos_activos)[0]
        if BASE_CONOCIMIENTO.diagnosticos_sintoma_unico and sintoma_unico_id in BASE_CONOCIMIENTO.diagnosticos_sintoma_unico:
             # Corrección: Asegurarse de que el diccionario existe antes de acceder
             return BASE_CONOCIMIENTO.diagnosticos_sintoma_unico[sintoma_unico_id]
    return _llamar_modulo_ml(hechos_activos_ids)