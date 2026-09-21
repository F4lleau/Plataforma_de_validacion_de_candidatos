# Task 03 — Informe final

> Actualización de organización (2026-09-20): `docs/task/` dejó de estar excluida
> de Git por pedido del usuario. Las menciones a carpeta ignorada y snapshots Git
> del cierre original se conservan como evidencia histórica. El estado actual es
> versionable; `task-original.txt` preserva la consigna recibida y `task.md` agrega
> un checklist de cierre por mini task.


Estado: completada el 2026-09-20 en `develop`, sin commit ni push.

## Resultado

Se auditó y completó la implementación existente, conservando login, schemas,
servicios, JWT, hashing, bootstrap, router y componentes. La tarea ya tenía la base
funcional; los faltantes corregidos eran de sesión, alcance de permisos, manejo de
errores, navegación móvil y documentación.

La carpeta `docs/task/` contiene consignas, estado, informe y evidencia local; está
excluida de Git. El índice en `docs/task/README.md` define cómo ordenar las próximas tareas.

## Cambios funcionales

- JWT exige expiración y subject, rechaza refresh como access y subjects inválidos;
  resuelve el usuario y rol desde BD mediante UserRepository.
- `require_roles` conserva el control central de roles. `AccessService` y
  `UserModuleRepository` aplican un único criterio de alcance por asignación
  habilitada, elección, cargo y localidad. ADMIN conserva acceso administrativo.
- Carga/consulta de candidatos y consulta/validación de listas respetan ese alcance.
  Se mantiene la advertencia de afiliación sin rechazar automáticamente al candidato.
- `GET /api/v1/lists/` pasó de placeholder a consulta real usando el schema,
  repositorio y servicio existentes; no se construyó un CRUD de listas.
- Routers administrativos placeholder protegidos por ADMIN; plantillas y resumen
  requieren autenticación. Su contenido pendiente no se presenta como un CRUD real.
- Cliente API compartido para JSON/uploads/login: Bearer, manejo seguro de errores,
  401 limpia Zustand/localStorage y 403 mantiene la sesión.
- Restauración `/auth/me`, logout, cambios entre pestañas y respuestas pendientes
  protegidos contra restablecer o cerrar una sesión posterior.
- Login diferencia credenciales incorrectas, error de servidor y desconexión.
- Layout/nav accesible en móvil; 403 conserva layout y ofrece regreso al inicio.
- Listas muestra las listas disponibles y la plantilla existente; indica edición y
  envío pendientes. Revisión/listas muestran errores de carga explícitos.
- Formulario de candidatos conserva la creación real e incluye localidad opcional
  para autorizar cargos municipales del apoderado.

## Endpoints y rutas

Se reutilizan `POST /api/v1/auth/login`, `GET /api/v1/auth/me`,
`POST /api/v1/padron/import`, `GET /api/v1/candidates/review`,
`GET|POST /api/v1/candidates`, `GET /api/v1/list-templates/{office_type}` y
`GET /api/v1/validations/list/{list_id}`. Se completa `GET /api/v1/lists/`.

Rutas frontend: `/login`, `/dashboard`, `/padron`, `/listas`, `/candidatos`,
`/candidatos/revision`, `/403`. ADMIN ve padrón/revisión; APODERADO ve sus listas
por módulo y carga de candidatos. El backend sigue siendo autoridad final.

## JWT, sesión y bootstrap

JWT HS256 por defecto, clave por entorno, access token con 30 minutos de vida por
configuración. Firma, expiración, tipo y usuario activo se comprueban en backend;
el rol firmado no reemplaza al rol de BD. Contraseñas hasheadas con passlib/bcrypt.

El bootstrap existente usa `INITIAL_ADMIN_EMAIL` / `INITIAL_ADMIN_PASSWORD`;
no se regeneraron credenciales ni se ejecutó de nuevo el seed. El usuario APODERADO
local y sus módulos del turno anterior se conservan. Las credenciales siguen solo
en `backend/.env`, ignorado por Git. No se guarda password en frontend.

Refresh se sigue emitiendo por compatibilidad, pero no se persiste ni utiliza en
frontend. Renovación, rotación y revocación quedan para una tarea posterior;
logout elimina la sesión cliente y no revoca un JWT ya emitido.

## Verificación

