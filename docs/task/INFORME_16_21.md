# Autenticación 16–21 — aceptación local y operación

Fecha: 21/09/2026. Rama: `develop`. Sin commit/push por esta ejecución.
Se conservan los cambios previos de Tasks 16–19; este informe amplía su
[evidencia histórica](INFORME_16_19.md), sin sustituir la aceptación electoral de Task 15.

## Resultado y alcance

JWT con sesiones revocables, renovación rotativa HttpOnly/CSRF, Argon2id y bcrypt
legacy, bloqueo/desbloqueo, recuperación/cambio e invitaciones están implementados
localmente. Mailpit captura correo real por SMTP local. **Producción no está habilitada**:
proveedor/remitente/dominio, HTTPS real y entrega externa autorizada siguen pendientes.
No hay integración RENAPER real ni confirmación institucional de plantillas de prueba.

Task 20 agrega invitaciones separadas de User, digest de un uso, 48 horas,
creación/listado/reenvío/cancelación ADMIN con reautenticación, cuotas y auditoría.
El primer acceso crea perfil/clave, marca email verificado y aplica módulos vigentes;
no asigna listas ni inicia sesión. POST /users ya no crea cuentas; PUT no permite
cambio de email ni contraseña ajena. Cuentas legacy conservan acceso y verificación NULL.

Task 21 verifica roles, estados, sesiones, correo y migraciones con pruebas negativas,
concurrencia real en PostgreSQL y recorrido en navegador. No hay certificación NIST/ASVS.

## Matriz de aceptación

| Operación / estado | Anónimo | APODERADO | ADMIN | Evidencia |
| --- | --- | --- | --- | --- |
| Login activo/legacy | Credenciales válidas; error genérico al fallar | Rol real desde BD | Rol real desde BD | auth_rbac, security_16_19 |
| Login inactivo/bloqueado | Rechazado; bloqueo temporal no extiende por ataques | Sesión previa no se revoca por fallos | Desbloqueo no reactiva | security_16_19; circuito API local |
| Refresh/logout | Cookie + CSRF; replay revoca familia | Solo sesión propia | Solo sesión propia | security_16_19, security_postgres |
| Ver/revocar sesiones, cambio | 401 | Propias; cambio con clave actual | Propias; cierre global con reauth | security_16_19; frontend |
| Desbloqueo y recuperación ADMIN | 401 | 403 | Reauth + motivo cuando corresponde | security_16_19; circuito local |
| Forgot/reset | Respuesta genérica; enlace válido, sin login automático | Revoca sesiones y claves anteriores | Igual política | security_16_19, security_postgres; Mailpit/navegador |
| Crear/listar/reenviar/cancelar invitación | 401 | 403 | Reauth, CSRF, cuotas, paginación | invitations_20_21 |
| Invitación pendiente | Inspección no consume; aún no hay usuario | Otra sesión se conserva | Otra sesión se conserva | API y navegador móvil |
| Aceptar vencida/cancelada/usada | Rechazado | Sin privilegios adicionales | No elude token | invitations_20_21 |
| Manipular rol/email/módulos | 422 | 422/403 según ruta | El alta solo permite APODERADO | invitations_20_21 |
| Cuenta existente/inactiva | No sobrescribe ni reactiva | Gestión/recuperación | Conflicto 409 | invitations_20_21 |
| Invitador inactivo/sin rol, catálogo/reglas inactivos | No activa cuenta | Sin permisos nuevos | Debe emitir invitación vigente | invitations_20_21 |
| Módulo sin lista asignada | 401 | No ve lista ajena | Administración mantiene alcance | tasks_04_09, invitations_20_21 |
| Correo caído/duplicación potencial | No crea usuario incompleto | Estado de dominio se conserva | Cola/retry observable | security_16_19, invitations_20_21 |

Las rutas de pruebas se encuentran bajo `backend/tests/` y `frontend/src/tests/`.

## Pruebas automatizadas

- Backend completo con `SECURITY_POSTGRES_TESTS=1 .venv/bin/python -m pytest -q`:
  **167 aprobadas**, sin skips en esa ejecución. Advertencias heredadas por
  `datetime.utcnow`; no cambian el resultado.
- Después del ajuste de orden global de bloqueos de catálogos, se repitieron
  invitaciones y PostgreSQL: **27 aprobadas**.
- Frontend: **17 aprobadas**; build y ESLint correctos. Aviso de Browserslist sobre
  su dataset antiguo, sin fallo de compilación.
