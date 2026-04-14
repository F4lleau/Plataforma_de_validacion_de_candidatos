# Backend - Junta Electoral

## Tecnologías principales

- **Python 3.12**
- **FastAPI**: Framework web moderno y rápido para construir APIs.
- **SQLAlchemy**: ORM para manejar la base de datos de forma eficiente.
- **Alembic**: Herramienta de migraciones para SQLAlchemy.
- **PostgreSQL**: Base de datos relacional robusta y escalable.
- **Neon**: Servicio de PostgreSQL en la nube, ideal para desarrollo y producción.

## ¿Por qué estas tecnologías?

- **FastAPI** permite desarrollar APIs de alto rendimiento con tipado y documentación automática.
- **SQLAlchemy** y **Alembic** facilitan la gestión y migración de la base de datos.
- **PostgreSQL** es confiable, potente y ampliamente soportado.
- **Neon** permite tener una base de datos PostgreSQL gestionada en la nube, facilitando el despliegue y la colaboración.

## Instalación de dependencias

1. Clona el repositorio y entra a la carpeta backend:
   ```bash
   git clone <url-del-repo>
   cd junta_electoral/backend
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # En Linux/Mac
   source .venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de la base de datos

1. Crea una cuenta y un proyecto en [Neon](https://neon.tech/).
2. Obtén la cadena de conexión (connection string) de tu base de datos PostgreSQL en Neon.
3. Crea un archivo `.env` en la carpeta backend con el siguiente contenido:
   ```env
   DATABASE_URL=postgresql+psycopg2://<usuario>:<password>@<host>/<db_name>
   ```

## Migraciones con Alembic

- **Inicializar Alembic** (solo la primera vez):
  ```bash
  alembic init alembic
  ```
- **Crear una nueva migración automática:**
  ```bash
  alembic revision --autogenerate -m "mensaje de la migración"
  ```
- **Aplicar migraciones a la base de datos:**
  ```bash
  alembic upgrade head
  ```

> Asegúrate de que la variable `DATABASE_URL` esté correctamente configurada en tu `.env`.

## Comandos útiles

- **Correr el servidor de desarrollo:**
  ```bash
  uvicorn main:app --reload
  ```
- **Ver el estado de las migraciones:**
  ```bash
  alembic current
  ```

## Archivos clave

- `main.py`: Punto de entrada de la API.
- `models/`: Definición de modelos de base de datos.
- `alembic/`: Configuración y scripts de migración.
- `.env`: Variables de entorno (no subir a GitHub).

## Notas

- Usa siempre un entorno virtual para evitar conflictos de dependencias.
- No subas el archivo `.env` ni la carpeta `.venv` al repositorio.
- Consulta la documentación oficial de cada tecnología para más detalles.
