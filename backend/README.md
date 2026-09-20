# Backend - Junta Electoral

## Descripción del Sistema

La aplicación backend de Junta Electoral gestiona la administración de elecciones, listas, candidatos y validaciones asociadas. Provee una API RESTful para la gestión de usuarios, listas electorales, candidatos, validaciones y auditoría.

### Requisitos Funcionales

- Gestión de usuarios y autenticación.
- Administración de listas electorales y candidatos.
- Validación de afiliaciones y candidaturas.
- Registro de logs de auditoría.
- Integración con servicios externos (ej: RENAPER).

### Requisitos No Funcionales

- Seguridad basada en JWT y roles.
- Rendimiento optimizado para grandes volúmenes de datos.
- Escalabilidad y modularidad.

## Arquitectura

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Base de datos:** (configurable, por defecto SQLite/PostgreSQL)
- **Migraciones:** Alembic
- **Autenticación:** JWT
- **Integraciones:** RENAPER

### Estructura de Carpetas

- `app/`: Código principal del backend
- `alembic/`: Migraciones de base de datos
- `requirements.txt`: Dependencias

Las migraciones se encuentran en `backend/alembic/versions/`.

## Documentación de APIs

- **Swagger UI:** Disponible en `/docs` al ejecutar el backend.
- **Redoc:** Disponible en `/redoc`.

## Guía de Configuración

### Clonar el Repositorio

```bash
git clone <url-del-repo>
cd junta_electoral/backend
```

### Crear y Activar Entorno Virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Variables de Entorno

Configura las variables en un archivo `.env` en `backend/app/` (ver ejemplo en `config.py`).

### Ejecutar el Backend

```bash
uvicorn app.main:app --reload
```

### Bootstrap de administrador de desarrollo

Definí `INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` en el entorno y ejecutá:

```bash
python scripts/bootstrap_admin.py
```

El script crea un usuario ADMIN solo si no existe. Nunca guarda la contraseña en el código ni la imprime.

La autenticación expone `POST /api/v1/auth/login` y `GET /api/v1/auth/me`. El refresh token se emite para compatibilidad, pero su rotación/revocación queda pendiente de una tarea posterior; el logout actual elimina la sesión del cliente.

### Migraciones de Base de Datos

```bash
alembic upgrade head
```

## Documentación de Usuario

### Guías de Uso

- Accede a la API vía Swagger UI (`/docs`).
- Consulta los endpoints disponibles y prueba operaciones.

### FAQ

- **¿Por qué falla la conexión a la base de datos?**
  - Verifica las variables de entorno y la configuración en `config.py`.
- **¿Cómo crear un usuario admin?**
  - Usa el endpoint de registro y asigna el rol adecuado.

### Solución de Problemas

- **Error de migraciones:** Revisa el estado de Alembic y sincroniza con `alembic upgrade head`.
- **Problemas de dependencias:** Ejecuta `pip install -r requirements.txt`.

## Documentación del Proyecto

### Objetivo del Negocio

Facilitar la gestión y validación de procesos electorales, optimizando la transparencia y eficiencia.

---
