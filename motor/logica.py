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
    """ Placeholder MEJORADO v2 para la integración del módulo ML. Considera combinaciones. """
    print(f"INFO: Reglas no concluyentes para {hechos_activos_ids}. Pasando a módulo ML (simulado).")
    
    set_hechos_activos = set(hechos_activos_ids) # Usamos un set para búsquedas rápidas
    
    # --- Lógica Simulada Mejorada: Priorizar Combinaciones ---
    
    sugerencia_ml = "investigar posibles conflictos de software generales o drivers recientes." # Sugerencia por defecto aún más genérica
    
    # Combinación: Lento + Problemas de Red (WiFi o Internet)
    if "sistema_lento" in set_hechos_activos and ("no_conecta_wifi" in set_hechos_activos or "wifi_conectado_sin_internet" in set_hechos_activos):
        sugerencia_ml = "revisar si hay software consumiendo mucho ancho de banda (actualizaciones, P2P), buscar malware que afecte la red, o considerar problemas con el router/proveedor que impacten el rendimiento general."
    
    # Combinación: Lento + Cierres/Errores (Software Inestable)
    elif "sistema_lento" in set_hechos_activos and ("programas_cierran" in set_hechos_activos or "mensajes_error_frecuentes" in set_hechos_activos or "pantalla_azul" in set_hechos_activos):
        sugerencia_ml = "buscar actualizaciones del sistema operativo y de las aplicaciones que fallan, verificar la integridad de los archivos del sistema (ejecutar 'sfc /scannow' en CMD como admin), o considerar problemas de RAM."
        
    # Combinación: Problemas de Video + Lento/Cierres (GPU/Driver Inestable)
    elif "imagen_congelada_o_artefactos" in set_hechos_activos and ("sistema_lento" in set_hechos_activos or "programas_cierran" in set_hechos_activos):
        sugerencia_ml = "realizar una instalación limpia de los drivers de la tarjeta gráfica (usando DDU si es necesario), monitorizar las temperaturas de la GPU, o verificar si la fuente de poder es suficiente."
        
    # --- Lógica basada en palabras clave individuales (si no aplican combinaciones) ---
        
    # Solo Lento (sin otros síntomas clave combinados arriba)
    elif "sistema_lento" in set_hechos_activos and not {"ruidos_hdd", "sobrecalentamiento", "programas_cierran", "publicidad_excesiva", "no_conecta_wifi", "wifi_conectado_sin_internet", "pantalla_azul", "mensajes_error_frecuentes", "imagen_congelada_o_artefactos"} & set_hechos_activos:
        sugerencia_ml = "optimizar el sistema operativo (programas de inicio, espacio en disco, desfragmentar HDD), buscar malware o verificar el estado del disco duro/SSD."

    # Solo Problemas WiFi/Internet (sin lentitud combinada arriba)
    elif ("no_conecta_wifi" in set_hechos_activos or "wifi_conectado_sin_internet" in set_hechos_activos) and not {"sistema_lento"} & set_hechos_activos:
        sugerencia_ml = "revisar la configuración de red (IP/DNS), reiniciar router/módem, actualizar drivers de red o contactar al proveedor de internet."
        
    # Solo Problemas de Video (sin lentitud/cierres combinados arriba)
    elif "imagen_congelada_o_artefactos" in set_hechos_activos and not {"sistema_lento", "programas_cierran"} & set_hechos_activos:
        sugerencia_ml = "actualizar los drivers de la tarjeta gráfica, verificar las conexiones de video o monitorizar temperaturas de la GPU."

    # --- Mensaje Final ---
    return (f"Diagnóstico: Las reglas exactas no coinciden. Un análisis avanzado (ML) sugiere {sugerencia_ml} "
            "Considere proporcionar más detalles en la sección 'Otro Problema'. (Módulo ML simulado)")


# Reemplaza la función motor_de_inferencia en motor/logica.py con esto:

def motor_de_inferencia(hechos_activos_ids: List[str]) -> Dict[str, Any]:
    """
    Motor de inferencia v3.3: Prioriza regla específica y verifica coincidencia significativa.
    Devuelve un diccionario con diagnóstico y síntomas.
    """
    set_hechos_activos = set(hechos_activos_ids)
    resultado_final: str = "Diagnóstico no determinado"
    
    if not set_hechos_activos:
         resultado_final = "Por favor, selecciona al menos un síntoma."
    else:
        mejor_regla_encontrada = None
        max_condiciones_positivas_coincidentes = -1
        max_especificidad_regla = -1

        # 1. Buscar la regla que mejor se ajuste y sea más específica
        for regla in BASE_CONOCIMIENTO.reglas:
            condiciones_cumplidas = True
            condiciones_positivas_coincidentes_actual = 0
            especificidad_actual = len(regla.condiciones)
            
            for cond in regla.condiciones:
                cond_base = cond.replace("NOT:", "")
                if cond.startswith("NOT:"):
                    if cond_base in set_hechos_activos:
                        condiciones_cumplidas = False; break
                else:
                    if cond not in set_hechos_activos:
                        condiciones_cumplidas = False; break
                    else:
                         condiciones_positivas_coincidentes_actual += 1
            
            if condiciones_cumplidas:
                # Priorizar la regla que usa MÁS de los síntomas activos actuales
                if condiciones_positivas_coincidentes_actual > max_condiciones_positivas_coincidentes:
                    max_condiciones_positivas_coincidentes = condiciones_positivas_coincidentes_actual
                    max_especificidad_regla = especificidad_actual
                    mejor_regla_encontrada = regla
                # Desempate: Si usan la misma cantidad de síntomas activos, preferir la más específica (más condiciones en total)
                elif condiciones_positivas_coincidentes_actual == max_condiciones_positivas_coincidentes and especificidad_actual > max_especificidad_regla:
                    max_especificidad_regla = especificidad_actual
                    mejor_regla_encontrada = regla

        # --- LÓGICA DE DECISIÓN CORREGIDA ---
        # 2. Verificar si la mejor regla encontrada es suficientemente buena
        # Consideramos 'buena' si usa casi todos los síntomas activos.
        # Por ejemplo, si hay 2 síntomas, la regla debe usar al menos 1 o 2. Si hay 3, al menos 2.
        # Ajusta este umbral si es necesario.

        if mejor_regla_encontrada and max_condiciones_positivas_coincidentes == len(set_hechos_activos - {c.replace("NOT:","") for c in mejor_regla_encontrada.condiciones if c.startswith("NOT:")}):

            resultado_final = mejor_regla_encontrada.diagnostico
            
        # 3. Si no hay regla buena, y es un solo síntoma con sugerencia
        elif len(set_hechos_activos) == 1:
            sintoma_unico_id = list(set_hechos_activos)[0]
            if BASE_CONOCIMIENTO.diagnosticos_sintoma_unico and sintoma_unico_id in BASE_CONOCIMIENTO.diagnosticos_sintoma_unico:
                resultado_final = BASE_CONOCIMIENTO.diagnosticos_sintoma_unico[sintoma_unico_id]
            else: # Síntoma único sin sugerencia -> ML
                 resultado_final = _llamar_modulo_ml(hechos_activos_ids)
        # 4. Si no aplican los anteriores (múltiples síntomas sin regla suficientemente buena) -> ML
        else:
             resultado_final = _llamar_modulo_ml(hechos_activos_ids)

    # Devolver diccionario
    return {
        "diagnostico": resultado_final,
        "sintomas_pasados_ids": hechos_activos_ids
    }

# La función _llamar_modulo_ml se mantiene igual que en la versión anterior.
# Asegúrate de tenerla definida en el mismo archivo.