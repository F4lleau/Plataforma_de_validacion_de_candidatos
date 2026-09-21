# Task 18 — Estado

- Estado: **Planificada — pendiente de implementación**.
- Fecha de planificación: 20/09/2026.
- Rama prevista: `develop`.
- Dependencias: 16, 17, 05, 14.
- [Consigna y checklist](task.md) · [Plan común](../LOGIN_SEGURIDAD.md).

## Estado auditado

Login solo valida email, hash y is_active. No hay contadores/locked_until ni rate limiting. La gestión ADMIN actual se limita a apoderados.

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
