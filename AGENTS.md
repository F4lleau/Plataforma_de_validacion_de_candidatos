# AGENTS.md

## Objetivo

Esta documentación central define la base operativa para agentes de desarrollo del proyecto Junta Electoral / Plataforma de Validación de Candidatos.

El proyecto tiene como finalidad apoyar a la Junta Electoral del Partido Justicialista, Distrito Chaco, en la gestión de listas, candidatos y validaciones antes de la revisión administrativa.

## Alcance

- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL/Neon
- Frontend: React + TypeScript + Vite + Tailwind
- Documentación y arquitectura: esta carpeta y los documentos especializados en `backend/`, `frontend/` y `docs/`

## Roles principales

### ADMIN

- administra usuarios y apoderados;
- importa y actualiza el padrón de afiliados PJ;
- revisa candidatos y listas;
- accede a observaciones y validaciones;
- gestiona información electoral.

### APODERADO

- trabaja sobre los módulos/listas asignados;
- carga candidatos;
- consulta validaciones;
- completa listas;
- remite listas para revisión.

## Regla crítica de negocio

La afiliación partidaria se valida contra el padrón de afiliados PJ cargado por el administrador.

No existe una API externa del padrón. El padrón se importa mediante Excel y se persiste en la base de datos.

Importante: un candidato ausente en el padrón NO debe bloquear su registro. Debe:

1. guardarse;
2. registrar la validación de afiliación;
3. mostrar una advertencia al apoderado;
4. marcarlo para revisión administrativa;
5. permitir continuar trabajando con la lista.

La ausencia en padrón es una observación o alerta, no un rechazo automático.

## Arquitectura general

### Backend

- `backend/app/api/v1/endpoints`: endpoints de la API
- `backend/app/services`: lógica de negocio
- `backend/app/repositories`: acceso a datos
- `backend/app/models`: modelos SQLAlchemy
- `backend/app/schemas`: validación de entrada/salida
- `backend/app/core`: configuración, seguridad, utilidades generales
- `backend/app/integrations`: integraciones externas o mockeadas

Se mantiene la separación de responsabilidades: endpoint -> service -> repository -> model/database.

### Frontend

- `frontend/src/modules`: módulos por funcionalidad
- `frontend/src/services`: clientes API y lógica de consumo
- `frontend/src/components`: componentes reutilizables
- `frontend/src/pages`: vistas principales
- `frontend/src/hooks`: hooks reutilizables
- `frontend/src/types`: tipos o contratos del frontend

## Convenciones de desarrollo

- No introducir lógica compleja en endpoints.
- No acceder directamente a SQLAlchemy desde capas que deberían usar repositories/services.
- Mantener una separación clara entre backend y frontend.
- Toda modificación estructural de base de datos se debe hacer mediante Alembic.
- No usar `Base.metadata.create_all()` como reemplazo de migraciones.
- No hardcodear usuarios, credenciales, IDs ni secretos.
- No commitear `.env` ni exponer `DATABASE_URL` en documentación pública.
- Validar permisos y roles en backend.
- Documentar cambios relevantes en README y docs cuando modifiquen setup, endpoints, dependencias o flujos de negocio.

## Dependencias locales

Con Docker iniciado, ejecutar desde la raíz del proyecto:

```bash
docker compose -f local-deps.yml up -d --wait
```

Levanta PostgreSQL y Mailpit (SMTP en `localhost:1025`, bandeja en
<http://localhost:8025>, puertos predeterminados). En una instalación nueva sin
`.env` ni `backend/.env`, ejecutar primero `python3 scripts/init_local_env.py`;
conservar la configuración existente. La API, el frontend y el worker de correo
se inician por separado; ver [operación local](docs/AUTH_OPERATIONS.md).

## Workflow de Git

- Trabajar sobre la rama `develop` del repositorio.
- Revisar el estado del repo antes de seguir con cambios.
- Mantener el alcance de la tarea estrictamente documental cuando así corresponda.
- No generar cambios funcionales, migraciones ni refactors no relacionados.

## Definición de done

Una tarea se considera terminada cuando:

- la documentación refleje la realidad del proyecto;
- las partes mockeadas o incompletas queden claramente indicadas;
- la lógica funcional no haya sido alterada;
- se haya verificado que la documentación no contradiga el código real.

## Referencias

- [backend/AGENTS.md](backend/AGENTS.md)
- [frontend/AGENTS.md](frontend/AGENTS.md)
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md)
- [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md)
- [backend/README.md](backend/README.md)
- [frontend/README.md](frontend/README.md)
