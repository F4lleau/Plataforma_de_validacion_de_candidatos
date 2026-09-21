# Informe Task 17

SMTP TLS configurable, Mailpit Docker, outbox cifrada transaccional y worker con lease/retry/purga. Aceptación de proveedor externo pendiente.

Implementada el 21/09/2026 sobre `develop`. Ver [informe conjunto 16–19](../INFORME_16_19.md)
para archivos, modelos, endpoints, permisos, decisiones, evidencia de tests/concurrencia,
recorrido de navegador, límites y estado Git. Ver [contratos](../../AUTHENTICATION.md)
y [operación/variables](../../AUTH_OPERATIONS.md).

La migración compartida es `6cb192ebc9fe`; conserva usuarios/asignaciones/listas.
Pruebas completas backend con PostgreSQL: **144 pasan**. Frontend: **15 tests**, build y lint.
SMTP verificado con captura local Mailpit; entrega externa pendiente de configuración.
No se modificó la regla de afiliación ni se habilitó RENAPER. Sin commit/push.
