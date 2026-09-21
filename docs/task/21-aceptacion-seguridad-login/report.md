# Task 21 — Aceptación y operación de autenticación

Implementación y aceptación local: 21/09/2026, `develop`, sin commit/push.
[Informe consolidado, matriz y pruebas](../INFORME_16_21.md).

## Entrega

Matriz ADMIN/APODERADO/anónimo, pruebas de carreras con PostgreSQL 17, aislamiento
de sesiones, fallos de entrega y transacción, enlaces de otra finalidad y estados de
cuenta. Upgrade vacío/existente, rechazo de colisiones sin alteración, downgrade y
backup/restore comprobados en bases desechables; preservación de módulos/listas.

Operación documentada para desplegar API/frontend/worker juntos, rotar secretos,
retener/purgar correo y credenciales, recuperar ADMIN y responder a incidentes.
Regresión electoral conservada: padrón ausente permite guardar con observación;
envío/solo lectura, permisos, reportes y descargas siguen cubiertos.

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
