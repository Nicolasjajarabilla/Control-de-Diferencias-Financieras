# Proyecto de Control de Diferencias Financieras

## Descripción General

Este proyecto es una aplicación backend construida con FastAPI que proporciona una API para analizar y comparar datos financieros de diferentes fuentes, principalmente archivos Excel y CSV. El objetivo principal es identificar discrepancias en las posiciones de instrumentos financieros (como acciones, ADRs, CEDEARs) reportadas por distintas plataformas.

Esta versión ha sido refactorizada para tener una arquitectura más limpia, modular y escalable, separando la lógica de la API de la lógica de negocio.

## Arquitectura del Proyecto

El proyecto sigue una estructura de directorios organizada para separar responsabilidades:

- **`main.py`**: El punto de entrada de la aplicación FastAPI. Configura la app, los middlewares y los routers.
- **`app/api/routers/`**: Contiene los módulos que definen los endpoints de la API.
  - `control_diferencias.py`: Define todas las rutas relacionadas con el procesamiento y la comparación de archivos (`/procesar-diferencias/...`).
- **`app/services/`**: Contiene la lógica de negocio principal.
  - `file_processing_service.py`: Incluye todas las funciones que realizan el trabajo pesado de leer, limpiar y comparar los datos con `pandas`.
- **`requirements.txt`**: Lista de dependencias de Python necesarias para el proyecto.
- **`.env`**: Archivo para configurar las variables de entorno (no incluido en el repositorio).

## Características Principales

- **API RESTful:** Endpoints claros y concisos para cada tipo de comparación.
- **Arquitectura Modular:** Lógica de negocio separada de la capa de la API para mayor mantenibilidad.
- **Procesamiento de Archivos:** Capacidad para procesar archivos Excel (`.xlsx`, `.xls`) y CSV (`.csv`) subidos a través de la API.
- **Lógica de Comparación Específica:**
  - Condor vs. Latin
  - Condor vs. IBKR (Interactive Brokers)
  - Transactions vs. Convers
- **Normalización de Datos:** Funciones para estandarizar los símbolos de los instrumentos financieros antes de la comparación.
- **Asincronía:** Construido sobre FastAPI para un manejo eficiente de las peticiones.

## Tecnologías Utilizadas

- **Backend Framework:**
  - **FastAPI:** Framework web de alto rendimiento para construir APIs.
- **Servidores ASGI/WSGI:**
  - **Uvicorn:** Servidor ASGI ultra rápido para desarrollo y producción.
  - **Gunicorn:** Servidor WSGI de calidad de producción.
- **Procesamiento de Datos:**
  - **Pandas:** Librería fundamental para la manipulación y análisis de datos.
  - **Openpyxl & xlrd:** Librerías para que Pandas pueda trabajar con archivos Excel.
- **Herramientas Adicionales:**
  - **Python-dotenv:** Para gestionar variables de entorno.
  - **Python-multipart:** Para soportar la subida de archivos desde formularios.

## Endpoints de la API

La API expone varios endpoints para procesar archivos y devolver las diferencias encontradas. Todos están agrupados bajo el prefijo `/posiciones`.

### Comparación Condor vs. Latin

- `POST /posiciones/procesar-diferencias-condor-latin/`
  - **Descripción:** Sube dos archivos Excel (de Latin y Condor) para calcular las diferencias en las cantidades de los instrumentos.
  - **Cuerpo de la Petición:** `multipart/form-data` con los archivos `file_latin` y `file_argentina`.
  - **Respuesta Exitosa:** Un JSON con un mensaje y los resultados de la comparación.
    ```json
    {
      "message": "Datos procesados exitosamente",
      "resultados": {
        "SIMBOLO": {
          "Qty-latin": 100,
          "Qty-argentina": 105,
          "Qty-diferencias": 5
        }
      }
    }
    ```

### Comparación Condor vs. IBKR

- `POST /posiciones/procesar-diferencias-condor-ibkr/`
  - **Descripción:** Sube un archivo CSV de IBKR y un Excel de Condor para encontrar discrepancias.
  - **Cuerpo de la Petición:** `multipart/form-data` con los archivos `file_ibkr` y `file_condor`.
  - **Respuesta Exitosa:** Un JSON con los resultados.

### Comparación Transactions vs. Convers

- `POST /posiciones/procesar-transactions-convers/`
  - **Descripción:** Procesa archivos de transacciones y conversiones para conciliar datos.
  - **Cuerpo de la Petición:** `multipart/form-data` con los archivos `file_transactions` y `file_convers`.
  - **Respuesta Exitosa:** Un JSON con los resultados.

## Cómo Ejecutar el Proyecto Localmente

### Prerrequisitos

- Python 3.7+
- Un gestor de paquetes como `pip`

### 1. Clonar el Repositorio

```bash
git clone <URL-del-repositorio>
cd Control_diferencias_excels
```

### 2. Crear un Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto. Puedes dejarlo vacío o especificar un host y puerto.

```
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
```

### 5. Ejecutar el Servidor

Inicia el servidor de desarrollo con Uvicorn.

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva de la API (generada por Swagger UI) en `http://127.0.0.1:8000/docs`.
