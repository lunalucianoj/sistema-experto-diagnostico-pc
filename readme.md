# 🖥️ Sistema Experto para Diagnóstico de Fallas en PC

Este proyecto es un sistema experto diseñado para diagnosticar problemas de hardware y software en computadoras personales. La aplicación demuestra conceptos clave de la inteligencia artificial, como bases de conocimiento y motores de inferencia, a través de una arquitectura modular y flexible.

## ✨ Características Principales

* **Doble Interfaz de Usuario**: El sistema puede ser ejecutado de dos maneras:
    1.  **Aplicación de Escritorio (GUI)**: Una interfaz gráfica amigable creada con Tkinter para un uso local y directo.
    2.  **Servidor Web (API + Web)**: Un servidor FastAPI que expone tanto una API (para ser consumida por otros programas) como una interfaz web interactiva en HTML.

* **Motores de Inferencia Intercambiables**: El núcleo del sistema puede operar con dos lógicas de diagnóstico distintas:
    1.  **Motor de Reglas Estrictas**: Un motor clásico `SI... ENTONCES...` que cumple con la consigna original del proyecto.
    2.  **Motor de Puntuación (Pesos)**: Un motor más avanzado que asigna pesos a los síntomas para calcular el diagnóstico más probable, permitiendo manejar la incertidumbre.

* **Arquitectura Modular**: El código está organizado separando la lógica del "motor" de las "interfaces", lo que facilita su mantenimiento y escalabilidad.

## 📂 Estructura del Proyecto

El proyecto está organizado en paquetes para una clara separación de responsabilidades:

```
proyecto_inferencia/
|
|-- gui/
|   |-- app_gui.py          # Lógica de la interfaz gráfica con Tkinter.
|   `-- __init__.py
|
|-- motor/
|   |-- logica_reglas.py    # Motor de inferencia simple (SI/ENTONCES).
|   |-- logica_pesos.py     # Motor de inferencia avanzado (Puntuación).
|   `-- __init__.py
|
|-- templates/
|   `-- index.html          # Interfaz web para el servidor FastAPI.
|
|-- api_server.py           # Código del servidor web con FastAPI.
|-- main.py                 # Punto de entrada principal para lanzar la aplicación.
|-- requirements.txt        # Dependencias del proyecto.
`-- README.md               # Esta documentación.
```

## 🧠 ¿Cómo Funciona el Sistema Experto?

El sistema se basa en la separación de la **Base de Conocimiento** (la información sobre los problemas) y el **Motor de Inferencia** (el "cerebro" que usa esa información). Este proyecto implementa dos tipos de motores:

### 1. Motor de Reglas (Simple)

* **Archivo**: `motor/logica_reglas.py`
* **Concepto**: Este motor utiliza una serie de reglas `SI... ENTONCES...` estrictas. Para que un diagnóstico sea concluyente, todos los síntomas (condiciones) de una regla deben cumplirse a la perfección.
* **Ejemplo**: `SI 'la PC no enciende' Y 'hace pitidos', ENTONCES el diagnóstico es 'Falla de RAM/Video'`.
* **Fortaleza**: Es muy transparente y fácil de entender. Cada diagnóstico se puede rastrear a una regla específica.
* **Debilidad**: Es rígido. Si falta un solo síntoma para cumplir una regla, no puede llegar a una conclusión, incluso si la evidencia es fuerte.

### 2. Motor de Puntuación (Avanzado)

* **Archivo**: `motor/logica_pesos.py`
* **Concepto**: Este motor trata cada síntoma como una "pista" a la que se le asigna un "peso" o puntuación. Suma los puntos de todos los síntomas seleccionados para cada diagnóstico posible y presenta el que tenga la puntuación más alta.
* **Ejemplo**: El síntoma `'ruidos extraños en HDD'` aporta **25 puntos** al diagnóstico de "Falla de Disco Duro", mientras que `'sistema lento'` solo aporta **8 puntos**.
* **Fortaleza**: Maneja la incertidumbre y la información incompleta. Puede ofrecer el diagnóstico **más probable** incluso con un solo síntoma.
* **Debilidad**: La lógica es menos directa, ya que se basa en la suma de pesos y un umbral de confianza.

| Característica | Motor de Reglas (Simple) | Motor de Puntuación (Avanzado) |
| :--- | :--- | :--- |
| **Precisión** | Alta, pero solo en casos perfectos. | Flexible, encuentra la mejor opción posible. |
| **Incertidumbre** | No la maneja. | Es su principal fortaleza. |
| **Transparencia** | Muy alta (fácil de explicar). | Moderada (basada en cálculos). |
| **Complejidad** | Baja. | Media. |

## 🚀 Instalación y Uso

### Instalación

1.  Asegúrate de tener Python 3 instalado.
2.  Clona o descarga este repositorio.
3.  Abre una terminal en la carpeta del proyecto.
4.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

### Uso

1.  Para ejecutar la aplicación, corre el siguiente comando en la terminal:
    ```bash
    python main.py
    ```
2.  El programa te pedirá que elijas qué **motor de inferencia** quieres usar (el simple o el avanzado).
3.  Luego, te preguntará cómo quieres ejecutar el sistema:
    * **Opción 1**: Lanza la **aplicación de escritorio**. Se abrirá una ventana donde podrás seleccionar los síntomas y obtener un diagnóstico.
    * **Opción 2**: Lanza el **servidor web**. Para usarlo, abre tu navegador y ve a `http://127.0.0.1:8000`. Verás una página web para realizar el diagnóstico.