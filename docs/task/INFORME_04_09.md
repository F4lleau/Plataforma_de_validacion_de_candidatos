# Ejecución Tasks 04–09

## Resultado

Tasks 04–08 implementadas y verificadas con datos/plantillas de prueba. Task 09 completa
la preparación autorizada; conexión real RENAPER diferida hasta contar con proveedor/API.
Se preservan los cambios previos de Task 03 y setup, sin commit ni push.

[Recorrido, endpoints, modelos, decisiones y límites](../ELECTORAL_WORKFLOWS.md).

## Checks

- Backend: **73 passed**.
- Frontend: **11 passed**, build y lint aprobados.
- Alembic actual/head: **e271bb89a403**; sin cambios de esquema pendientes.
- Base PostgreSQL vacía: upgrade → downgrade → upgrade aprobado.
- Base existente: usuarios/padrón/listas conservados; datos demo adicionales cargados.
- Concurrencia PostgreSQL: dos imports simultáneos, un único lote vigente.
- Navegador: ADMIN configuración/apoderados/padrón; APODERADO detalle/alta/borrador;
  rutas admin denegadas; móvil sin overflow; sin errores JavaScript.
- [Pantalla móvil](evidencia-04-09/lista-mobile.png), [controles por candidato](evidencia-04-09/validaciones-mobile.png).
- Script temporal de datos locales ejecutado y eliminado. No se versionan credenciales/seed.

## Aclaraciones

API RENAPER real, muestras/plantillas institucionales y criterios pendientes no se dan
por validados. Persisten deprecaciones datetime/passlib y aviso de Browserslist.
Las verificaciones de proveedor son dobles/no configurado, no conexiones reales.
Las pruebas automatizadas ajustan los antiguos contratos de catálogo ADMIN-only y
carga sin lista al nuevo contrato de consultas acotadas y candidatos por lista.

## Git status de cierre

Snapshot incluye cambios de tareas anteriores; archivos nuevos figuran como `??` hasta
agregarlos al índice. La documentación de tasks se vuelve a agregar sin generar commit.

