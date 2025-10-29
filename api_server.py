# Archivo: api_server.py (Versión con Categorías)

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import json
import os
from datetime import datetime

# Importamos las funciones necesarias del motor Y HECHOS_POR_ID
from motor.logica import (
    get_categorias,
    get_hechos_por_categoria,
    motor_de_inferencia,
    Hecho, # Clase Hecho para type hinting (buena práctica)
    HECHOS_POR_ID # Necesario para obtener las preguntas en /diagnostico
)

# --- Configuración de FastAPI y Plantillas ---
# Define la aplicación FastAPI con un título descriptivo.
app = FastAPI(title="Sistema Experto de Diagnóstico de PC v3.3")

# Configura Jinja2 para buscar plantillas en la carpeta 'templates'.
templates = Jinja2Templates(directory="templates")

# Monta la carpeta 'static' para servir archivos CSS, JS, etc., bajo la URL '/static'.
# Rutas de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
# Servir los logos que el usuario colocó en la carpeta 'imgs' en la raíz del proyecto
app.mount("/imgs", StaticFiles(directory="imgs"), name="imgs")

# --- Constantes y Configuración ---
HISTORIAL_DIAGNOSTICOS_FILE = "historial_diagnosticos.json"
PROBLEMAS_MANUALES_FILE = "problemas_manuales.json"
CONOCIMIENTO_USUARIO_FILE = "conocimiento_usuario.json"
NUMERO_SOPORTE = "+54 11 1234-5678"  # Número de contacto de soporte técnico

# --- Funciones Auxiliares para JSON ---

def cargar_json(archivo: str) -> list:
    """Carga datos desde un archivo JSON. Si no existe, retorna lista vacía."""
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"WARN: Error al leer {archivo}, retornando lista vacía.")
            return []
    return []

def guardar_json(archivo: str, datos: list):
    """Guarda datos en un archivo JSON."""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def generar_id_diagnostico() -> str:
    """Genera un ID único para diagnósticos basado en timestamp."""
    return f"diag_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

# --- Endpoints para la Interfaz Web Dinámica ---

@app.get("/", response_class=HTMLResponse)
async def mostrar_categorias(request: Request):
    """
    Endpoint Raíz (GET /): Muestra la página principal.
    Obtiene las categorías desde el motor y las pasa a la plantilla
    'seleccionar_categoria.html' para renderizar los botones.
    """
    categorias = get_categorias() # Llama a la función del motor
    print(f"DEBUG: Categorías obtenidas: {categorias}") # Mensaje de depuración
    return templates.TemplateResponse("seleccionar_categoria.html", {
        "request": request,
        "categorias": categorias
    })

@app.get("/sintomas/{categoria}", response_class=HTMLResponse)
async def mostrar_sintomas_por_categoria(request: Request, categoria: str):
    """
    Endpoint para mostrar síntomas (GET /sintomas/{categoria}):
    Obtiene los hechos (síntomas) para la 'categoria' especificada en la URL.
    Si la categoría es inválida o no tiene hechos, redirige a la página principal.
    Pasa la lista de hechos y el nombre de la categoría a la plantilla
    'seleccionar_sintomas.html' para renderizar los checkboxes.
    """
    print(f"DEBUG: Solicitando síntomas para la categoría: {categoria}") # Mensaje de depuración
    hechos = get_hechos_por_categoria(categoria)
    if not hechos:
        print(f"WARN: Categoría '{categoria}' no encontrada o sin hechos. Redirigiendo a /.") # Mensaje de advertencia
        return RedirectResponse(url="/", status_code=303) # Redirige si la categoría no es válida

    return templates.TemplateResponse("seleccionar_sintomas.html", {
        "request": request,
        "categoria": categoria.capitalize(), # Pone la primera letra en mayúscula para mostrar
        "hechos": hechos # Lista de objetos Hecho
    })

