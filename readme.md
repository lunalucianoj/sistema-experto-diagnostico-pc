# 🖥️ Sistema Experto para Diagnóstico de Fallas en PC

Este proyecto es un sistema experto diseñado para diagnosticar problemas de hardware y software en computadoras personales. La aplicación demuestra conceptos clave de la inteligencia artificial, como bases de conocimiento y motores de inferencia, a través de una arquitectura modular y flexible.

## ✨ Características Principales

* **Interfaz Web Interactiva**: Servidor FastAPI con interfaz HTML moderna y responsive que incluye:
    - Diagnóstico guiado por categorías (Hardware/Software)
    - Sistema de feedback para evaluar la efectividad de los diagnósticos
    - Historial completo de diagnósticos realizados
    - Registro de problemas manuales con sistema de urgencias
    - Módulo de ingreso de datos por usuarios (conocimiento colaborativo)

* **Motor de Inferencia Avanzado**: Sistema basado en reglas `SI... ENTONCES...` que incluye:
    - Evaluación de reglas con condiciones positivas y negativas (NOT:)
    - Priorización por especificidad y coincidencia de síntomas
    - Integración dinámica de datos aportados por usuarios
    - Fallback a módulo ML simulado para casos no cubiertos por reglas

* **Sistema de Gestión de Conocimiento**:
    - **Base de conocimiento estática**: Reglas predefinidas en `base_conocimiento.json`
    - **Base de conocimiento dinámica**: Usuarios pueden aportar nuevos síntomas y diagnósticos
    - Marcado de datos temporales para revisión
    - Persistencia en archivos JSON para fácil auditoría

* **Funcionalidades de Soporte**:
    - Sistema de feedback ("Sí sirvió" / "No sirvió") con número de contacto técnico
    - Marcado de reportes urgentes con contacto de soporte inmediato
    - Historial completo de diagnósticos con estado de feedback
    - Historial de problemas reportados manualmente

* **Arquitectura Modular**: El código está organizado separando la lógica del "motor" de las "interfaces", lo que facilita su mantenimiento y escalabilidad.

## 📂 Estructura del Proyecto

El proyecto está organizado en paquetes para una clara separación de responsabilidades:

```
proyecto_inferencia/
|
|-- motor/
|   |-- logica.py           # Motor de inferencia con integración de datos de usuario
|   `-- __init__.py
|
|-- templates/
|   |-- seleccionar_categoria.html        # Página principal con menú de navegación
|   |-- seleccionar_sintomas.html         # Selección de síntomas por categoría
|   |-- resultado_diagnostico.html        # Resultado con sistema de feedback
|   |-- detallar_problema.html            # Reporte manual con flag de urgencia
|   |-- historial_diagnosticos.html       # Historial de diagnósticos realizados
|   |-- historial_problemas.html          # Historial de problemas manuales
|   `-- ingresar_datos.html               # Módulo de ingreso de nuevos datos
|
|-- static/
|   `-- styles.css                        # Estilos con paleta del logo (azul/celeste)
|
|-- api_server.py           # Servidor FastAPI con 9 endpoints
|-- main.py                 # Lanza el servidor web
|-- base_conocimiento.json  # Base de reglas predefinidas
|-- historial_diagnosticos.json  # Almacén de diagnósticos con feedback
|-- problemas_manuales.json      # Almacén de reportes manuales
|-- conocimiento_usuario.json    # Datos aportados por usuarios (temporal)
|-- requirements.txt        # Dependencias web
`-- README.md               # Documentación
```

## 🧠 ¿Cómo Funciona el Sistema Experto?

El sistema se basa en la separación de la **Base de Conocimiento** (la información sobre los problemas) y el **Motor de Inferencia** (el "cerebro" que usa esa información).

### Motor de Inferencia con Reglas SI-ENTONCES

* **Archivo**: `motor/logica.py`
* **Concepto**: Utiliza reglas `SI... ENTONCES...` con evaluación de condiciones positivas y negativas (NOT:).
* **Ejemplo**: `SI 'sistema_lento' Y 'publicidad_excesiva' Y NOT:'no_conecta_wifi', ENTONCES el diagnóstico es 'Malware o Adware instalado'`.
* **Fortaleza**: 
  - Sistema transparente y explicable
  - Prioriza reglas por especificidad y coincidencia de síntomas
  - Integra dinámicamente datos aportados por usuarios
  - Fallback a módulo ML simulado cuando no hay coincidencias exactas
* **Características avanzadas**:
  - Evaluación de condiciones negadas (NOT:)
  - Selección de mejor regla por coincidencia y especificidad
  - Soporte para diagnósticos de síntoma único
  - Integración de conocimiento colaborativo temporal

## 🎯 Funcionalidades del Sistema

### 1. Diagnóstico Guiado
- Selección por categoría (Hardware/Software)
- Presentación organizada de síntomas
- Evaluación inteligente con motor de inferencia
- Resultados detallados con síntomas considerados

### 2. Sistema de Feedback
- Botones "Sí sirvió" / "No sirvió" en cada diagnóstico
- Almacenamiento de valoraciones en historial
- Muestra número de soporte técnico si el diagnóstico no fue útil
- Tracking completo de efectividad del sistema

### 3. Historial de Diagnósticos
- Registro automático de todos los diagnósticos realizados
- Visualización con fecha y hora
- Estado de feedback con iconos (✅ Sirvió / ❌ No sirvió / ⏳ Sin feedback)
- Acceso a síntomas y diagnósticos pasados

### 4. Reportes Manuales
- Formulario para describir problemas no cubiertos por el diagnóstico guiado
- Sistema de marcado de urgencia con checkbox
- Almacenamiento persistente en JSON
- Visualización de número de soporte para casos urgentes

