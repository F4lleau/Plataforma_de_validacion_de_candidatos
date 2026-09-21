# Informe — Task 08

**Resultado:** Completada en alcance de prueba.

Alta y corrección transaccional por lista, borrador/validación separados, posiciones, edad configurable, afiliación no bloqueante y revisión de resultados. Borrador exige identidad mínima completa.

## Implementación principal

- `backend/app/services/electoral_workflow_service.py`
- `backend/app/services/office_validation_service.py`
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

- Ningún impedimento técnico para el alcance de prueba. Las decisiones institucionales siguen identificadas en DECISIONES.md.

Ver [decisiones](../DECISIONES.md), [contratos](../../ELECTORAL_WORKFLOWS.md) y
[git status/diff de cierre](../INFORME_04_09.md). Sin commit ni push.
