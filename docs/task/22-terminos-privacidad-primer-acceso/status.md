# Task 22 — Estado

> Estado vigente al 22/09/2026: RENAPER retirado del alcance; sus menciones como pendiente más abajo describen el cierre histórico. Ver [retiro](../RETIRO_RENAPER.md).

- Estado: **Completada en alcance local; textos definitivos pendientes**.
- Fecha: 21/09/2026. Rama: `develop`. Sin commit/push.
- [Checklist](task.md) · [Informe y evidencia](report.md).

## Implementación

- [x] Auditoría del login, invitaciones, sesión, permisos y footer existentes.
- [x] Migración aditiva `b8316d72c4ef` aplicada localmente y verificada con Alembic.
- [x] Aceptación única por cuenta, fecha UTC/versión/instantánea y auditoría atómica.
- [x] Restricción central en backend, estado de perfil y control de rutas frontend.
- [x] Aviso bajo botón de login, checkbox explícito, errores/reintentos y salida.
- [x] Modales compartidos, contenido provisorio, lectura pública y footer por rol.
- [x] Concurrencia PostgreSQL, migración/reversión, regresión de auth/electoral.
- [x] Recorrido navegador móvil/escritorio, foco, Escape, red y formularios conservados.
- [x] Contratos, operación, manuales, índice y matriz AUTH actualizados.

## Decisiones ejecutadas

ADMIN y APODERADO sin evidencia aceptan antes de habilitar módulos, también al
restaurar sesiones existentes. No se fabricó aceptación para cuentas anteriores.
Políticas se consultan sin checkbox adicional. La primera aceptación persiste
entre dispositivos, logout, cambios/reset de clave y desbloqueo. Actualizar el texto
no exige reaceptación. Un documento modificado durante la primera confirmación
produce conflicto y requiere confirmar nuevamente la versión servida.

## Pendiente externo

Revisión institucional y textos definitivos antes de producción. Los borradores
están identificados como provisorios para pruebas. No se afirma cumplimiento legal
ni consentimiento de personas incluidas en el padrón. RENAPER, SMTP externo y las
reglas electorales oficiales conservan sus pendientes anteriores.
