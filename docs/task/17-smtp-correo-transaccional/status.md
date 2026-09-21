# Task 17 — Estado

- Estado: **Completada en alcance local; habilitación SMTP externa pendiente**.
- Fecha: 21/09/2026. Rama: `develop`. Sin commit/push.
- SMTP TLS configurable, Mailpit Docker, outbox cifrada transaccional y worker con lease/retry/purga. Aceptación de proveedor externo pendiente.
- [Checklist](task.md) · [Informe](report.md) · [Evidencia común](../INFORME_16_19.md).

## Verificación

- [x] Auditar login existente y preservar usuarios/asignaciones/datos electorales.
- [x] Implementar API, UI, migración y controles del alcance local.
- [x] Probar permisos, concurrencia y circuito real navegador/API/Mailpit.
- [x] Ejecutar suites backend/frontend, build, lint y migraciones Alembic.
- [x] Documentar variables, operación y límites; sin secretos ni seed versionados.

La conexión SMTP externa requiere proveedor/dominio/remitente/HTTPS y destinatario
autorizado. Invitaciones corresponden a Task 20 y aceptación integral adicional a 21.