@app.post("/diagnostico", response_class=HTMLResponse)
async def diagnosticar_desde_web(request: Request, sintomas_seleccionados: List[str] = Form(None)):
    """
    Endpoint de Diagnóstico (POST /diagnostico):
    Recibe la lista de IDs de los síntomas seleccionados desde el formulario.
    Si no se seleccionó ninguno, inicializa la lista como vacía.
    Llama al 'motor_de_inferencia' con la lista de IDs.
    Obtiene las preguntas correspondientes a los IDs seleccionados para mostrarlas.
    GUARDA automáticamente el diagnóstico en historial_diagnosticos.json.
    Pasa el diagnóstico y las preguntas a la plantilla 'resultado_diagnostico.html'.
    """
    # Maneja el caso donde no se selecciona ningún síntoma
    if not sintomas_seleccionados:
        sintomas_seleccionados = []
        print("DEBUG: No se seleccionaron síntomas.") # Mensaje de depuración
    else:
         print(f"DEBUG: Síntomas seleccionados recibidos: {sintomas_seleccionados}") # Mensaje de depuración

    # Llama al motor de inferencia (que ahora devuelve un diccionario)
    resultado_motor = motor_de_inferencia(sintomas_seleccionados)
    print(f"DEBUG: Resultado del motor: {resultado_motor}") # Mensaje de depuración

    # Obtiene las preguntas completas para los IDs seleccionados (usa el HECHOS_POR_ID importado)
    sintomas_preguntas = [HECHOS_POR_ID[id_hecho].pregunta
                          for id_hecho in sintomas_seleccionados
                          if id_hecho in HECHOS_POR_ID]

    # --- GUARDAR DIAGNÓSTICO EN HISTORIAL ---
    id_diagnostico = generar_id_diagnostico()
    registro_diagnostico = {
        "id": id_diagnostico,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sintomas_ids": sintomas_seleccionados,
        "sintomas_texto": sintomas_preguntas,
        "diagnostico": resultado_motor["diagnostico"],
        "feedback": None,  # Se actualizará cuando el usuario dé feedback
        "timestamp": datetime.now().timestamp()
    }
    
    historial = cargar_json(HISTORIAL_DIAGNOSTICOS_FILE)
    historial.append(registro_diagnostico)
    guardar_json(HISTORIAL_DIAGNOSTICOS_FILE, historial)
    print(f"DEBUG: Diagnóstico guardado con ID: {id_diagnostico}")

    # Renderiza la plantilla de resultados
    return templates.TemplateResponse("resultado_diagnostico.html", {
        "request": request,
        "diagnostico": resultado_motor["diagnostico"], # Extrae el texto del diagnóstico
        "sintomas_mostrados": sintomas_preguntas, # Pasa la lista de preguntas
        "id_diagnostico": id_diagnostico,  # Pasa el ID para el feedback
        "numero_soporte": NUMERO_SOPORTE  # Número de soporte técnico
    })

# --- Endpoints para "Detallar Otro Problema" ---

@app.get("/otro-problema", response_class=HTMLResponse)
async def mostrar_formulario_otro_problema(request: Request):
    """
    Endpoint GET /otro-problema:
    Muestra el formulario para que el usuario describa un problema no listado.
    Obtiene las categorías disponibles para el selector desplegable.
    """
    categorias = get_categorias()
    return templates.TemplateResponse("detallar_problema.html", {
        "request": request,
        "categorias": categorias,
        "mensaje_exito": None # Para no mostrar mensaje de éxito al cargar
    })

@app.post("/registrar-otro-problema", response_class=HTMLResponse)
async def registrar_otro_problema(
    request: Request, 
    categoria_otro: str = Form(...), 
    descripcion: str = Form(...),
    urgente: bool = Form(False)
):
    """
    Endpoint POST /registrar-otro-problema:
    Recibe la categoría, la descripción y si es urgente.
    GUARDA el problema en problemas_manuales.json.
    Vuelve a mostrar el formulario con un mensaje de éxito.
    Si es urgente, muestra el número de soporte técnico.
    """
    # Crear registro del problema
    registro_problema = {
        "id": f"prob_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "categoria": categoria_otro,
        "descripcion": descripcion,
        "urgente": urgente,
        "timestamp": datetime.now().timestamp()
    }
    
    # Guardar en archivo JSON
    problemas = cargar_json(PROBLEMAS_MANUALES_FILE)
    problemas.append(registro_problema)
    guardar_json(PROBLEMAS_MANUALES_FILE, problemas)
    
    # Imprime la información recibida en la terminal del servidor
    print("\n--- NUEVO PROBLEMA DETALLADO POR USUARIO ---")
    print(f"Categoría Seleccionada: {categoria_otro}")
    print(f"Descripción del Usuario: {descripcion}")
    print(f"Urgente: {'SÍ' if urgente else 'NO'}")
    print("---------------------------------------------\n")

    # Re-renderiza la misma página mostrando un mensaje de confirmación
    categorias = get_categorias() # Necesario para el selector
    return templates.TemplateResponse("detallar_problema.html", {
        "request": request,
        "categorias": categorias,
        "mensaje_exito": "¡Gracias! Hemos registrado tu descripción.",
        "es_urgente": urgente,
        "numero_soporte": NUMERO_SOPORTE if urgente else None
    })

# --- Endpoint para Feedback de Diagnóstico ---

