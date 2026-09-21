# TASK 17 — SMTP Delivery, Email Templates and Local Mail Capture

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado inicial: planificada; no implementada por esta consigna.**

**Dependencias:** Tasks 16, 14.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-02; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Crear infraestructura de correo transaccional verificable localmente y configurable para SMTP real, reutilizable por recuperación e invitaciones.

**Punto de partida auditado:** No hay integración SMTP ni cola de correo. SUPPORT_CONTACT es solo informativo. local-deps.yml contiene PostgreSQL.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [ ] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [ ] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [ ] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. CONFIGURACIÓN Y CAPTURA LOCAL
==================================================

- [ ] Definir SMTP_HOST/PORT/USERNAME/PASSWORD, remitente, TLS, timeout y URL pública canónica desde entorno; .env.example sin secretos y validación estricta en producción.
- [ ] Agregar capturador SMTP local a local-deps.yml (propuesta Mailpit), puertos solo en loopback, healthcheck y guía de inspección. El modo local no entrega correos externos.
- [ ] Implementar adapter SMTP con verificación TLS; probar credenciales inválidas, certificado inválido, timeout y proveedor no configurado sin degradar silenciosamente a texto plano.
- [ ] Documentar remitente/dominio autorizados y evidencia de SPF, DKIM y DMARC para habilitación real; no afirmar entregabilidad por una captura local.

==================================================
## 3. OUTBOX Y WORKER
==================================================

- [ ] Crear outbox y worker persistentes con migraciones, estados pending/processing/sent/failed, intentos, próximo intento y errores sanitizados.
- [ ] Guardar evento de dominio y envío pendiente en una misma transacción; procesar solo después del commit. No depender únicamente de BackgroundTasks en memoria.
- [ ] Implementar reclamo atómico, lease/recovery tras caída, backoff y máximo de reintentos; no reintentar errores permanentes indefinidamente.
- [ ] Usar deduplicación por evento y verificar vigencia antes de enviar; un reintento de transporte no genera otro token. Documentar que SMTP no garantiza entrega exactamente una vez.
- [ ] Proteger payloads que contienen enlaces secretos con cifrado autenticado y clave externa a BD, acceso mínimo y purga tras envío/expiración; las tablas de tokens conservan solo digest.
- [ ] Distinguir aceptado por SMTP de recibido por destinatario; observabilidad sin asunto/cuerpo sensible, URL completa ni credenciales.

==================================================
## 4. PLANTILLAS Y SEGURIDAD DE ENLACES
==================================================

- [ ] Crear HTML accesible y texto plano en español para invitación, recuperación, cambio de clave y desbloqueo; identidad Junta Electoral/PJ Chaco, vencimiento y canal de ayuda.
- [ ] Construir enlaces desde origen configurado, nunca Host/Forwarded no confiables. Escapar datos, impedir inyección de headers y rechazar destinatarios arbitrarios desde el cliente.
- [ ] Definir consumo del token mediante POST confirmado; abrir GET o previsualizar el mail no activa cuentas ni consume enlaces.
- [ ] Restringir acceso a vistas de correo/errores a operadores autorizados; no exponer cuerpos o enlaces en la API ADMIN.

==================================================
## 5. PRUEBAS Y OPERACIÓN
==================================================

- [ ] Verificar HTML/texto, caracteres españoles, enlaces canónicos y ausencia de contraseñas en los mensajes.
- [ ] Probar reinicio de worker, doble consumidor, caída entre envío y confirmación, reintentos y expiración/revocación antes del envío.
- [ ] Inspeccionar mails de prueba en capturador; solo enviar prueba externa a destinatario expresamente autorizado.
- [ ] Documentar arranque del worker, monitoreo, reintento operativo, retención y manejo de cola agotada. Separar aceptación local de habilitación SMTP real.

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
