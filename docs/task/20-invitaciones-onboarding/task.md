# TASK 20 — Email Invitations, Single-Use Activation and First-Access Onboarding

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado inicial: planificada; no implementada por esta consigna.**

**Dependencias:** Tasks 16, 17, 18, 19, 05.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-07, AUTH-08; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Permitir que ADMIN invite apoderados por correo y que cada destinatario complete sus datos y cree su contraseña inicial al aceptar un enlace único.

**Punto de partida auditado:** El alta actual crea APODERADO activo con contraseña definida por ADMIN. Username/full_name/password_hash son obligatorios. La nueva invitación requiere diseñar migración y no crear usuarios ficticios para satisfacer esos campos.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [ ] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [ ] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [ ] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. INVITACIONES Y ALCANCE
==================================================

- [ ] Modelar invitación separada del usuario con email normalizado, invitador, rol APODERADO, módulos propuestos, digest, vencimiento, estados y auditoría; restricción de duplicados/concurrencia.
- [ ] Fijar como alcance inicial invitaciones a APODERADO, coherente con /users actual. No permitir que el invitado elija ADMIN ni ampliar alta de administradores sin task explícita.
- [ ] Implementar creación, listado, reenvío y cancelación exclusivos ADMIN. No enviar contraseña inicial ni devolver enlace/token en la respuesta de administración.
- [ ] Propuesta de vigencia 48 horas; reenviar genera token nuevo y revoca el anterior. Cooldown/cuotas para evitar spam; cancelar invalida aceptación y mensajes pendientes.
- [ ] Tratar cuenta existente/pending/expirada/cancelada/aceptada sin duplicar ni sobreescribir perfiles. Si existe usuario, derivar al flujo de gestión/recuperación según su estado.

==================================================
## 3. ACEPTACIÓN Y PRIMER ACCESO
==================================================

- [ ] Agregar página pública de invitación que presente contexto mínimo al poseedor del token y permita ingresar nombre completo, username si sigue requerido y contraseña/confirmación.
- [ ] Fijar el email al destino de la invitación, sin sustitución desde el cliente. No pedir DNI, domicilio u otros datos del candidato para crear una cuenta operativa.
- [ ] GET de enlace no consume, activa ni crea sesión; validar token por POST y completar aceptación solo con envío explícito del formulario.
- [ ] Consumir token, crear usuario con hash seguro y email verificado, aplicar módulos autorizados vigentes y registrar auditoría en una transacción; resolver dos aceptaciones/reenvío/cancelación concurrentes.
- [ ] Revalidar invitador activo ADMIN y módulos/catálogos vigentes al aceptar; si perdió autorización, impedir activación y requerir nueva invitación de un ADMIN vigente.
- [ ] No autoasignar listas por municipio ni por módulos. Mantener módulo más asignación explícita por lista y mínimo privilegio.
- [ ] Tras completar datos y clave mostrar confirmación y enviar a login; validar acceso por rol. Un enlace abierto con otra sesión no cambia silenciosamente esa identidad.

==================================================
## 4. FRONTEND ADMIN Y MIGRACIÓN
==================================================

- [ ] Adaptar Apoderados con pestaña/listado de invitaciones, estados, vencimiento, reenvío/cancelación y feedback de cola/SMTP; solo datos autorizados.
- [ ] Reemplazar el alta manual con contraseña por invitación, también en backend, sin dejar un endpoint alternativo que eluda la aceptación.
- [ ] Conservar usuarios, roles, listas y asignaciones existentes. Distinguir cuentas legacy sin verificación histórica de email; no marcar email_verified solo por migrarlas ni bloquearlas masivamente.
- [ ] Planificar conflicto de emails normalizados antes de imponer índice único; no fusionar cuentas ni sobrescribir datos automáticamente.
- [ ] Agregar perfil/seguridad accesible desde la sesión para consultar datos y cambiar contraseña. El cambio de email y elevación de rol quedan fuera; no abrir edición sin verificación.

==================================================
## 5. TESTS Y PRUEBA MANUAL
==================================================

- [ ] ADMIN invita, mail llega al capturador, destinatario completa datos, inicia sesión y ve solo sus módulos/listas autorizadas.
- [ ] Probar expirado/usado/cancelado/reenvío, dos aceptaciones simultáneas, caída de transacción y caída SMTP; no quedan cuentas activas a medio crear.
- [ ] Probar cambio de email/rol/módulos en request, API directa por APODERADO, token de otra finalidad e invitador desactivado antes de aceptar.
- [ ] Verificar scanners de mail, link abierto dos veces, otra sesión activa, móviles, navegación atrás y ausencia de token en analítica/logs.

==================================================
## 6. VERIFICACIÓN
==================================================

- [ ] Mantener endpoint → service → repository → model; permisos y validaciones en backend.
- [ ] Ejecutar `python -m pytest -q` desde backend; verificar `alembic current`, `alembic heads` y migraciones aplicables en bases desechables vacía/existente; no sustituirlas por create_all.
- [ ] Ejecutar `npm run test`, `npm run build` y `npm run lint` desde frontend.
- [ ] Verificar en navegador los flujos afectados y permisos por API; registrar evidencia sin emails reales, tokens, cookies o contraseñas.
- [ ] Ejecutar `git diff --check` y revisar secretos/archivos temporales antes de cerrar.

==================================================
## 7. DOCUMENTACIÓN E INFORME FINAL
==================================================

- [ ] Actualizar documentación de setup, contratos, variables, permisos y límites realmente implementados.
- [ ] Crear `report.md` con archivos/modelos/migraciones, decisiones, resultados de tests, prueba manual y pendientes; registrar git status/diff.
- [ ] Actualizar checklist, `status.md`, índice, matriz AUTH y decisiones; diferenciar capturador/mock de integración SMTP externa.
- [ ] No hacer commit/push salvo instrucción del usuario; no modificar reglas electorales fuera del alcance.

## Dependencias externas

Proveedor SMTP, remitente autorizado y origen HTTPS real se necesitan para entrega
externa; los escenarios locales usan capturador SMTP. No solicitar credenciales en
texto ni bloquear el trabajo local por falta de proveedor. Ver plan común.

## Definición de done

- [ ] Mini tasks implementadas y verificadas; pendientes externos explícitos, sin presentar placeholders como funcionalidad real.
- [ ] Regla electoral crítica conservada: ausencia en padrón permite guardar con observación.
- [ ] Usuarios/asignaciones existentes preservados; ninguna escalada de rol ni filtración de secretos.
- [ ] Documentación e informe consistentes con el código; sin cambios funcionales ajenos.
