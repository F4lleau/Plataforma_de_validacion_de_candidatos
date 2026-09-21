# TASK 18 — Login Throttling, Account Lockout and Administrative Unlock

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado: implementación local completada el 21/09/2026; límites externos en status/report.**

**Dependencias:** Tasks 16, 17, 05, 14.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-03, AUTH-04; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Limitar intentos de autenticación, bloquear temporalmente por fallos y permitir desbloqueo administrativo auditado sin confundir bloqueo con desactivación.

**Punto de partida auditado:** Login solo valida email, hash y is_active. No hay contadores/locked_until ni rate limiting. La gestión ADMIN actual se limita a apoderados.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [x] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [x] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. POLÍTICA Y ESTADO
==================================================

- [x] Modelar ventana/intentos fallidos/locked_until separados de is_active y del estado de invitación; persistencia compartida, UTC y operaciones atómicas.
- [x] Usar parámetros iniciales propuestos en LOGIN_SEGURIDAD.md: 5 fallos en 15 minutos, bloqueo de 15 minutos. Configurarlos y documentar que no son umbrales impuestos por OWASP.
- [x] No extender indefinidamente el bloqueo con solicitudes recibidas mientras está bloqueada. Expiración del bloqueo o login válido fuera de bloqueo reinicia contadores según política.
- [x] Definir bloqueo temporal como impedimento para nuevos login; sesiones existentes conservan vigencia salvo revocación explícita para evitar expulsión inducida por terceros. Desactivación sí revoca todas.

==================================================
## 3. LIMITACIÓN Y RESPUESTAS
==================================================

- [x] Combinar límites por identificador normalizado y origen IP con estado compartido entre workers; aplicar cuotas también a identificadores inexistentes y documentar proxies confiables.
- [x] Evitar enumeración por mensajes, códigos, Retry-After o caminos rápidos de hash. No revelar en login público si la cuenta existe, está bloqueada o desactivada.
- [x] Diferenciar fallos de infraestructura de fallos de credenciales para no sumar intentos por caída de BD o timeout interno.
- [x] Aplicar una política consistente de 429 para límites de petición sin publicar contadores de cuentas; no usar un contador en memoria del proceso como protección final.

==================================================
## 4. DESBLOQUEO ADMIN
==================================================

- [x] Agregar listado/filtros de cuentas bloqueadas con motivo técnico, vencimiento e intentos para ADMIN, sin hashes ni tokens.
- [x] Implementar POST /admin/users/{id}/unlock con motivo obligatorio, reautenticación reciente y auditoría de actor/fecha/antes/después; operación idempotente y atómica.
- [x] Permitir que un ADMIN activo desbloquee otro ADMIN o APODERADO bloqueado; esta acción no cambia rol, is_active, módulos, contraseña ni invitaciones. Mantener el CRUD de apoderados acotado.
- [x] En la UI diferenciar activa, bloqueada temporalmente y desactivada; confirmación accesible y notificación por correo con límites de frecuencia.
- [x] Representar invitación pendiente cuando Task 20 incorpore su modelo (dependencia posterior explícita; no hay cuentas invitadas ficticias).
- [x] Documentar recuperación operativa si todos los ADMIN quedan sin acceso: procedimiento excepcional autenticado en servidor, auditado, sin endpoint público ni contraseña universal.

==================================================
## 5. TESTS Y PRUEBA MANUAL
==================================================

- [x] Probar umbral, límites de ventana, expiración, login válido, fallos simultáneos e intentos durante bloqueo con reloj controlado.
- [x] Probar ADMIN desbloquea, APODERADO/anónimo no; desbloqueo repetido y carrera con fallo nuevo; cuenta desactivada permanece sin acceso.
- [x] Probar múltiples workers, email con variaciones de normalización, ataque desde varias IP e IP compartida sin contar cada usuario como una cuenta única.
- [x] Comprobar que no hay enumeración obvia por respuesta/código y que cada transición efectiva registra auditoría.

==================================================
## 6. VERIFICACIÓN
==================================================

- [x] Mantener endpoint → service → repository → model; permisos y validaciones en backend.
- [x] Ejecutar `python -m pytest -q` desde backend; verificar `alembic current`, `alembic heads` y migraciones aplicables en bases desechables vacía/existente; no sustituirlas por create_all.
- [x] Ejecutar `npm run test`, `npm run build` y `npm run lint` desde frontend.
- [x] Verificar en navegador los flujos afectados y permisos por API; registrar evidencia sin emails reales, tokens, cookies o contraseñas.
- [x] Ejecutar `git diff --check` y revisar secretos/archivos temporales antes de cerrar.

==================================================
## 7. DOCUMENTACIÓN E INFORME FINAL
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

Dependencia posterior resuelta en Task 20: invitaciones pendientes en Apoderados,
con enlace desde Seguridad; no se inventan cuentas antes de aceptar.
