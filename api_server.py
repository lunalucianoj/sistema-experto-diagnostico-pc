# Archivo: api_server.py (Versión con Categorías)

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

# Importamos las funciones necesarias del motor
from motor.logica import (
    get_categorias, 
    get_hechos_por_categoria, 
    motor_de_inferencia,
    Hecho # Importamos la clase Hecho para type hinting
)

# Configuración de FastAPI y plantillas
app = FastAPI(title="Sistema Experto de Diagnóstico de PC v2")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoints para la Interfaz Web Dinámica ---

@app.get("/", response_class=HTMLResponse)
async def mostrar_categorias(request: Request):
    """ Muestra la página principal con botones para cada categoría. """
    categorias = get_categorias()
    return templates.TemplateResponse("seleccionar_categoria.html", {
        "request": request, 
        "categorias": categorias
    })

@app.get("/sintomas/{categoria}", response_class=HTMLResponse)
async def mostrar_sintomas_por_categoria(request: Request, categoria: str):
    """ Muestra los síntomas correspondientes a la categoría seleccionada. """
    hechos = get_hechos_por_categoria(categoria)
    if not hechos: # Si la categoría no existe o no tiene hechos
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse("seleccionar_sintomas.html", {
        "request": request, 
        "categoria": categoria.capitalize(), 
        "hechos": hechos
    })

# Reemplaza el endpoint existente en api_server.py
@app.post("/diagnostico", response_class=HTMLResponse)
async def diagnosticar_desde_web(request: Request, sintomas_seleccionados: List[str] = Form(...)):
    """ Recibe la lista de IDs de síntomas, obtiene diagnóstico y síntomas, y muestra el resultado. """
    
    # Llamamos al motor, que ahora devuelve un diccionario
    resultado_motor = motor_de_inferencia(sintomas_seleccionados)
    
    # Obtenemos las preguntas correspondientes a los IDs seleccionados
    # Usamos HECHOS_POR_ID que ya está definido globalmente en logica.py
    # Necesitamos importarlo en api_server.py
    from motor.logica import HECHOS_POR_ID # Añadir esta importación al principio de api_server.py
    
    sintomas_preguntas = [HECHOS_POR_ID[id_hecho].pregunta for id_hecho in sintomas_seleccionados if id_hecho in HECHOS_POR_ID]

    return templates.TemplateResponse("resultado_diagnostico.html", {
        "request": request,
        "diagnostico": resultado_motor["diagnostico"], # Extraemos el diagnóstico
        "sintomas_mostrados": sintomas_preguntas # Pasamos las preguntas
    })

# --- Endpoint API (opcional, si quieres mantenerlo) ---
# Puedes adaptar el endpoint /api/diagnostico si lo necesitas,
# asegurándote de que Pydantic valide una lista de strings ahora.

@app.get("/otro-problema", response_class=HTMLResponse)
async def mostrar_formulario_otro_problema(request: Request):
    """ Muestra el formulario para describir un problema no listado. """
    categorias = get_categorias() # Reutilizamos la función del motor
    return templates.TemplateResponse("detallar_problema.html", {
        "request": request,
        "categorias": categorias,
        "mensaje_exito": None
    })

@app.post("/registrar-otro-problema", response_class=HTMLResponse)
async def registrar_otro_problema(request: Request, categoria_otro: str = Form(...), descripcion: str = Form(...)):
    """ Recibe la descripción del problema y la 'registra' (por ahora, imprime). """
    print("\n--- NUEVO PROBLEMA DETALLADO POR USUARIO ---")
    print(f"Categoría: {categoria_otro}")
    print(f"Descripción: {descripcion}")
    print("---------------------------------------------\n")
    
    # Podríamos guardar esto en un archivo, base de datos, etc.
    
    categorias = get_categorias() # Necesario para volver a renderizar la plantilla
    return templates.TemplateResponse("detallar_problema.html", {
        "request": request,
        "categorias": categorias,
        "mensaje_exito": "¡Gracias! Hemos registrado tu descripción."
    })


# --- Función para Iniciar (se usa desde main.py) ---
def iniciar_api(motor_seleccionado=None): # El parámetro ya no es necesario aquí
    """ Lanza el servidor FastAPI. """
    print("Iniciando servidor API en http://127.0.0.1:8000")
    print("Abre tu navegador en esa dirección.")
    uvicorn.run(app, host="127.0.0.1", port=8000)