### 5. Historial de Problemas Manuales
- Lista completa de problemas reportados
- Indicadores visuales de urgencia (⚠️ URGENTE)
- Badges de categorización (Hardware/Software)
- Información de contacto de soporte para casos urgentes

### 6. Ingreso de Datos por Usuarios (Conocimiento Colaborativo)
- Formulario para agregar nuevos síntomas y diagnósticos
- Validación de longitud mínima (10 chars síntoma, 20 chars diagnóstico)
- Contador de caracteres en tiempo real
- Almacenamiento temporal con marca de revisión
- **Integración automática con motor de inferencia**:
  - Los síntomas aparecen en la lista de selección con prefijo "[👤 Usuario]"
  - Los diagnósticos se devuelven con sufijo "[Sugerido por usuario - temporal]"
  - Funcionamiento completo end-to-end sin reinicio del servidor

### 7. Menú de Navegación
- Acceso rápido a todas las secciones desde la página principal
- Enlaces a historial de diagnósticos
- Acceso a reportes manuales
- Enlace al módulo de ingreso de datos

## 🎨 Interfaz de Usuario

- **Paleta de colores**: Basada en el logo institucional
  - Azul principal (#2563eb)
  - Celeste/Azul claro (#0ea5e9)
  - Gris (#6b7280)
  - Texto negro (#111827)
- **Diseño responsive**: Adaptable a diferentes tamaños de pantalla
- **Interfaz intuitiva**: Iconos emoji para mejor comprensión
- **Feedback visual**: Mensajes de éxito, advertencias y estados claros

## 📊 Persistencia de Datos

El sistema utiliza archivos JSON para almacenamiento persistente:

| Archivo | Propósito |
|---------|-----------|
| `base_conocimiento.json` | Reglas y síntomas predefinidos del sistema |
| `historial_diagnosticos.json` | Diagnósticos realizados con feedback de usuarios |
| `problemas_manuales.json` | Reportes manuales con flags de urgencia |
| `conocimiento_usuario.json` | Datos temporales aportados por usuarios |

## 🔄 Flujo de Trabajo del Sistema

1. **Usuario accede** → Página principal con menú de opciones
2. **Selecciona categoría** → Hardware o Software
3. **Marca síntomas** → Lista de síntomas relevantes (incluye datos de usuario)
4. **Obtiene diagnóstico** → Motor de inferencia evalúa reglas (base + usuario)
5. **Proporciona feedback** → "Sí sirvió" o "No sirvió"
6. **Acciones adicionales**:
   - Ver historial de diagnósticos
   - Reportar problema manual (con opción de marcar urgente)
   - Aportar nuevos datos al sistema (colaborativo)

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
2.  El servidor se iniciará automáticamente y abrirá tu navegador en `http://127.0.0.1:8000`
3.  Desde la página principal puedes:
    - **Iniciar diagnóstico**: Selecciona una categoría (Hardware/Software) y marca los síntomas
    - **Ver historial**: Revisa diagnósticos pasados y su efectividad
    - **Reportar problema**: Describe un problema manualmente (opción de marcar como urgente)
    - **Ingresar nuevos datos**: Contribuye con nuevos síntomas y diagnósticos al sistema

## 📡 Endpoints de la API

El servidor FastAPI expone los siguientes endpoints:

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Página principal con menú de navegación |
| GET | `/sintomas/{categoria}` | Selección de síntomas por categoría |
| POST | `/diagnostico` | Procesa síntomas y devuelve diagnóstico |
| GET | `/otro-problema` | Formulario de reporte manual |
| POST | `/registrar-otro-problema` | Guarda reporte manual con flag de urgencia |
| POST | `/feedback` | Registra feedback de un diagnóstico |
| GET | `/historial-diagnosticos` | Lista todos los diagnósticos con feedback |
| GET | `/historial-problemas` | Lista todos los reportes manuales |
| GET | `/ingresar-datos` | Formulario de ingreso de nuevos datos |
| POST | `/guardar-nuevo-dato` | Guarda datos aportados por usuarios |

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3, FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Templating**: Jinja2
- **Validación**: Pydantic
- **Almacenamiento**: JSON (persistencia en archivos)
- **Arquitectura**: MVC adaptado (Modelo-Vista-Controlador)

## 👥 Contribuciones de Usuarios

El sistema permite a los usuarios contribuir con nuevos conocimientos de forma colaborativa:

1. Los usuarios pueden agregar síntomas y diagnósticos que no están en la base de conocimiento
2. Los datos se marcan como "temporales" para revisión
3. Se integran automáticamente en el motor de inferencia
4. Los síntomas de usuario aparecen con prefijo "[👤 Usuario]"
5. Los diagnósticos de usuario incluyen sufijo "[Sugerido por usuario - temporal]"

Esta funcionalidad permite que el sistema experto evolucione con el uso real.

## 📝 Notas de Desarrollo

- **Versión del motor de inferencia**: v3.4 (con integración de datos de usuario)
- **Versión de estilos CSS**: v2.4 (paleta azul/celeste)
- **Número de soporte técnico**: +54 11 1234-5678 (configurable en `api_server.py`)

## 🔮 Futuras Mejoras

- Autenticación de usuarios para tracking personalizado
- Dashboard de administración para revisar datos temporales
- Exportación de datos a CSV/Excel
- Sistema de votación para datos de usuario (validación comunitaria)
- Integración con modelo ML real (actualmente es simulado)
- Estadísticas de efectividad de diagnósticos
- Sistema de notificaciones para reportes urgentes

---

**Desarrollado como proyecto académico de Sistemas de Inteligencia Artificial**