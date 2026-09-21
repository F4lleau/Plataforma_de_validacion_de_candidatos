# Task 20 — Invitaciones y primer acceso

Implementación y aceptación local: 21/09/2026, `develop`, sin commit/push.
[Informe consolidado, matriz y pruebas](../INFORME_16_21.md).

## Entrega

Modelo Invitation separado, digest/generación, vigencia/cooldown/cuota configurables,
CRUD de invitación limitado a ADMIN con reauth, aceptación atómica, email verificado
y frontend de primer acceso. POST /users cerrado al alta manual; usuarios legacy
conservados; catálogos/rol del invitador revalidados y ninguna lista autoasignada.

Migración `a72e903d418f`, índice normalizado con preflight, outbox cifrada de invitación,
retención y auditoría. API → service → repository preservado. Pantallas de Apoderados,
Invitaciones y Perfil/seguridad actualizadas; captura de token aislada por finalidad.

## Verificación

- Backend completo: 167 tests aprobados. Tras ajuste de orden de locks: 27 tests de invitaciones/PostgreSQL aprobados.
- Frontend: 17 tests, build y lint correctos.
- Alembic head/current `a72e903d418f`, check sin diferencias; backup/restore real.
- Navegador: invitación SMTP local → perfil/clave → login APODERADO; otra sesión
  preservada, móvil sin desborde, bloqueo/desbloqueo y recuperación con revocación.
- `git diff --check` sin errores. Cambios funcionales/documentales de 16–21 sin
  versionar aún; `.env` real ignorado, ejemplos preparados para versionado.

## Límites

SMTP externo/HTTPS real/dominio y aceptación institucional pendientes. No se
declara producción completada ni conformidad NIST/ASVS. No se alteraron reglas
electorales ni se incorporó API RENAPER. No se versionaron scripts/credenciales de QA.