- `alembic current/heads`: `a72e903d418f`; `alembic check`: sin diferencias.
- `git diff --check`: sin errores; entornos reales ignorados y ejemplos versionables.

PostgreSQL 17 aislado: diez tests con bases aleatorias migradas por Alembic, eliminadas
al terminar. Se comprueban doble refresh, doble reset, contadores concurrentes y dos
consumidores de correo; doble aceptación, aceptación contra resend/cancel y altas
simultáneas por dos ADMIN para un mismo correo. No quedan cuentas a medio crear.

Upgrade vacío/existente, downgrade/upgrade, colisiones normalizadas y conservación de
cuenta/módulo/asignación se comprueban sin fusionar datos. La prueba de backup crea
`pg_dump -Fc` y restaura con `pg_restore` tras downgrade, recuperando invitación y cuenta.
Solo utiliza su base desechable, no la base de trabajo. En SQLite se prueban unidades;
no sustituye la evidencia PostgreSQL de carreras/migraciones.

Los tests electorales siguen verificando guardado con observación por ausencia en
padrón, módulos/asignaciones, envío atómico, lectura posterior, reportes y descargas.
El cliente prueba renovación durante JSON/upload/download, rechazo de MIME incorrecto,
pérdida de red sin repetición automática de escrituras y respuestas obsoletas de sesión.

## Recorrido local

ADMIN → Apoderados → Invitaciones → correo sintético + módulo → Mailpit SMTP →
`/invitacion` → nombre/usuario/contraseña → confirmación → cierre explícito de la
sesión anterior → login APODERADO. Se comprobó módulo provincial y ausencia de listas
asignadas, perfil y email verificado. El secreto desaparece de la URL, sin localStorage
ni cookies accesibles desde JavaScript; otra sesión no cambia de identidad al aceptar.

El recorrido de recuperación usa esa cuenta: cinco intentos fallidos, bloqueo,
desbloqueo ADMIN con reautenticación/motivo, login y forgot, Mailpit y reset en navegador.
Se verifica rechazo de clave, JWT y refresh anteriores, enlace consumido y logout efectivo.
El reset cierra también la otra pestaña; navegar atrás tras logout no restaura la sesión.
Una falla de red simulada al cerrar una sesión muestra feedback y conserva el perfil;
al restablecer la red, el cierre funciona. Reabrir la invitación consumida muestra rechazo.

La interfaz se revisa en escritorio y móvil de 390×844, sin desborde horizontal,
con controles etiquetados, autocompletado de gestores de claves y foco de teclado.
Capturas en `/tmp/task2021-*.png`, fuera de Git, sin tokens ni contraseñas. Los scripts,
cuenta y cuatro correos sintéticos fueron eliminados tras la prueba; no se versiona un seed.
No se detectaron errores JavaScript en el recorrido.

## Cambios y operación

- Migración nueva `a72e903d418f_invitations_verified_email.py`, posterior a `6cb192ebc9fe`.
- `models/invitation.py`, `schemas/invitation.py`, repository/service/endpoints dedicados.
- Extensión de User/Outbox, comprobación de generación en worker y retención de invitaciones.
- Frontend `InvitationsAdmin`, `InvitationAccept`, editor de apoderados y perfil de seguridad;
  captura de fragmentos específica por ruta para no mezclar recuperación e invitación.
- `.env.example`: vigencia/cuota de invitaciones; infraestructura Mailpit de Task 17 reutilizada.
- Manuales, contratos, operación, decisiones e índices de tasks actualizados.

Ver [AUTH_OPERATIONS](../AUTH_OPERATIONS.md) para despliegue coordinado API/frontend/worker,
backup/rollback, colisiones, retención, monitoreo de cola/bloqueos, rotación de secretos
y recuperación del operador. La auditoría electoral se conserva.

## Habilitación externa pendiente

- SMTP autorizado, dominio/remitente, SPF/DKIM/DMARC y destinatario de aceptación externo.
- HTTPS real, cookie Secure, CORS/proxy y no-store/no-referrer en hosting/proxy productivo.
- Gestión de secretos y prueba de recuperación en infraestructura de destino.
- Evaluación de MFA para ADMIN antes de uso sensible; MFA/passkeys/SSO son ampliaciones.

SMTP aceptado no significa entregado; una caída después de aceptación antes del commit
puede repetir el mismo mensaje, sin renovar enlace. Link perdido al recargar se reabre
desde correo. Cambiar email requiere otro flujo de verificación; no se habilita aquí.
La política técnica y los datos de prueba no constituyen reglas electorales oficiales.