@app.post("/feedback")
async def guardar_feedback(id_diagnostico: str = Form(...), feedback: str = Form(...)):
    """
    Endpoint POST /feedback:
    Recibe el ID del diagnóstico y el feedback ('si' o 'no').
    Actualiza el registro en historial_diagnosticos.json.
    Retorna respuesta JSON para manejo desde el frontend.
    """
    historial = cargar_json(HISTORIAL_DIAGNOSTICOS_FILE)
    
    # Buscar el diagnóstico por ID y actualizar feedback
    diagnostico_encontrado = False
    for registro in historial:
        if registro["id"] == id_diagnostico:
            registro["feedback"] = feedback
            registro["fecha_feedback"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            diagnostico_encontrado = True
            break
    
    if diagnostico_encontrado:
        guardar_json(HISTORIAL_DIAGNOSTICOS_FILE, historial)
        print(f"DEBUG: Feedback '{feedback}' guardado para diagnóstico {id_diagnostico}")
        return JSONResponse(content={"status": "success", "feedback": feedback, "numero_soporte": NUMERO_SOPORTE})
    else:
        print(f"WARN: Diagnóstico {id_diagnostico} no encontrado para feedback")
        return JSONResponse(content={"status": "error", "message": "Diagnóstico no encontrado"}, status_code=404)

# --- Endpoints para Historiales ---

@app.get("/historial-diagnosticos", response_class=HTMLResponse)
async def ver_historial_diagnosticos(request: Request):
    """
    Endpoint GET /historial-diagnosticos:
    Muestra todos los diagnósticos realizados, ordenados por fecha (más reciente primero).
    """
    historial = cargar_json(HISTORIAL_DIAGNOSTICOS_FILE)
    # Ordenar por timestamp descendente (más reciente primero)
    historial_ordenado = sorted(historial, key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return templates.TemplateResponse("historial_diagnosticos.html", {
        "request": request,
        "diagnosticos": historial_ordenado
    })

@app.get("/historial-problemas", response_class=HTMLResponse)
async def ver_historial_problemas(request: Request):
    """
    Endpoint GET /historial-problemas:
    Muestra todos los problemas reportados manualmente, ordenados por fecha (más reciente primero).
    """
    problemas = cargar_json(PROBLEMAS_MANUALES_FILE)
    # Ordenar por timestamp descendente (más reciente primero)
    problemas_ordenados = sorted(problemas, key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return templates.TemplateResponse("historial_problemas.html", {
        "request": request,
        "problemas": problemas_ordenados,
        "numero_soporte": NUMERO_SOPORTE
    })

# --- Endpoint para Ingreso de Nuevos Datos por Usuario ---

@app.get("/ingresar-datos", response_class=HTMLResponse)
async def mostrar_formulario_ingresar_datos(request: Request):
    """
    Endpoint GET /ingresar-datos:
    Muestra el formulario para que el usuario ingrese nuevos datos al sistema:
    - Categoría (Hardware/Software)
    - Descripción del síntoma
    - Diagnóstico/Solución
    """
    categorias = get_categorias()
    # Cargar datos de usuario previos para mostrarlos
    datos_usuario = cargar_json(CONOCIMIENTO_USUARIO_FILE)
    
    return templates.TemplateResponse("ingresar_datos.html", {
        "request": request,
        "categorias": categorias,
        "datos_guardados": datos_usuario,
        "mensaje_exito": None
    })

@app.post("/guardar-nuevo-dato")
async def guardar_nuevo_dato(
    request: Request,
    categoria: str = Form(...),
    sintoma: str = Form(...),
    diagnostico: str = Form(...)
):
    """
    Endpoint POST /guardar-nuevo-dato:
    Recibe categoría, síntoma y diagnóstico ingresados por el usuario.
    Los guarda en conocimiento_usuario.json de forma TEMPORAL.
    """
    # Crear nuevo registro
    nuevo_dato = {
        "id": f"user_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "categoria": categoria,
        "sintoma": sintoma,
        "diagnostico": diagnostico,
        "temporal": True,  # Marca que es ingresado por usuario
        "timestamp": datetime.now().timestamp()
    }
    
    # Guardar en archivo JSON
    datos_usuario = cargar_json(CONOCIMIENTO_USUARIO_FILE)
    datos_usuario.append(nuevo_dato)
    guardar_json(CONOCIMIENTO_USUARIO_FILE, datos_usuario)
    
    print(f"\n--- NUEVO DATO INGRESADO POR USUARIO ---")
    print(f"Categoría: {categoria}")
    print(f"Síntoma: {sintoma}")
    print(f"Diagnóstico: {diagnostico}")
    print("------------------------------------------\n")
    
    # Recargar página con mensaje de éxito
    categorias = get_categorias()
    datos_usuario_actualizados = cargar_json(CONOCIMIENTO_USUARIO_FILE)
    
    return templates.TemplateResponse("ingresar_datos.html", {
        "request": request,
        "categorias": categorias,
        "datos_guardados": datos_usuario_actualizados,
        "mensaje_exito": "¡Dato guardado exitosamente! Ahora aparece en el sistema de forma temporal."
    })

# --- Función de Inicio del Servidor (llamada desde main.py) ---
def iniciar_api(): # Eliminado el parámetro 'motor_seleccionado' ya que no se usa aquí
    """ Lanza el servidor web FastAPI/Uvicorn. """
    print("Iniciando servidor FastAPI en http://127.0.0.1:8000")
    print("Abre tu navegador en esa dirección para usar el Sistema Experto.")
    print("Presiona CTRL+C para detener el servidor.")
    # Ejecuta el servidor Uvicorn, apuntando a la instancia 'app' de FastAPI en este archivo.
    uvicorn.run(app, host="127.0.0.1", port=8000)