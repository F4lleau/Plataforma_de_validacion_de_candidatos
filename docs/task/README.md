# Tareas del proyecto

Esta carpeta se incluye en Git por pedido del usuario. Contiene las consignas,
checklists y seguimiento; no debe contener secretos, padrones reales ni datos personales
de las capturas del manual. No se hace commit ni push sin indicación.

## Índice y orden de ejecución

Tasks 03–08 implementadas; 04/06/07/08 usan reglas y datos de prueba autorizados.
Task 09 fue retirada del alcance el 22/09/2026: RENAPER deja de ser una dependencia
y sus resultados granulares locales continúan en Task 08. Ver [retiro](RETIRO_RENAPER.md). Tasks 10–14 están implementadas en el alcance local; Task 15 completó aceptación
local y mantiene pendiente la institucional. Ver [informe 04–09](INFORME_04_09.md) y
[informe 10–15](INFORME_10_15.md).

| Orden | Task | Estado | Dependencias | Documentos |
| --- | --- | --- | --- | --- |
| 03 | Authentication, RBAC and Role-Based Frontend | Completada | Base Task 02B | [Consigna con checklist](03-authentication-rbac/task.md) · [Original](03-authentication-rbac/task-original.txt) · [Estado](03-authentication-rbac/status.md) · [Informe](03-authentication-rbac/report.md) |
| 04 | Election Configuration, Catalogs and Validation Rules | Completada (alcance de prueba) | 03 | [Task](04-configuracion-electoral/task.md) · [Estado](04-configuracion-electoral/status.md) |
| 05 | Apoderado Management, Assignments and Account Access | Completada | 03, 04 | [Task](05-apoderados-asignaciones/task.md) · [Estado](05-apoderados-asignaciones/status.md) |
| 06 | Official Membership Register Import, Search and History | Completada (alcance de prueba) | 03, 04 | [Task](06-padron-oficial/task.md) · [Estado](06-padron-oficial/status.md) |
| 07 | Electoral Lists, Templates and Assigned Ownership | Completada (alcance de prueba) | 04, 05 | [Task](07-listas-plantillas/task.md) · [Estado](07-listas-plantillas/status.md) |
| 08 | Candidate Drafts, Editing and Office Requirements | Completada (alcance de prueba) | 06, 07 | [Task](08-candidatos-requisitos/task.md) · [Estado](08-candidatos-requisitos/status.md) |
| 09 | RENAPER Integration and Candidate Validation Results | Retirada por el usuario (22/09/2026) | — | [Task](09-renaper-validacion-identidad/task.md) · [Estado](09-renaper-validacion-identidad/status.md) |
| 10 | List Composition, Submission and Automatic Approval | Completada en entorno de prueba; habilitación institucional pendiente | 07, 08 | [Task](10-composicion-envio-aprobacion/task.md) · [Estado](10-composicion-envio-aprobacion/status.md) |
| 11 | Administrative List Inbox and Granular Validation Review | Completada | 07, 08, 10 | [Task](11-bandeja-administrativa-validaciones/task.md) · [Estado](11-bandeja-administrativa-validaciones/status.md) |
| 12 | Role-Based Dashboards and Live Electoral Metrics | Completada | 05, 07, 10, 11 | [Task](12-dashboards-por-rol/task.md) · [Estado](12-dashboards-por-rol/status.md) |
| 13 | Reports, Statistics and Excel CSV PDF Exports | Completada | 06, 11, 12 | [Task](13-reportes-exportaciones/task.md) · [Estado](13-reportes-exportaciones/status.md) |
| 14 | Audit Trail and Electoral Action History | Completada | 04, 05, 06, 07, 08, 10, 11, 13 | [Task](14-auditoria-historial/task.md) · [Estado](14-auditoria-historial/status.md) |
| 15 | End-to-End Acceptance, Role Manuals and Support | Aceptación local completada; aceptación institucional pendiente | 03, 04, 05, 06, 07, 08, 10, 11, 12, 13, 14 | [Task](15-aceptacion-manual-soporte/task.md) · [Estado](15-aceptacion-manual-soporte/status.md) |
| 16 | JWT Hardening, Session Rotation and Revocation | Completada localmente | 03, 14 | [Task](16-jwt-sesiones-seguras/task.md) · [Estado](16-jwt-sesiones-seguras/status.md) |
| 17 | SMTP Delivery, Email Templates and Local Mail Capture | Completada localmente | 16, 14 | [Task](17-smtp-correo-transaccional/task.md) · [Estado](17-smtp-correo-transaccional/status.md) |
| 18 | Login Throttling, Account Lockout and Administrative Unlock | Completada localmente | 16, 17, 05, 14 | [Task](18-bloqueo-desbloqueo-cuentas/task.md) · [Estado](18-bloqueo-desbloqueo-cuentas/status.md) |
| 19 | Password Recovery, Password Changes and Credential Policy | Completada localmente | 16, 17, 18 | [Task](19-recuperacion-cambio-clave/task.md) · [Estado](19-recuperacion-cambio-clave/status.md) |
| 20 | Email Invitations, Single-Use Activation and First-Access Onboarding | Completada localmente | 16, 17, 18, 19, 05 | [Task](20-invitaciones-onboarding/task.md) · [Estado](20-invitaciones-onboarding/status.md) |
| 21 | Authentication Acceptance, Security Regression and Operations | Aceptación local completa; producción pendiente | 16, 17, 18, 19, 20 | [Task](21-aceptacion-seguridad-login/task.md) · [Estado](21-aceptacion-seguridad-login/status.md) |
| 22 | First-Login Terms Acceptance and Privacy Documents | Completada localmente; textos definitivos pendientes | 16, 20, 21, 14 | [Task](22-terminos-privacidad-primer-acceso/task.md) · [Estado](22-terminos-privacidad-primer-acceso/status.md) · [Informe](22-terminos-privacidad-primer-acceso/report.md) |
| 23 | Admin Panel and Electoral Configuration UX Improvement | Implementación parcial avanzada | 04, 05, 14, 18, 21, 22 | [Task](23-mejora-panel-admin-configuracion/task.md) · [Estado](23-mejora-panel-admin-configuracion/status.md) · [Informe parcial](23-mejora-panel-admin-configuracion/report.md) |

