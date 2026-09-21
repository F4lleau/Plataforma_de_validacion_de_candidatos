# Informe — Task 07

**Resultado:** Completada con plantillas de prueba.

Listas, detalle, edición, número, filtros/paginación, versiones de plantilla y asignaciones compartidas explícitas. Migración conserva autoría y datos.

## Implementación principal

- `backend/app/models/list_assignment.py`
- `backend/app/services/electoral_workflow_service.py`
- `frontend/src/pages/Listas.tsx`
- `frontend/src/pages/ListaDetalle.tsx`

Se reutilizan modelos, JWT, repositories y layout. Escrituras administrativas exigen ADMIN;
listas/candidatos de APODERADO requieren módulo habilitado y asignación expresa.
Ausencia/inactividad en padrón conserva el registro con warning.

## Verificación

- `pytest -q`: **73 passed** (incluye regresiones anteriores).
- `npm run test`: **11 passed**; build y lint sin errores.
- Alembic current/heads: `e271bb89a403`; `alembic check` sin operaciones pendientes.
- PostgreSQL vacío: upgrade, downgrade al checkpoint anterior y upgrade de nuevo.
- PostgreSQL con datos: migración local conserva usuarios/listas/padrón previos.
- Importaciones concurrentes: dos lotes completos, exactamente uno vigente.
- Navegador: configuración y apoderado guardados, padrón consultable; APODERADO carga
  candidato ausente, ve controles, corrige y guarda borrador; ADMIN-only deniega acceso.
- Móvil 390×844: sin overflow ni overlay de error.
- [Evidencia visual](../evidencia-04-09/validaciones-mobile.png).

Las pruebas de identidad usan cliente no configurado/dobles, no una API externa real.
Deprecaciones existentes de datetime/passlib y aviso Browserslist no impiden los checks.

## Pendientes del alcance institucional

- Consejos: total exacto 22; obtener nombres/orden/grupos oficiales antes de presentar cargos inventados como definitivos (D02).

Ver [decisiones](../DECISIONES.md), [contratos](../../ELECTORAL_WORKFLOWS.md) y
[git status/diff de cierre](../INFORME_04_09.md). Sin commit ni push.
