# TASK 16 — JWT Hardening, Session Rotation and Revocation

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado: implementación local completada el 21/09/2026; límites externos en status/report.**

**Dependencias:** Tasks 03, 14.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-01; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Reforzar el JWT existente y completar el ciclo de sesión con renovación, rotación, revocación y manejo seguro en navegador.

**Punto de partida auditado:** JWT HS256 y bcrypt actuales; access de 30 minutos; refresh emitido sin uso; logout solo local. Ver core/security.py, services/auth_service.py, auth.store.ts y services/api.ts.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [x] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [x] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. CONTRATO JWT Y CLAVES
==================================================

- [x] Definir el contrato de access JWT con sub, iss, aud, iat, exp, jti, sid y tipo explícito; validar tipos, vigencia, firma, emisor y audiencia; leeway pequeño documentado.
- [x] Fijar algoritmos permitidos en servidor; rechazar none, confusión de tipos/algoritmos y claves débiles. Elegir y documentar firma según el despliegue; HS256 no exige sustitución automática si solo firma/verifica la API.
- [x] Definir carga, rotación y retiro de claves desde secretos del entorno, con kid restringido al inventario local; no resolver URLs/claves arbitrarias del token.
- [x] Mantener autorización con usuario, rol y asignaciones actuales de BD. No incluir contraseñas, emails innecesarios ni datos electorales en JWT.

==================================================
## 3. SESIONES Y RENOVACIÓN
==================================================

- [x] Agregar sesiones y familias de refresh mediante Alembic: usuario, sid, digest de refresh, vencimiento absoluto/inactividad, generación y revocación; índices y limpieza programada.
- [x] Implementar login, refresh y logout transaccionales. Refresh opaco aleatorio, digest persistido, rotación por uso y revocación de la familia ante reutilización.
- [x] Consultar sesión vigente en cada request autenticada para revocación inmediata del access. Logout actual, logout global, desactivación y cambio/restablecimiento de clave deben invalidar las sesiones correspondientes.
- [x] Resolver dos refresh concurrentes con operación atómica y coordinación de pestañas; documentar reintentos de red sin crear ventanas de replay indefinidas.
- [x] Implementar reautenticación reciente en servidor con contraseña actual, comprobante ligado a sid/usuario, TTL corto y límites de intentos; reutilizar en acciones sensibles sin confiar en el frontend.
- [x] Agregar consulta de sesiones propias y cierre individual/global; no exponer tokens. ADMIN no adquiere capacidad de actuar como otro usuario.

==================================================
## 4. NAVEGADOR Y CSRF
==================================================

- [x] Retirar access_token de localStorage; access en memoria, refresh en cookie HttpOnly con Secure en producción, SameSite y Path explícitos; limitar excepción HTTP a desarrollo local.
- [x] Implementar protección CSRF en operaciones con cookie, incluido login, refresh y logout; validar origen autorizado y estrategia de token CSRF. CORS con orígenes exactos y credenciales, sin wildcard.
- [x] Restaurar sesión mediante refresh al abrir la app; una sola renovación coordinada para requests concurrentes; máximo un reintento, 403 no cierra sesión.
- [x] Adaptar JSON, upload y descarga al cliente compartido. Preservar protección frente a respuestas obsoletas tras logout y sincronizar pestañas sin persistir tokens.
- [x] Probar reenvío de requests con efectos: no repetir una escritura ya aplicada ni reintentar en bucle ante fallos de autenticación.

==================================================
## 5. MIGRACIÓN Y AUDITORÍA
==================================================

- [x] Planificar corte compatible de frontend/API y rechazo de JWT antiguos sin sid; eliminar tokens legacy del navegador y pedir login sin perder usuarios/listas.
- [x] Auditar creación/cierre/revocación/replay de sesiones sin token ni cookie; definir retención y limpieza de sesiones vencidas.
- [x] Preparar página de seguridad de cuenta con sesiones propias y cierre; confirmar acciones globales e informar el cierre efectivo.

==================================================
## 6. TESTS Y PRUEBA MANUAL
==================================================

- [x] Probar firma incorrecta, expirado, nbf futuro si existe, emisor/audiencia/tipo incorrectos, sid revocado y claims manipulados.
- [x] Probar refresh replay/concurrencia, logout actual/global, 401/403, usuario desactivado, cambio de rol y aislamiento entre usuarios.
- [x] Verificar cookies y CSRF desde origen no autorizado, recarga, varias pestañas, uploads/descargas y logout con requests en vuelo.
- [x] Comprobar que access y refresh no quedan en localStorage, URLs, logs o auditoría.

==================================================
## 7. VERIFICACIÓN
==================================================

- [x] Mantener endpoint → service → repository → model; permisos y validaciones en backend.
- [x] Ejecutar `python -m pytest -q` desde backend; verificar `alembic current`, `alembic heads` y migraciones aplicables en bases desechables vacía/existente; no sustituirlas por create_all.
- [x] Ejecutar `npm run test`, `npm run build` y `npm run lint` desde frontend.
- [x] Verificar en navegador los flujos afectados y permisos por API; registrar evidencia sin emails reales, tokens, cookies o contraseñas.
- [x] Ejecutar `git diff --check` y revisar secretos/archivos temporales antes de cerrar.

==================================================
## 8. DOCUMENTACIÓN E INFORME FINAL
==================================================

- [x] Actualizar documentación de setup, contratos, variables, permisos y límites realmente implementados.
- [x] Crear `report.md` con archivos/modelos/migraciones, decisiones, resultados de tests, prueba manual y pendientes; registrar git status/diff.
- [x] Actualizar checklist, `status.md`, índice, matriz AUTH y decisiones; diferenciar capturador/mock de integración SMTP externa.
- [x] No hacer commit/push salvo instrucción del usuario; no modificar reglas electorales fuera del alcance.

## Dependencias externas

Proveedor SMTP, remitente autorizado y origen HTTPS real se necesitan para entrega
externa; los escenarios locales usan capturador SMTP. No solicitar credenciales en
texto ni bloquear el trabajo local por falta de proveedor. Ver plan común.

## Definición de done

- [x] Mini tasks implementadas y verificadas; pendientes externos explícitos, sin presentar placeholders como funcionalidad real.
- [x] Regla electoral crítica conservada: ausencia en padrón permite guardar con observación.
- [x] Usuarios/asignaciones existentes preservados; ninguna escalada de rol ni filtración de secretos.
- [x] Documentación e informe consistentes con el código; sin cambios funcionales ajenos.