Tasks 16–19 implementadas y verificadas localmente; SMTP externo pendiente. Task 18
incorpora el estado de invitación desde Task 20. Tasks 20–21 verificadas localmente. Ver
[informe 16–19](INFORME_16_19.md) y [arquitectura/orden](LOGIN_SEGURIDAD.md).

**Task 22 implementada localmente:** aceptación única de términos antes del ingreso
y consulta de términos/privacidad mediante modales desde login y footer. Los textos
provisorios requieren revisión institucional antes de producción.

**Task 23 en implementación parcial:** mejora de panel ADMIN y Configuración con
submenú de cargos, proceso electoral y localidades habilitadas, sistema visual global
para botones/enlaces y limpieza de información técnica visible para usuarios finales.

## Fuente, cobertura y decisiones

- [Fuente del manual](FUENTE_MANUAL.md): documento, hash, páginas revisadas y límites de interpretación.
- [Matriz de capacidades](CAPACIDADES.md): 26 capacidades trazadas al manual y al estado actual del repo.
- [Decisiones pendientes](DECISIONES.md): contradicciones, reglas no definidas y acceso externo.
- [Plan de login y seguridad](LOGIN_SEGURIDAD.md): brechas actuales, política propuesta, contratos y matriz AUTH.
- [Resumen de planificación](PLANIFICACION.md): alcance documental y verificación de los archivos.

## Forma de trabajo

1. Leer la consigna y requisitos de las dependencias; auditar código antes de modificarlo.
2. Mantener `task.md` con checklist por mini task y `status.md` con estado y bloqueos concretos.
3. Marcar `[x]` solo con implementación/evidencia verificadas. Una decisión, mock o placeholder no completa una función real.
4. Si una mini task depende de datos/definiciones externas, mantenerla pendiente y avanzar con las partes independientes.
5. Registrar decisiones en `DECISIONES.md` y cambios de alcance en el seguimiento; conservar originales recibidos cuando se normalice su formato.
6. Cerrar cada task con `report.md`: archivos, endpoints/modelos, permisos, tests, prueba manual, pendientes, git status y diff.
7. Actualizar este índice y la matriz de capacidades al cerrar; no ejecutar el trabajo siguiente solo por haber redactado su consigna.
8. Mantener las tasks y documentación versionadas; secretos/.env, datos reales y scripts de seed temporales quedan fuera.
9. No hacer commit ni push sin indicación del usuario.

## Notas de dependencias

- Tasks 10–15 ejecutadas localmente. Pendientes externos: reglas oficiales y aceptación institucional.
- Task 09 retirada: no se requiere proveedor/API RENAPER para completar el sistema.
- Tasks 08/10/11/13/15 conservan afiliación, requisitos, composición, revisión y reportes.
- Los informes y capturas anteriores son históricos; [RETIRO_RENAPER.md](RETIRO_RENAPER.md) describe el alcance vigente y la conservación de datos.
- Auditoría se instrumenta desde Task 04 y en cada operación de dominio; Task 14 completa consulta/historial, no reconstruye acciones nunca registradas.
- Las declaraciones históricas de Task 03 sobre carpeta ignorada describen el cierre anterior. Este índice refleja la decisión actual de versionarla.

[Informe consolidado 16–21 y habilitación externa pendiente](INFORME_16_21.md).
