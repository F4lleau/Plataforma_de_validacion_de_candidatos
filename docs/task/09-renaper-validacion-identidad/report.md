# Informe — Task 09

**Resultado:** Preparación completada; conexión real diferida por el usuario.

Cliente desacoplado sin llamadas de red, contrato tipado, estados honestos, orquestación/persistencia, reintento autorizado y UI granular. No hay API real ni OK simulado.

## Implementación principal

- `backend/app/integrations/renaper_client.py`
- `backend/app/services/renaper_validation_service.py`
- `backend/app/services/electoral_workflow_service.py`

Se reutilizan modelos, JWT, repositories y layout. Escrituras administrativas exigen ADMIN;
listas/candidatos de APODERADO requieren módulo habilitado y asignación expresa.
Ausencia/inactividad en padrón conserva el registro con warning.

## Verificación

- `pytest -q`: **73 passed** (incluye regresiones anteriores).
- `npm run test`: **11 passed**; build y lint sin errores.
- Alembic current/heads: `e271bb89a403`; `alembic check` sin operaciones pendientes.
- PostgreSQL vacío: upgrade, downgrade al checkpoint anterior y upgrade de nuevo.
- PostgreSQL con datos: migración local conserva usuarios/listas/padrón previos.
- Importaciones concurrentes: dos lotes completos, exactamente uno vigente.
- Navegador: configuración y apoderado guardados, padrón consultable; APODERADO carga
  candidato ausente, ve controles, corrige y guarda borrador; ADMIN-only deniega acceso.
- Móvil 390×844: sin overflow ni overlay de error.
- [Evidencia visual](../evidencia-04-09/validaciones-mobile.png).

Las pruebas de identidad usan cliente no configurado/dobles, no una API externa real.
Deprecaciones existentes de datetime/passlib y aviso Browserslist no impiden los checks.

## Pendientes del alcance institucional

- Resolver D07: proveedor autorizado, endpoint/documentación, credenciales, ambiente de pruebas, campos, límites y semántica de coincidencia.
- Implementar cliente encapsulado con timeout y errores controlados; configuración/secretos por entorno.
- Validar respuesta y coincidencia según contrato; no hacer comparación improvisada de nombres o sexo.
- Permitir reintentar fallos transitorios bajo límites; no mantener transacciones DB abiertas mientras se espera a la red.
- Contrato del proveedor: coincide, no coincide, no encontrado, datos incompletos, timeout, 429 y respuesta inesperada.
- Con credenciales de pruebas autorizadas, verificar un caso real del proveedor y registrar evidencia sin secretos.

Ver [decisiones](../DECISIONES.md), [contratos](../../ELECTORAL_WORKFLOWS.md) y
[git status/diff de cierre](../INFORME_04_09.md). Sin commit ni push.
