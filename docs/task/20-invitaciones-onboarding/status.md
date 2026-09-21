# Task 20 — Estado

- Estado: **Planificada — pendiente de implementación**.
- Fecha de planificación: 20/09/2026.
- Rama prevista: `develop`.
- Dependencias: 16, 17, 18, 19, 05.
- [Consigna y checklist](task.md) · [Plan común](../LOGIN_SEGURIDAD.md).

## Estado auditado

El alta actual crea APODERADO activo con contraseña definida por ADMIN. Username/full_name/password_hash son obligatorios. La nueva invitación requiere diseñar migración y no crear usuarios ficticios para satisfacer esos campos.

## Seguimiento

- [ ] Auditar dependencias al iniciar ejecución y fijar contrato técnico.
- [ ] Implementar mini tasks y migraciones aplicables.
- [ ] Verificar seguridad, concurrencia, permisos y experiencia por rol.
- [ ] Documentar evidencia local y habilitación externa por separado.
- [ ] Crear report.md al ejecutar y actualizar índice/matriz.

## Evidencia y dependencias

Esta planificación no incorpora código, migraciones, envíos ni tests nuevos.
No hay evidencia de implementación de esta task. SMTP externo requiere proveedor,
remitente/dominio y URL HTTPS configurados; el capturador permite desarrollo local.
Las decisiones propuestas están en LOGIN_SEGURIDAD.md y DECISIONES.md, D12–D16.
