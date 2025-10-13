import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

def crear_app(motor):
    """ Crea la aplicación FastAPI usando el motor especificado. """
    app = FastAPI(title="Sistema Experto de Diagnóstico de PC")
    templates = Jinja2Templates(directory="templates")
    SintomasPC = motor.SintomasPC # Obtenemos el modelo del motor

    @app.get("/", response_class=HTMLResponse)
    async def mostrar_formulario_web(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.post("/diagnostico-web", response_class=HTMLResponse)
    async def diagnosticar_desde_web(request: Request, pc_no_enciende: bool = Form(False),
                                     pantalla_sin_video: bool = Form(False), sistema_operativo_lento: bool = Form(False),
                                     ruidos_extranos_hdd: bool = Form(False), periferico_no_funciona: bool = Form(False),
                                     hace_pitidos_al_arrancar: bool = Form(False), mensajes_de_error_os: bool = Form(False)):
        sintomas = SintomasPC(
            pc_no_enciende=pc_no_enciende, pantalla_sin_video=pantalla_sin_video,
            sistema_operativo_lento=sistema_operativo_lento, ruidos_extranos_hdd=ruidos_extranos_hdd,
            periferico_no_funciona=periferico_no_funciona, hace_pitidos_al_arrancar=hace_pitidos_al_arrancar,
            mensajes_de_error_os=mensajes_de_error_os
        )
        diagnostico_resultado = motor.motor_de_inferencia(sintomas)
        return templates.TemplateResponse("index.html", {"request": request, "diagnostico": diagnostico_resultado})

    @app.post("/api/diagnostico")
    def diagnosticar_pc_api(sintomas: SintomasPC):
        diagnostico_resultado = motor.motor_de_inferencia(sintomas)
        return {"diagnostico": diagnostico_resultado}
        
    return app

def iniciar_api(motor_seleccionado):
    """ Lanza el servidor FastAPI usando la app creada con el motor correcto. """
    app = crear_app(motor_seleccionado)
    print("Iniciando servidor API en http://127.0.0.1:8000")
    print("Abre tu navegador en esa dirección para ver la interfaz web.")
    uvicorn.run(app, host="127.0.0.1", port=8000)