| Comprobación | Resultado |
| --- | --- |
| `python -m pytest -q` | 40 passed; incluye la suite previa de Task 02B |
| `alembic current` | `8c4f2e91b6a7 (head)` |
| `alembic heads` | `8c4f2e91b6a7 (head)` |
| `npm run test` | 10 passed (Vitest) |
| `npm run build` | Correcto |
| `npm run lint` | Correcto |
| `git diff --check` | Correcto |
| `git check-ignore docs/task/...` | Carpeta excluida correctamente |

Pruebas backend: login correcto/incorrecto, usuario inexistente/inactivo, `/me`,
token ausente/inválido/expirado/firma incorrecta/claims incompletos, refresh rechazado,
rol actualizado en BD, RBAC padrón/revisión/administración, autoría del import y del
candidato, asignación por usuario/elección/cargo/localidad y deshabilitación.

Pruebas frontend: restauración verificada y rechazada, ausencia de token, logout,
401 en JSON/uploads, conservación de sesión ante 403, respuestas obsoletas,
distinción entre credenciales, servidor y red.

Prueba de navegador realizada contra FastAPI + PostgreSQL local con agent-browser:

1. Sin sesión: `/` redirige a `/login`.
2. Login ADMIN: sidebar correcto; acceso al formulario Padrón.
3. Listas ADMIN: se muestran las tres listas del seed y seis cargos de plantilla.
4. Abrir `/login` con sesión: `/auth/me` restaura y redirige a dashboard.
5. Logout: regreso a login.
6. Login APODERADO: Dashboard, Mis listas y Candidatos.
7. Carga de candidatos accesible y listas del seed visibles por sus tres módulos.
8. Abrir `/padron` directamente: redirección a `/403`.
9. Vista 390 × 844: navegación y logout visibles; captura revisada visualmente.
10. Token alterado durante la sesión y request a Mis listas: 401 limpia token y
    Zustand y redirige a `/login`.
11. Sin excepciones de JavaScript, sin overlay de Vite y sin overflow horizontal.

Evidencia: [APODERADO móvil con acceso restringido](apoderado-mobile.png).
Guía reproducible: [docs/AUTHENTICATION.md](../../AUTHENTICATION.md).

## Pendientes reales fuera de alcance

- Refresh, rotación/revocación y eventual estrategia de cookies.
- CRUD/envío de listas, altas/edición visual de usuarios y módulos, revisión administrativa resolutiva.
- Asignación individual por lista: el esquema actual asigna módulos, no listas.
- Localidad de postulación separada del domicilio: hoy se usa el campo existente
  `Person.municipality_id`; requiere definición/modelado posterior.
- Selectores de catálogos en Candidatos; el formulario actual solicita IDs.
- Catálogos administrativos y métricas: conservan placeholders protegidos.
- RENAPER sigue sin integración productiva.
- Advertencias previas de passlib/crypt y datetime.utcnow; no impidieron los tests.
  npm sigue reportando 12 vulnerabilidades del árbol de dependencias (también estaban
  antes de esta task), y Browserslist informa datos desactualizados. No se ejecutó
  una actualización masiva de dependencias fuera del alcance.

## Archivos creados en esta tarea (versionables)

- `backend/app/repositories/user_module_repository.py`
- `backend/app/services/access_service.py`
- `frontend/src/tests/auth.test.ts`
- `docs/AUTHENTICATION.md`

Archivos locales ignorados: `docs/task/README.md`, consigna original `task.md`,
`status.md`, este `report.md` y captura móvil dentro de `03-authentication-rbac/`.

## Archivos modificados

- `.gitignore`
- `backend/AGENTS.md`
- `backend/README.md`
- `backend/app/api/v1/endpoints/candidates.py`
- `backend/app/api/v1/endpoints/lists.py`
- `backend/app/api/v1/endpoints/validations.py`
- `backend/app/api/v1/router.py`
- `backend/app/core/security.py`
- `backend/app/repositories/candidate_repository.py`
- `backend/app/repositories/list_repository.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/services/candidate_service.py`
- `backend/app/services/list_service.py`
- `backend/tests/test_auth_rbac.py`
- `docs/BUSINESS_RULES.md`
- `docs/PROJECT_CONTEXT.md`
- `frontend/AGENTS.md`
- `frontend/README.md`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/Root.tsx`
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/pages/Candidatos.tsx`
- `frontend/src/pages/CandidatosRevision.tsx`
- `frontend/src/pages/Forbidden.tsx`
- `frontend/src/pages/Listas.tsx`
- `frontend/src/pages/Login.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/services/auth.service.ts`
- `frontend/src/services/lists.service.ts`
- `frontend/src/stores/auth.store.ts`

