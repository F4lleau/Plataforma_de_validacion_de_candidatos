# Junta Electoral — desarrollo local

Backend FastAPI + SQLAlchemy, frontend React + Vite y PostgreSQL en Docker.
La API usa las migraciones Alembic existentes. La afiliación se consulta en el
padrón importado desde Excel; RENAPER todavía no tiene una integración productiva.
Autenticación, configuración, padrón, listas/candidatos, envío, bandeja, dashboards,
reportes/exportaciones y auditoría están implementados y probados localmente. Las
reglas de prueba no sustituyen confirmación institucional ni integración real RENAPER.

## Requisitos

- Docker con Docker Compose.
- Python 3.12 (versión utilizada para verificar este entorno).
- Node.js 22.12+ o 24 y npm.

## Preparar y levantar la base

Desde la raíz del repositorio:

```bash
python3 scripts/init_local_env.py
docker compose -f local-deps.yml up -d --wait
```

El script genera contraseñas aleatorias y configuración en `.env` y
`backend/.env`, ignorados por Git. No sobrescribe archivos existentes; se ejecuta
solo la primera vez. También genera las credenciales del administrador local
(`INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` en `backend/.env`).

PostgreSQL 17 escucha en `127.0.0.1:5432` y conserva sus datos en un volumen.
Si el puerto está ocupado, ejecutar el generador con `POSTGRES_PORT=5433`.
El Compose solo contiene PostgreSQL: el código actual no requiere Redis ni colas.

## Backend

En una terminal, desde la raíz:

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m dotenv -f .env run -- .venv/bin/python -m scripts.bootstrap_admin
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si usás `uv`, podés crear el entorno con `uv venv --python 3.12 .venv` e
instalar con `uv pip install --python .venv/bin/python -r requirements.txt`.

API: <http://localhost:8000>. Swagger: <http://localhost:8000/docs>.
El bootstrap crea el administrador si aún no existe; no reemplaza su contraseña.
La base inicial no incluye padrón, elecciones ni candidatos.

## Frontend

En otra terminal, desde la raíz:

```bash
cd frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Abrir <http://localhost:5173> e iniciar sesión con las credenciales generadas.
El cliente API actual apunta a `http://localhost:8000/api/v1`.

## Verificar y detener

```bash
docker compose -f local-deps.yml ps
docker compose -f local-deps.yml logs postgres
```

Desde `backend/`: `.venv/bin/python -m pytest tests -q`.
Desde `frontend/`: `npm run build` y `npm run lint`.

Detener backend y frontend con `Ctrl+C` en sus terminales. Desde la raíz,
`docker compose -f local-deps.yml down` detiene PostgreSQL y conserva el volumen.
No agregar `-v` salvo que se quiera borrar la base local.

## Gestión electoral

Ver [configuración, apoderados, listas y carga de candidatos](docs/ELECTORAL_WORKFLOWS.md)
y [seguimiento de Tasks 04–09](docs/task/INFORME_04_09.md).


## Guías y aceptación

- [Manual ADMIN](docs/MANUAL_ADMIN.md) y [manual APODERADO](docs/MANUAL_APODERADO.md).
- [Envío, reportes y auditoría](docs/SUBMISSION_REPORTING_AUDIT.md).
- [Operación local, respaldo y recuperación](docs/OPERACION_LOCAL.md).
- [Tasks 10–15: resultados, capturas y pendientes](docs/task/INFORME_10_15.md).

Una lista completa con observaciones puede enviarse a revisión y queda en lectura.
La aprobación automática exige controles obligatorios vigentes y verificados;
RENAPER pendiente y plantillas experimentales nunca la habilitan.
