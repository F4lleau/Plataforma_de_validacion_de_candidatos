# TASK 21 — Authentication Acceptance, Security Regression and Operations

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado: completada en alcance local el 21/09/2026; habilitación productiva pendiente.**

**Dependencias:** Tasks 16, 17, 18, 19, 20.
**Fuente:** solicitud del usuario sobre login, SMTP, recuperación, bloqueo e invitaciones (20/09/2026); no atribuida al PDF electoral.
**Cobertura:** AUTH-09; ver [plan y contratos comunes](../LOGIN_SEGURIDAD.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md), D12–D16. Los valores propuestos son decisiones técnicas iniciales, no requisitos normativos confirmados.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`,
`docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`, `docs/AUTHENTICATION.md`,
las consignas/estados de dependencias y el plan común. Rutas desde raíz del repo.

==================================================
## OBJETIVO
==================================================

Cerrar la nueva autenticación con pruebas integrales, migración verificable y operación documentada, distinguiendo evidencia local de correo productivo.

**Punto de partida auditado:** Task 15 cubrió aceptación electoral local con login anterior. Este cierre debe agregar escenarios nuevos sin reemplazar su evidencia histórica.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; preservar cambios y datos ajenos.
- [x] Auditar código real de las dependencias y registrar brechas/contratos en `status.md`.
- [x] Revisar política común, amenazas, compatibilidad y dependencias externas de esta task; avanzar con las partes independientes.

==================================================
## 2. MATRIZ DE ACEPTACIÓN
==================================================

- [x] Construir matriz ADMIN/APODERADO/anónimo con login, refresh, logout, sesiones, bloqueo/desbloqueo, reset/cambio e invitación, positivos y negativos.
- [x] Probar todos los estados: activo, desactivado, bloqueado, invitado pendiente, enlace expirado/cancelado/consumido y cuenta legacy.
- [x] Cubrir CSRF, replay, enumeración, permisos, carreras y límites con PostgreSQL real aislado y varios workers; no cerrar solo con mocks.

==================================================
## 3. RECORRIDO E2E
==================================================

- [x] Ejecutar invitación → correo local → perfil/clave → login → acceso asignado → logout efectivo; capturar evidencia sanitizada.
- [x] Ejecutar fallos hasta bloqueo → desbloqueo ADMIN → login; luego forgot → mail → reset → rechazo de clave/JWT/refresh anteriores.
- [x] Probar varias pestañas, sesión expirada durante carga/descarga, pérdida de red y navegador móvil; no duplicar cambios electorales.
- [x] Revisar teclado, foco, feedback, gestores de claves y links caducados; mantener estilo de INTERFAZ_VISUAL.md.

==================================================
## 4. MIGRACIÓN, SEGURIDAD Y OPERACIÓN
==================================================

- [x] Verificar upgrade desde BD existente y desde vacía, índices, conservación de cuentas/asignaciones y rollback practicable con backup en base desechable.
- [x] Documentar despliegue coordinado API/frontend/worker, invalidación de tokens antiguos y expiración absoluta de sesiones.
- [x] Verificar HTTPS, cookies, CORS, CSRF, secretos/rotación, logs sin credenciales y limpieza de tokens/sesiones/outbox; medir costo de hashing y límites.
- [x] Documentar monitoreo de fallos, bloqueo abusivo, cola fallida, revocación por incidente, recuperación de ADMIN y retención de auditoría; no registrar más datos personales de los necesarios.
- [x] Mantener abierta la habilitación externa hasta probar SMTP autorizado, dominio/remitente y URL HTTPS reales. Capturador local no es evidencia de entrega productiva.
- [x] Registrar MFA/passkeys/SSO como ampliaciones fuera de este alcance; evaluar MFA para ADMIN antes de un despliegue sensible sin declarar certificación NIST/ASVS.

==================================================
## 5. REGRESIÓN ELECTORAL Y DOCUMENTACIÓN
==================================================

- [x] Ejecutar suites backend/frontend y recorridos electorales críticos: permisos, guardar candidato ausente de padrón, envío y solo lectura, reportes y descargas.
- [x] Actualizar AUTHENTICATION.md, manuales ADMIN/APODERADO, operación local, README y .env.example con comportamiento implementado.
- [x] Entregar informe consolidado 16–21 con evidencias locales y externas separadas, pendientes y criterios de habilitación; no marcar completada producción si faltan SMTP/dominio.

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

## Evidencia de cierre local

Ver [informe](report.md) y [matriz/evidencia 16–21](../INFORME_16_21.md). Los checks
corresponden al entorno local; HTTPS/SMTP externo y aceptación institucional siguen
pendientes según la sección de habilitación externa. No se afirma despliegue productivo.