```text
 M backend/AGENTS.md
 M backend/README.md
 M backend/app/api/v1/endpoints/auth.py
 M backend/app/api/v1/endpoints/candidates.py
 M backend/app/api/v1/endpoints/elections.py
 M backend/app/api/v1/endpoints/lists.py
 M backend/app/api/v1/endpoints/municipalities.py
 M backend/app/api/v1/endpoints/offices.py
 M backend/app/api/v1/endpoints/padron.py
 M backend/app/api/v1/endpoints/users.py
 M backend/app/api/v1/endpoints/validations.py
 M backend/app/api/v1/router.py
 M backend/app/core/config.py
 M backend/app/core/security.py
 M backend/app/integrations/renaper_client.py
 M backend/app/models/__init__.py
 M backend/app/models/affiliate_import_batch.py
 M backend/app/models/candidate.py
 M backend/app/models/candidate_validation.py
 M backend/app/models/election.py
 M backend/app/models/electoral_list.py
 M backend/app/models/office.py
 M backend/app/models/party_member.py
 M backend/app/repositories/candidate_repository.py
 M backend/app/repositories/list_repository.py
 M backend/app/repositories/party_member_repository.py
 M backend/app/repositories/user_repository.py
 M backend/app/services/affiliate_import_service.py
 M backend/app/services/candidate_service.py
 M backend/app/services/list_service.py
 M backend/app/services/list_validation_service.py
 M backend/app/services/office_validation_service.py
 M backend/app/services/renaper_validation_service.py
 M backend/tests/test_auth_rbac.py
 M backend/tests/test_candidate_api.py
 M docs/BUSINESS_RULES.md
 M docs/PROJECT_CONTEXT.md
A  docs/task/03-authentication-rbac/apoderado-mobile.png
A  docs/task/03-authentication-rbac/report.md
A  docs/task/03-authentication-rbac/status.md
A  docs/task/03-authentication-rbac/task-original.txt
A  docs/task/03-authentication-rbac/task.md
AM docs/task/04-configuracion-electoral/status.md
AM docs/task/04-configuracion-electoral/task.md
AM docs/task/05-apoderados-asignaciones/status.md
AM docs/task/05-apoderados-asignaciones/task.md
AM docs/task/06-padron-oficial/status.md
AM docs/task/06-padron-oficial/task.md
AM docs/task/07-listas-plantillas/status.md
AM docs/task/07-listas-plantillas/task.md
AM docs/task/08-candidatos-requisitos/status.md
AM docs/task/08-candidatos-requisitos/task.md
AM docs/task/09-renaper-validacion-identidad/status.md
AM docs/task/09-renaper-validacion-identidad/task.md
A  docs/task/10-composicion-envio-aprobacion/status.md
A  docs/task/10-composicion-envio-aprobacion/task.md
A  docs/task/11-bandeja-administrativa-validaciones/status.md
A  docs/task/11-bandeja-administrativa-validaciones/task.md
A  docs/task/12-dashboards-por-rol/status.md
A  docs/task/12-dashboards-por-rol/task.md
A  docs/task/13-reportes-exportaciones/status.md
A  docs/task/13-reportes-exportaciones/task.md
A  docs/task/14-auditoria-historial/status.md
A  docs/task/14-auditoria-historial/task.md
A  docs/task/15-aceptacion-manual-soporte/status.md
A  docs/task/15-aceptacion-manual-soporte/task.md
AM docs/task/CAPACIDADES.md
AM docs/task/DECISIONES.md
A  docs/task/FUENTE_MANUAL.md
A  docs/task/PLANIFICACION.md
AM docs/task/README.md
 M frontend/AGENTS.md
 M frontend/README.md
 M frontend/package-lock.json
 M frontend/package.json
 M frontend/src/App.tsx
 M frontend/src/Root.tsx
 M frontend/src/components/layout/AppLayout.tsx
 M frontend/src/index.css
 M frontend/src/pages/Candidatos.tsx
 M frontend/src/pages/CandidatosRevision.tsx
 M frontend/src/pages/Configuracion.tsx
 M frontend/src/pages/Forbidden.tsx
 M frontend/src/pages/Listas.tsx
 M frontend/src/pages/Login.tsx
 M frontend/src/pages/Padron.tsx
 M frontend/src/pages/Usuarios.tsx
 M frontend/src/services/api.ts
 M frontend/src/services/auth.service.ts
 M frontend/src/services/lists.service.ts
 M frontend/src/services/padron.service.ts
 M frontend/src/stores/auth.store.ts
?? README.md
?? backend/alembic/versions/dc5da19db749_electoral_configuration_assignments_and_.py
?? backend/alembic/versions/e271bb89a403_electoral_range_constraints.py
?? backend/app/models/election_rule.py
?? backend/app/models/list_assignment.py
?? backend/app/repositories/management_repository.py
?? backend/app/repositories/padron_repository.py
?? backend/app/repositories/user_module_repository.py
?? backend/app/schemas/management.py
?? backend/app/services/access_service.py
?? backend/app/services/audit_service.py
?? backend/app/services/electoral_workflow_service.py
?? backend/app/services/management_service.py
?? backend/app/services/padron_service.py
?? backend/app/services/transaction.py
?? backend/tests/test_tasks_04_09.py
?? docs/AUTHENTICATION.md
?? docs/ELECTORAL_WORKFLOWS.md
?? docs/task/04-configuracion-electoral/report.md
?? docs/task/05-apoderados-asignaciones/report.md
?? docs/task/06-padron-oficial/report.md
?? docs/task/07-listas-plantillas/report.md
?? docs/task/08-candidatos-requisitos/report.md
?? docs/task/09-renaper-validacion-identidad/report.md
?? docs/task/evidencia-04-09/
?? frontend/src/components/forms/
?? frontend/src/hooks/
?? frontend/src/pages/ListaDetalle.tsx
?? frontend/src/services/management.service.ts
?? frontend/src/tests/
?? local-deps.yml
?? scripts/
```

## Git diff --stat

Este comando solo cuenta archivos ya conocidos por Git; los nuevos están listados arriba.

