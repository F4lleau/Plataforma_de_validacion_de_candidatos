# Backend AGENTS.md

## Objetivo

Documentar la arquitectura y las convenciones del backend de la plataforma de validación de candidatos, basado en el estado real del repositorio.

## Stack actual

- Python
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL / Neon
- Pydantic Settings
- JWT
- passlib/bcrypt
- pandas/openpyxl para importación de padrón

## Estructura principal

```text
backend/
  app/
    api/v1/endpoints/
    core/
    db/
    integrations/
    models/
    repositories/
    schemas/
    services/
    utils/
  alembic/
  requirements.txt
```

## Arquitectura y capas

### Endpoint

Los endpoints deben exponer la interfaz HTTP y delegar la lógica a servicios. No deben incluir lógica compleja de negocio ni SQL directo.

### Service

La lógica de negocio vive en servicios. Aquí se componen validaciones, reglas de dominio y llamadas a repositorios e integraciones.

### Repository

Los repositorios encapsulan el acceso a la base de datos y las consultas más específicas de cada modelo.

### Model / DB

Los modelos SQLAlchemy están definidos en `backend/app/models/`. La base se configura en `backend/app/db/` y las migraciones se gestionan con Alembic.

## SQLAlchemy y Alembic

- Los modelos se crean con SQLAlchemy 2, usando `Mapped` y `mapped_column`.
- La base de datos debe evolucionar vía migraciones Alembic.
- No usar `Base.metadata.create_all()` como reemplazo de migraciones.
- Antes de crear una nueva migración, revisar modelos, heads y compatibilidad incremental.
- Evitar borrar datos existentes al generar cambios estructurales.

## Configuración y seguridad

- La configuración principal entrega `secret_key`, `algorithm`, `database_url`, `cors_origins` a través de `pydantic-settings`.
- El acceso se basa en JWT.
- La seguridad es responsabilidad del backend: validar roles y permisos en cada operación relevante.
- No hardcodear IDs de usuarios ni credenciales.
- No exponer `DATABASE_URL` en documentación pública.
- No guardar passwords sin hash.
- El hash se realiza con `passlib` y `bcrypt`.

## Autenticación y autorización

La seguridad actual se basa en JWT y en roles definidos por `UserRole`:

- `admin`
- `apoderado`

La aplicación usa `auth_service` para generar tokens e incluye datos del rol en el payload. La autorización final debe validarse en backend, no confiar en un rol enviado por el frontend.

## Validaciones y reglas de dominio

Los validadores del backend incluyen:

- validación de afiliación por DNI contra padrón importado;
- validación de composición de listas por cargos requeridos;
- validación por género con paridad/alternancia cuando la lógica esté presente;
- validación de requisitos de cargo y otros tipos definidos en enums.

### Estado real de la lógica

Hay servicios de validación implementados y otros parcialmente estructurados:

- `AffiliationValidationService`: valida si el DNI existe en el padrón.
- `ListValidationService`: valida completitud, posiciones, duplicados, paridad y alternancia.
- `OfficeValidationService` y `RenaperValidationService`: existen como estructura inicial o pendiente, no como integración productiva.

## Padrón PJ

### Estado actual

El padrón no es una API externa. Se importa desde Excel y se persiste en la base de datos.

El flujo implementado incluye:

- `AffiliateImportService` para leer Excel, normalizar columnas, validar filas mínimas y crear registros de `PartyMember`.
- `AffiliateImportBatch` para registrar el lote de importación.
- `PartyMemberRepository` para consultar miembros por DNI y limpiar importaciones por batch.
- endpoint `POST /api/v1/padron/import` para subir archivos Excel.
- endpoint `POST /api/v1/candidates` para registrar candidatos y persistir la validación de afiliación.
- endpoint `GET /api/v1/candidates/review` para consultar observaciones de afiliación.

La dependencia JWT `get_current_user` ya resuelve usuarios activos desde el token y la base de datos. El login HTTP y el RBAC completo permanecen como integración de Task 03; los endpoints no aceptan IDs de usuario enviados por el frontend.

### Regla crítica

La ausencia en padrón no debe bloquea automáticamente un candidato. La validación debe quedar como advertencia/observación e indicar revisión administrativa, sin impedir la carga ni el trabajo sobre la lista.

Esto es un punto disciplinario del proyecto y debe respetarse en futuros cambios.

## RENAPER

Existe una estructura de integración en `backend/app/integrations/` y un cliente base, pero no hay integración real productiva.

No asumir que RENAPER funciona en producción ni documentarlo como si estuviera operativo.

La clase `RenaperClient` y el servicio `RenaperValidationService` están en una etapa de base/mock o pendiente, no como implementación productiva real.

## Endpoints relevantes

Se encuentran en `backend/app/api/v1/endpoints` y se agrupan bajo `api/v1/router.py`.

Ejemplos relevantes:

- auth
- users
- elections
- offices
- municipalities
- lists
- candidates
- validations
- dashboard
- padron
- list_templates

El patrón deseado es que los endpoints se mantengan simples y deleguen la lógica a services/repositories.

## Testing

Antes de cerrar una tarea:

- revisar imports y referencias no usados;
- ejecutar tests existentes;
- comprobar que FastAPI pueda iniciar;
- revisar si hubo cambios en modelos o migraciones.

No declarar una task terminada si existen errores conocidos relacionados con la parte modificada.

## Reglas de seguridad

- nunca hardcodear IDs, usuarios o credenciales;
- nunca commitear `.env`;
- nunca guardar password sin hash;
- nunca confiar en roles enviados por el frontend;
- validar permisos en backend.

## Documentación

Cuando se modifique infraestructura, setup, endpoints, flujos, dependencias, validaciones o migraciones, actualizar la documentación relevante del repositorio.

## Referencias

- [backend/README.md](../backend/README.md)
- [AGENTS.md](../AGENTS.md)
- [docs/PROJECT_CONTEXT.md](../docs/PROJECT_CONTEXT.md)
- [docs/BUSINESS_RULES.md](../docs/BUSINESS_RULES.md)
