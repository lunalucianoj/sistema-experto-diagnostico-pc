import tkinter as tk
from tkinter import messagebox


def _realizar_diagnostico(sintomas_vars, motor):
    """ Usa el motor que recibe como parámetro para el diagnóstico. """
    SintomasPC = motor.SintomasPC
    sintomas = SintomasPC(
        pc_no_enciende=sintomas_vars["no_enciende"].get(),
        pantalla_sin_video=sintomas_vars["sin_video"].get(),
        sistema_operativo_lento=sintomas_vars["lento"].get(),
        ruidos_extranos_hdd=sintomas_vars["ruidos"].get(),
        periferico_no_funciona=sintomas_vars["periferico"].get(),
        hace_pitidos_al_arrancar=sintomas_vars["pitidos"].get(),
        mensajes_de_error_os=sintomas_vars["mensajes_error"].get()
    )
    diagnostico = motor.motor_de_inferencia(sintomas)
    messagebox.showinfo("Resultado del Diagnóstico", diagnostico)

def iniciar_aplicacion(motor_seleccionado):
    """ Crea y lanza la ventana, usando el motor que se le pasa como argumento. """
    ventana = tk.Tk()
    ventana.title("Sistema Experto de Diagnóstico de PC")
    # ... (El resto del código de la ventana es igual)
    frame_principal = tk.Frame(ventana, padx=20, pady=20)
    frame_principal.pack(expand=True, fill="both")
    etiqueta_titulo = tk.Label(frame_principal, text="Seleccione los síntomas:", font=("Helvetica", 16))
    etiqueta_titulo.pack(pady=10, anchor="w")
    sintomas_vars = {
        "no_enciende": tk.BooleanVar(), "sin_video": tk.BooleanVar(), "lento": tk.BooleanVar(),
        "ruidos": tk.BooleanVar(), "periferico": tk.BooleanVar(), "pitidos": tk.BooleanVar(),
        "mensajes_error": tk.BooleanVar(),
    }
    tk.Checkbutton(frame_principal, text="La PC no enciende para nada.", variable=sintomas_vars["no_enciende"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="La PC enciende pero la pantalla no muestra video.", variable=sintomas_vars["sin_video"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="El sistema operativo está muy lento.", variable=sintomas_vars["lento"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="El disco duro hace ruidos extraños (clics, zumbidos).", variable=sintomas_vars["ruidos"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="Un periférico (mouse, teclado, etc.) no funciona.", variable=sintomas_vars["periferico"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="La PC hace pitidos al intentar arrancar.", variable=sintomas_vars["pitidos"]).pack(anchor="w")
    tk.Checkbutton(frame_principal, text="Aparecen mensajes de error o 'pantallas azules'.", variable=sintomas_vars["mensajes_error"]).pack(anchor="w")

    # El botón ahora le pasa el motor seleccionado a la función de diagnóstico
    boton_diagnosticar = tk.Button(frame_principal, text="Diagnosticar", 
                                   command=lambda: _realizar_diagnostico(sintomas_vars, motor_seleccionado),
                                   font=("Helvetica", 12), bg="#007bff", fg="white")
    boton_diagnosticar.pack(pady=20)
    ventana.mainloop()