```text
 backend/AGENTS.md                                  |  10 +-
 backend/README.md                                  |  25 +-
 backend/app/api/v1/endpoints/auth.py               |  18 +-
 backend/app/api/v1/endpoints/candidates.py         |   8 +-
 backend/app/api/v1/endpoints/elections.py          |  65 ++-
 backend/app/api/v1/endpoints/lists.py              | 105 ++++-
 backend/app/api/v1/endpoints/municipalities.py     |  33 +-
 backend/app/api/v1/endpoints/offices.py            |  33 +-
 backend/app/api/v1/endpoints/padron.py             |  38 +-
 backend/app/api/v1/endpoints/users.py              |  47 +-
 backend/app/api/v1/endpoints/validations.py        |   7 +-
 backend/app/api/v1/router.py                       |  15 +-
 backend/app/core/config.py                         |   1 +
 backend/app/core/security.py                       |  15 +-
 backend/app/integrations/renaper_client.py         |  26 +-
 backend/app/models/__init__.py                     |   3 +
 backend/app/models/affiliate_import_batch.py       |   3 +-
 backend/app/models/candidate.py                    |   3 +-
 backend/app/models/candidate_validation.py         |   3 +-
 backend/app/models/election.py                     |   7 +-
 backend/app/models/electoral_list.py               |   5 +-
 backend/app/models/office.py                       |   3 +-
 backend/app/models/party_member.py                 |  21 +-
 backend/app/repositories/candidate_repository.py   |  51 +-
 backend/app/repositories/list_repository.py        |  70 ++-
 .../app/repositories/party_member_repository.py    |   1 +
 backend/app/repositories/user_repository.py        |   5 +-
 backend/app/services/affiliate_import_service.py   | 290 +++++++-----
 backend/app/services/candidate_service.py          |  11 +-
 backend/app/services/list_service.py               |  11 +-
 backend/app/services/list_validation_service.py    | 160 +++----
 backend/app/services/office_validation_service.py  |  45 +-
 backend/app/services/renaper_validation_service.py |  31 +-
 backend/tests/test_auth_rbac.py                    | 158 ++++++-
 backend/tests/test_candidate_api.py                |   4 +-
 docs/BUSINESS_RULES.md                             |  31 +-
 docs/PROJECT_CONTEXT.md                            |  92 +---
 docs/task/04-configuracion-electoral/status.md     |  30 +-
 docs/task/04-configuracion-electoral/task.md       |  86 ++--
 docs/task/05-apoderados-asignaciones/status.md     |  30 +-
 docs/task/05-apoderados-asignaciones/task.md       |  90 ++--
 docs/task/06-padron-oficial/status.md              |  30 +-
 docs/task/06-padron-oficial/task.md                |  88 ++--
 docs/task/07-listas-plantillas/status.md           |  30 +-
 docs/task/07-listas-plantillas/task.md             |  90 ++--
 docs/task/08-candidatos-requisitos/status.md       |  30 +-
 docs/task/08-candidatos-requisitos/task.md         |  96 ++--
 .../task/09-renaper-validacion-identidad/status.md |  30 +-
 docs/task/09-renaper-validacion-identidad/task.md  |  88 ++--
 docs/task/CAPACIDADES.md                           |  12 +
 docs/task/DECISIONES.md                            |  16 +
 docs/task/README.md                                |  22 +-
 frontend/AGENTS.md                                 |  21 +-
 frontend/README.md                                 |  20 +-
 frontend/package-lock.json                         | 303 +++++++++++-
 frontend/package.json                              |   4 +-
 frontend/src/App.tsx                               |   8 +-
 frontend/src/Root.tsx                              |   5 +
 frontend/src/components/layout/AppLayout.tsx       |  16 +-
 frontend/src/index.css                             |   7 +-
 frontend/src/pages/Candidatos.tsx                  | 181 +------
 frontend/src/pages/CandidatosRevision.tsx          |  12 +-
 frontend/src/pages/Configuracion.tsx               | 518 +++++++++++++++++++++
 frontend/src/pages/Forbidden.tsx                   |   5 +
 frontend/src/pages/Listas.tsx                      | 288 +++++++++---
 frontend/src/pages/Login.tsx                       |  57 ++-
 frontend/src/pages/Padron.tsx                      | 305 ++++++++----
 frontend/src/pages/Usuarios.tsx                    | 262 +++++++++++
 frontend/src/services/api.ts                       |  80 ++--
 frontend/src/services/auth.service.ts              |  14 +-
 frontend/src/services/lists.service.ts             |  24 +-
 frontend/src/services/padron.service.ts            |   2 +-
 frontend/src/stores/auth.store.ts                  |  41 +-
 73 files changed, 3167 insertions(+), 1228 deletions(-)
```