Los README de backend/frontend ya tenían modificaciones del setup anterior y se
conservaron. Los archivos no versionados `README.md`, `local-deps.yml` y
`scripts/init_local_env.py` pertenecen al turno de Docker, no al seed ni a esta task.
No se cambiaron modelos ni migraciones. El seed y sus datos se conservaron.

## git status --short

```text
 M .gitignore
 M backend/AGENTS.md
 M backend/README.md
 M backend/app/api/v1/endpoints/candidates.py
 M backend/app/api/v1/endpoints/lists.py
 M backend/app/api/v1/endpoints/validations.py
 M backend/app/api/v1/router.py
 M backend/app/core/security.py
 M backend/app/repositories/candidate_repository.py
 M backend/app/repositories/list_repository.py
 M backend/app/repositories/user_repository.py
 M backend/app/services/candidate_service.py
 M backend/app/services/list_service.py
 M backend/tests/test_auth_rbac.py
 M docs/BUSINESS_RULES.md
 M docs/PROJECT_CONTEXT.md
 M frontend/AGENTS.md
 M frontend/README.md
 M frontend/package-lock.json
 M frontend/package.json
 M frontend/src/App.tsx
 M frontend/src/Root.tsx
 M frontend/src/components/layout/AppLayout.tsx
 M frontend/src/pages/Candidatos.tsx
 M frontend/src/pages/CandidatosRevision.tsx
 M frontend/src/pages/Forbidden.tsx
 M frontend/src/pages/Listas.tsx
 M frontend/src/pages/Login.tsx
 M frontend/src/services/api.ts
 M frontend/src/services/auth.service.ts
 M frontend/src/services/lists.service.ts
 M frontend/src/stores/auth.store.ts
?? README.md
?? backend/app/repositories/user_module_repository.py
?? backend/app/services/access_service.py
?? docs/AUTHENTICATION.md
?? frontend/src/tests/
?? local-deps.yml
?? scripts/
```

## git diff --stat

```text
 .gitignore                                       |   3 +
 backend/AGENTS.md                                |   2 +-
 backend/README.md                                |  17 +-
 backend/app/api/v1/endpoints/candidates.py       |   6 +-
 backend/app/api/v1/endpoints/lists.py            |  16 +-
 backend/app/api/v1/endpoints/validations.py      |   7 +-
 backend/app/api/v1/router.py                     |  15 +-
 backend/app/core/security.py                     |  15 +-
 backend/app/repositories/candidate_repository.py |  15 +-
 backend/app/repositories/list_repository.py      |   9 +-
 backend/app/repositories/user_repository.py      |   5 +-
 backend/app/services/candidate_service.py        |  11 +-
 backend/app/services/list_service.py             |  11 +-
 backend/tests/test_auth_rbac.py                  | 164 +++++++++++-
 docs/BUSINESS_RULES.md                           |  11 +-
 docs/PROJECT_CONTEXT.md                          |  28 +--
 frontend/AGENTS.md                               |  13 +-
 frontend/README.md                               |  12 +-
 frontend/package-lock.json                       | 303 +++++++++++++++++++++--
 frontend/package.json                            |   4 +-
 frontend/src/App.tsx                             |   2 +-
 frontend/src/Root.tsx                            |   5 +
 frontend/src/components/layout/AppLayout.tsx     |  14 +-
 frontend/src/pages/Candidatos.tsx                |  13 +
 frontend/src/pages/CandidatosRevision.tsx        |  12 +-
 frontend/src/pages/Forbidden.tsx                 |   5 +
 frontend/src/pages/Listas.tsx                    |  44 ++--
 frontend/src/pages/Login.tsx                     |  14 +-
 frontend/src/services/api.ts                     |  75 +++---
 frontend/src/services/auth.service.ts            |  14 +-
 frontend/src/services/lists.service.ts           |  24 +-
 frontend/src/stores/auth.store.ts                |  41 +--
 32 files changed, 751 insertions(+), 179 deletions(-)
```

`git diff --stat` no incluye archivos sin seguimiento ni la carpeta ignorada de tareas.
No se ejecutaron `git add`, commit ni push.
