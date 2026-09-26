# Retiro de RENAPER — 22/09/2026

**Implementado y verificado localmente. Sin commit ni push.**

El usuario solicita retirar RENAPER del sistema. Antes de modificarlo se ejecutaron
`git fetch origin --prune` y `git pull --ff-only origin develop`: no había cambios
remotos ni locales; `develop` coincidía con `origin/develop` en `8787e2e`.

## Análisis de las tasks

| Tasks | Cambio de alcance |
| --- | --- |
| 04 | Configuración deja de ofrecer/exigir RENAPER. |
| 08 | Guardado, corrección y revalidación conservan afiliación y edad/requisitos. |
| 09 / CAP-15 | Retirada por el usuario; el proveedor/API deja de ser un pendiente. |
| 10 | Envío y aprobación ya no evalúan identidad externa. |
| 11–14 | Consultas operativas excluyen controles retirados; auditoría histórica se conserva. |
| 15 | Manuales/ayuda/aceptación se actualizan al alcance sin RENAPER. |
| 16–22 | Autenticación, correo, invitaciones y términos mantienen su comportamiento. |

La decisión D20 reemplaza D07. El PDF y los informes anteriores son antecedentes;
su exigencia de RENAPER no prevalece sobre la nueva instrucción del usuario.
El feedback granular de CAP-16 continúa con los controles locales de Task 08.

## Checklist de implementación

- [x] Revisar origin y sincronizar develop antes de editar.
- [x] Eliminar `RenaperClient` y `RenaperValidationService`, incluidas sus pruebas obsoletas.
- [x] Dejar de generar controles/persistencias nuevas de identidad externa.
- [x] Retirar `requires_renaper` del contrato de escritura y de las respuestas de reglas.
- [x] Ignorar ese campo en versiones antiguas sin modificar su JSON persistido.
- [x] Conservar idempotencia al guardar reglas equivalentes a una versión histórica.
- [x] Excluir controles retirados de candidatos, historial operativo y bandeja de revisión.
- [x] Quitar condición de identidad externa en aprobación automática.
- [x] Retirar opción/textos de configuración, candidatos, composición, ayuda y PDF exportado.
- [x] Actualizar índice, matriz, decisiones, manuales e instrucciones para agentes.
- [x] Verificar regresión, compatibilidad con datos antiguos y pantallas afectadas.

## Reglas que continúan

Una ausencia en padrón conserva el candidato con advertencia y permite trabajar.
Una composición incompleta/incorrecta impide enviar. Una lista completa con controles
pendientes u observados puede enviarse para revisión y queda en lectura.
La aprobación automática exige composición conforme, plantilla institucional y otros
requisitos confirmados, edad/requisitos OK y afiliación OK cuando es obligatoria.
Retirar RENAPER no confirma plantillas de prueba ni dispensa controles pendientes.

## Datos, contratos y despliegue

No cambia la estructura de la base: Alembic permanece en `b8316d72c4ef` y
`alembic check` no detecta operaciones nuevas. Se mantienen los valores históricos
de enums y las filas antiguas para permitir lectura y auditoría sin pérdida de datos.
No se reescriben listas enviadas, instantáneas de evaluación, reglas versionadas ni
eventos antiguos; pueden mencionar RENAPER como parte de su evidencia original.
El historial operativo del candidato muestra únicamente controles vigentes.

Los paths HTTP y permisos se conservan. La escritura de reglas rechaza con 422
`requires_renaper` porque el campo fue retirado; GET de reglas y detalle de lista lo
omiten incluso para versiones antiguas. Publicar backend y frontend conjuntamente
y recargar clientes abiertos. No hacen falta nuevas variables ni API externa.
Reiniciar la API para cargar el código actualizado; no ejecutar un borrado masivo
de validaciones ni reconstruir estados de listas enviadas.

## Verificación

- Backend: `SECURITY_POSTGRES_TESTS=1 .venv/bin/python -m pytest -q`:
  **188 passed**, incluidos tests PostgreSQL en bases temporales migradas.
- Frontend: **23 passed**, build y lint aprobados.
- La prueba positiva de aprobación usa importación real de un XLSX sintético y
  consulta al padrón de pruebas, sin doble de proveedor de identidad. Una regla
  histórica con `requires_renaper=true` no la bloquea.
- Nuevas regresiones: reglas antiguas ocultas e inmutables, escritura obsoleta
  rechazada, revalidación sin sobrescribir controles retirados, ausencia de esos
  controles en UI/historial y exclusión de warnings retirados en la bandeja.
- Navegador conectado a PostgreSQL local: login, configuración con reglas antiguas,
  detalle de una lista existente y ayuda. Solo aparecen afiliación y requisitos;
  sin errores JS ni overlay. Detalle móvil 390×844 sin desbordamiento horizontal.
- QA manual de lectura con cuenta sintética temporal; cuenta, sesiones y scripts
  eliminados al terminar. No se modificaron listas, candidatos ni reglas existentes.
- Capturas de QA fuera de Git: `/tmp/retiro-renaper-config.png`,
  `/tmp/retiro-renaper-lista.png`, `/tmp/retiro-renaper-mobile.png`.
- Advertencias preexistentes: uso de `datetime.utcnow()` y catálogo Browserslist
  desactualizado; no hubo fallos de tests/build.

Siguen pendientes las definiciones y aceptación institucionales, SMTP productivo y
textos legales definitivos. RENAPER ya no forma parte de esos pendientes.
