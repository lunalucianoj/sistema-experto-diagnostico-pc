# Archivo: api_server.py (Versión con Categorías)

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

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
app.mount("/static", StaticFiles(directory="static"), name="static")

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

    # Renderiza la plantilla de resultados
    return templates.TemplateResponse("resultado_diagnostico.html", {
        "request": request,
        "diagnostico": resultado_motor["diagnostico"], # Extrae el texto del diagnóstico
        "sintomas_mostrados": sintomas_preguntas # Pasa la lista de preguntas
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
async def registrar_otro_problema(request: Request, categoria_otro: str = Form(...), descripcion: str = Form(...)):
    """
    Endpoint POST /registrar-otro-problema:
    Recibe la categoría y la descripción del problema detallado por el usuario.
    Actualmente, solo imprime la información en la consola.
    (Futura mejora: guardar en archivo/base de datos).
    Vuelve a mostrar el formulario con un mensaje de éxito.
    """
    # Imprime la información recibida en la terminal del servidor
    print("\n--- NUEVO PROBLEMA DETALLADO POR USUARIO ---")
    print(f"Categoría Seleccionada: {categoria_otro}")
    print(f"Descripción del Usuario: {descripcion}")
    print("---------------------------------------------\n")

    # Re-renderiza la misma página mostrando un mensaje de confirmación
    categorias = get_categorias() # Necesario para el selector
    return templates.TemplateResponse("detallar_problema.html", {
        "request": request,
        "categorias": categorias,
        "mensaje_exito": "¡Gracias! Hemos registrado tu descripción."
    })

# --- Función de Inicio del Servidor (llamada desde main.py) ---
def iniciar_api(): # Eliminado el parámetro 'motor_seleccionado' ya que no se usa aquí
    """ Lanza el servidor web FastAPI/Uvicorn. """
    print("Iniciando servidor FastAPI en http://127.0.0.1:8000")
    print("Abre tu navegador en esa dirección para usar el Sistema Experto.")
    print("Presiona CTRL+C para detener el servidor.")
    # Ejecuta el servidor Uvicorn, apuntando a la instancia 'app' de FastAPI en este archivo.
    uvicorn.run(app, host="127.0.0.1", port=8000)