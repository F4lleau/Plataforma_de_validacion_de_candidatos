# Autenticación, roles y sesión

## API y autorización

| Endpoint | Acceso y comportamiento |
| --- | --- |
| `POST /api/v1/auth/login` | JSON `email`/`password`; valida hash y usuario activo; error genérico 401. |
| `GET /api/v1/auth/me` | Bearer válido; devuelve usuario y rol actuales de BD, sin hash. |
| `POST /api/v1/padron/import` | ADMIN; `imported_by` se toma de `current_user.id`. |
| `GET /api/v1/candidates/review` | ADMIN; consulta advertencias de afiliación. |
| `POST /api/v1/candidates` | Compatibilidad solo ADMIN; para APODERADO usar la ruta contextual por lista; `created_by` se toma de `current_user.id`. |
| `GET /api/v1/candidates` | ADMIN ve todos; APODERADO solo candidatos vinculados a listas asignadas y módulos habilitados. |
| `GET /api/v1/lists/` | Consulta real; ADMIN ve todas, APODERADO solo las asignadas con módulo habilitado. |
| `GET /api/v1/validations/list/{list_id}` | Usuario autenticado y acceso a la lista; conserva `office_type` como parámetro de plantilla. |
| `GET /api/v1/list-templates/{office_type}` | Usuario autenticado; catálogo de plantillas compartido. |

Configuración y usuarios ya exponen gestión real. Consultas de catálogos están
filtradas por módulos; sus mutaciones requieren ADMIN. Listas y candidatos requieren
módulo más asignación por lista. El POST antiguo de candidatos queda solo para ADMIN;
APODERADO usa `/lists/{id}/candidates`. Ver [contratos actuales](ELECTORAL_WORKFLOWS.md).

El dashboard sigue sin métricas reales (Task 12). Ausencia de token: 401; usuario
sin permiso: 403; recurso inexistente: 404. Ausencia de afiliación permite guardar.

## JWT y contraseñas

Se conserva passlib/bcrypt y el JWT firmado con la clave de entorno. El algoritmo
predeterminado es HS256; el access token vence a los 30 minutos por defecto.
Se exigen `exp`, `sub` y `type=access`, se valida la firma y se consulta el usuario
activo en BD en cada request. El claim de rol no concede permisos por sí mismo.

La API conserva el campo `refresh_token` por compatibilidad, pero no tiene endpoint
de renovación, rotación ni revocación. El frontend no lo persiste ni lo usa.
Logout elimina la sesión local; un access token copiado previamente sigue válido
hasta vencer o desactivar al usuario. Refresh y revocación quedan para otra tarea.

## Sesión y navegación frontend

Zustand mantiene usuario, access token, autenticación y carga. Al iniciar o cambiar
el token en otra pestaña se consulta `/auth/me` antes de habilitar las rutas.
`api.ts` agrega Bearer a JSON y uploads y, ante 401, limpia localStorage y Zustand.
Un 403 conserva la sesión. Las respuestas anteriores a logout/nuevo login no pueden
restaurar ni cerrar una sesión posterior. No se almacena la contraseña.

| Ruta | Acceso |
| --- | --- |
| `/login` | Público; una sesión validada redirige a dashboard. |
| `/dashboard` | ADMIN y APODERADO. |
| `/padron` | ADMIN. |
| `/listas` | Ambos roles; listas asignadas, creación y detalle con plantilla versionada. |
| `/candidatos` | Ambos roles; acceso al flujo de carga contextual desde listas. |
| `/candidatos/revision` | ADMIN. |
| `/403` | Sesión válida, layout y enlace para regresar. |

La navegación ADMIN incluye Configuración y Apoderados. Ambos roles tienen detalle
de listas, carga contextual y validaciones. Mostrar/ocultar contraseña y recuperación
asistida están disponibles en login; `SUPPORT_CONTACT` configura un contacto opcional.

## Usuarios y prueba manual

El bootstrap usa `INITIAL_ADMIN_EMAIL`/`INITIAL_ADMIN_PASSWORD` desde el entorno local.
Las claves del seed solo están en `backend/.env`. La gestión de apoderados permite alta,
edición, módulos, activación y restablecimiento sin mostrar hashes ni claves guardadas.

Para probar: ADMIN configura elección/cargo/reglas, crea un apoderado con módulos;
APODERADO crea una lista, guarda un candidato y consulta sus tres controles. Probar
revocación de asignaciones y acceso directo a `/configuracion` con rol APODERADO.
El [recorrido detallado](ELECTORAL_WORKFLOWS.md) explica datos de prueba y limitaciones.

## Verificación automatizada

Backend (desde `backend/` con entorno activado):

```bash
python -m pytest -q
alembic current
alembic heads
```

Frontend (desde `frontend/`):

```bash
npm ci
npm run test
npm run build
npm run lint
```

Vitest cubre restauración, logout, 401 de JSON/uploads, 403, respuestas obsoletas y
errores de login. Los tests backend mantienen Task 02B y agregan usuario inactivo,
JWT incompleto/firma inválida, rol de BD, autoría e aislamiento por módulos.
