# Task 20 — Estado

- Estado: **Completada en alcance local; producción pendiente de habilitación externa**.
- Fecha: 21/09/2026. Rama: `develop`. Sin commit/push.
- [Checklist](task.md) · [Informe](report.md) · [Matriz y evidencia](../INFORME_16_21.md).

## Auditoría y ejecución

Se preservaron los cambios no commiteados de Tasks 16–19 y los datos locales.
Las dependencias ya aportaban JWT/sesiones, CSRF, SMTP/outbox, bloqueo y reset.
El alta manual y falta de invitaciones eran las brechas: se sustituyeron con
invitación separada de User, perfil verificado, módulos vigentes y permiso mínimo.

- [x] Revisión de arquitectura, ramas, dependencias y amenazas.
- [x] API/UI, migración aditiva y documentación coherentes.
- [x] Permisos, estados, errores, concurrencia y correo local verificados.
- [x] Backend 167 tests; frontend 17, build/lint; Alembic y backup/restore.
- [x] Recorrido navegador/API/Mailpit con cuenta sintética y móviles.
- [x] Informe y matriz actualizados; entornos reales ignorados.

## Pendientes externos

SMTP autorizado, remitente/dominio, HTTPS real y recepción externa. Mailpit no
acredita entregabilidad productiva. MFA/passkeys/SSO y cambio de email están fuera
de este alcance; RENAPER y validación institucional electoral siguen pendientes.
