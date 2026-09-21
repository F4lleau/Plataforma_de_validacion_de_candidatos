# TASK 19 — Password Recovery, Password Changes and Credential Policy

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado inicial: planificada; no implementada por esta consigna.**

**Dependencias:** Tasks 16, 17, 18.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-05, AUTH-06; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Implementar recuperación por correo y cambio autenticado de contraseña con tokens de un uso, política de claves y revocación de sesiones.

**Punto de partida auditado:** Olvidé mi contraseña muestra ayuda asistida; ADMIN puede fijar una clave en save_user. Hash actual bcrypt y mínimo del alta de apoderados de 10 caracteres.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [ ] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [ ] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [ ] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. POLÍTICA DE CONTRASEÑAS
==================================================

- [ ] Crear servicio único de política para todas las altas, cambios, resets y onboarding: propuesta mínimo 15 y máximo 128 caracteres, espacios/Unicode, sin truncar ni exigir mezclas arbitrarias.
- [ ] Permitir gestores de contraseñas y pegar; cotejar claves comunes/comprometidas con una lista local mantenida, sin enviar contraseñas a servicios externos.
- [ ] Migrar nuevos hashes a Argon2id con parámetros medidos y biblioteca mantenida; verificar bcrypt legado y rehash al login válido sin pedir el texto de claves existentes.
- [ ] Documentar límites heredados de bcrypt y prueba con contraseñas largas/Unicode; no forzar cambios periódicos ni rechazar login legado solo por la nueva longitud.

==================================================
## 3. SOLICITUD Y TOKEN DE RECUPERACIÓN
==================================================

- [ ] Crear POST /auth/password/forgot con respuesta genérica y tiempo comparable exista o no cuenta; límites por IP/identificador y cooldown de reenvío.
- [ ] Emitir token opaco de 32 bytes aleatorios, guardar digest, propósito, usuario, expiración/consumo y versión de credenciales. Propuesta de validez 30 minutos.
- [ ] Guardar token y mail/outbox atómicamente; no cambiar cuenta ni revocar sesiones por mera solicitud. Una nueva solicitud no invalida un enlace vigente: consumo exitoso revoca todos los pendientes del usuario.
- [ ] No emitir reset para usuario desactivado o invitación no aceptada; responder genéricamente y conservar el flujo administrativo correspondiente.
- [ ] No registrar token/URL en logs/analítica; página dedicada sin terceros, Cache-Control no-store, Referrer-Policy no-referrer y limpieza del token de URL tras capturarlo de forma segura.

==================================================
## 4. CONSUMO, CAMBIO Y ADMINISTRACIÓN
==================================================

- [ ] Implementar POST /auth/password/reset: comprobar propósito, digest, vencimiento y estado; consumir una sola vez con update/lock transaccional incluso en solicitudes concurrentes.
- [ ] Actualizar hash, versión de credenciales, revocar todas las sesiones y tokens de reset pendientes y limpiar solo bloqueo temporal por reintentos; no reactivar cuenta deshabilitada.
- [ ] Tras reset exitoso enviar notificación y volver a login, sin login automático. Un fallo SMTP posterior no revierte una contraseña ya cambiada.
- [ ] Implementar POST /auth/password/change con sesión válida, contraseña actual/reautenticación, nueva clave distinta y notificación; revocar todas las sesiones y pedir nuevo login.
- [ ] Sustituir en ADMIN la asignación directa de contraseñas por envío de recuperación; validar también el endpoint legacy para impedir que permita omitir controles. Preparar su retirada coordinada.
- [ ] Agregar pantallas de solicitud, nueva clave, enlace inválido/vencido/usado y cambio desde seguridad de cuenta; mensajes accesibles y validación igual a backend.

==================================================
## 5. TESTS Y PRUEBA MANUAL
==================================================

- [ ] Probar existente/inexistente/inactivo, límites, expiración, uso repetido, dos consumos concurrentes y confusión reset/invitación/refresh.
- [ ] Probar recuperación estando temporalmente bloqueado, cuenta desactivada durante el flujo, fallo de envío y solicitudes repetidas sin invalidación maliciosa de enlace vigente.
- [ ] Comprobar que vieja contraseña, JWT copiado y refresh previo dejan de servir tras reset/cambio; nueva contraseña funciona y las otras cuentas no cambian.
- [ ] Probar política Unicode/larga/común, migración bcrypt, formulario móvil, gestores y token ausente en logs e historial tras limpieza.

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
