# Task 22 — Informe de implementación

Fecha: 21/09/2026. Rama: `develop`. Implementación local, sin commit/push.

## Resultado

La identidad autenticada debe aceptar términos una sola vez antes de usar módulos.
El login muestra el aviso debajo del botón, checkbox sin marcar y acción explícita.
La aceptación se guarda antes de navegar. Los enlaces de login/footer abren los
mismos modales de términos y privacidad sin afectar formularios ni registrar
consentimiento por lectura. Textos provisorios visibles y centralizados en backend.

## Archivos y contratos

Rutas desde raíz:

- `backend/app/legal/documents.json`: fuente única de ambos textos, versión/fecha.
- `backend/app/repositories/legal_repository.py`, `services/legal_service.py`,
  `schemas/legal.py`, `api/v1/endpoints/legal.py`: lectura, hash, validación y aceptación.
- `backend/app/models/user.py`: fecha UTC de primera aceptación, versión e instantánea
  JSON. `backend/alembic/versions/b8316d72c4ef_terms_acceptance.py`: campos nullable y
  restricción de integridad, sin backfill ficticio.
- `backend/app/core/security.py`: identidad separada de autorización; todas las rutas
  protegidas conservan el guard central. `/auth/me` y aceptación permiten identidad pendiente.
- `frontend/src/components/legal/LegalAccess.tsx`, `LegalModal.tsx` y
  `frontend/src/services/legal.service.ts`: documentos, confirmación, errores y modal.
- Login, AppLayout, ProtectedRoute, auth store/contratos y cliente API: paso pendiente,
  acceso por rol, manejo específico de 403, sincronización de perfil y respuestas obsoletas.
- Tests backend/frontend, manuales, contratos/operación, AGENTS de capas y backlog.

| Contrato nuevo | Resultado |
| --- | --- |
| GET `/api/v1/legal/documents` | Documentos públicos con SHA-256; no-store, sin mutación. |
| POST `/api/v1/auth/terms/accept` | Sesión válida, CSRF y booleano estricto; fecha/versión/snapshot + auditoría en una transacción. |
| `403 TERMS_ACCEPTANCE_REQUIRED` | Cuenta válida sin aceptación, sin acceso a módulos/admin/archivos/exportaciones. |
| `409 TERMS_DOCUMENT_CHANGED` | Primera aceptación de contenido desactualizado; UI recarga y desmarca checkbox. |

Se serializa usuario→sesión y se revalida activación/revocación tras el lock. Unicidad
natural por cuenta: doble clic/concurrencia/reintentos no reemplazan fecha ni versión.
La auditoría `legal.terms_accepted` y la evidencia en User sobreviven limpieza de auth/mail.
No se registran IP, dispositivo, contraseñas o tokens en esta evidencia.

## Verificación automatizada

- Suite completa: `SECURITY_POSTGRES_TESTS=1 .venv/bin/python -m pytest -q` desde
  backend: **187 passed**, 0 skipped. Incluye bases PostgreSQL desechables migradas,
  doble aceptación concurrente, migración/reversión y backup/restore existente.
- Se agregó después una prueba explícita de conservación tras cambio/reset de clave,
  desbloqueo y logout: suite específica `tests/test_legal_22.py`, **20 passed**.
  Total de casos únicos comprobados: **188**. Solo warnings preexistentes de `datetime.utcnow`.
- `npm run test`: **23 passed**; incluye falla de aceptación, 403 sin refresh,
  logout/respuestas obsoletas, restauración, perfil concurrente y destino de login.
- `npm run build` y `npm run lint`: correctos; build avisa dataset Browserslist antiguo.
- `alembic upgrade head` aplicado local; `alembic check`: sin diferencias.
- Ruff de imports/referencias nuevas y `git diff --check`: correctos.

La prueba de inventario recorre dependencias de todas las rutas API: exige el guard
central salvo la lista explícita de documentos/identidad/aceptación y flujos públicos
existentes. Casos incluyen intentos por API directa, campos extra, booleano falso o
string, contenido cambiado, CSRF, usuario inactivo/revocado y rollback de auditoría.
Las fixtures electorales representan usuarios ya aceptados; el flujo de invitación
prueba explícitamente bloqueo y aceptación antes de ejercer permisos.

## Verificación manual local

Recorrido con cuentas sintéticas; PostgreSQL y Mailpit en Docker, API 8000 y Vite 5173.
Skills utilizadas: agent-browser, agent-browser-verify, verification y revisión React.

- Modal público antes de login: contenido/aviso, Escape, devolución del foco y
  conservación de campos. Sin overlay ni errores JavaScript.
- Login ADMIN sin evidencia → pantalla pendiente, contraseña retirada del formulario,
  checkbox inicialmente desmarcado y confirmación deshabilitada.
- Acceso directo a `/listas` y restauración de cookie → vuelve al paso pendiente,
  sin mostrar módulos. Móvil 390×844 sin desbordamiento horizontal.
- Modal de privacidad: teclado, contención de foco y Escape. Se corrigió una salida
  del foco detectada durante la verificación del diálogo nativo.
- Conflicto de versión simulado en navegador → recarga documentos, muestra motivo
  y desmarca el checkbox; conflicto real de hash cubierto por pruebas API.
- Red simulada caída al confirmar → permanece pendiente con error; al restaurar y
  reintentar guarda en PostgreSQL y navega al destino original `/listas`.
- Footer de ADMIN: lectura conserva ruta y formulario de lista sin enviarlo.
- Invitación por API real → perfil/contraseña → cuenta APODERADO inicialmente sin
  aceptación. Ingreso/aceptación correctos; segundo login volvió a `/listas` sin
  checkbox ni aviso, sin tokens persistidos y sin errores JavaScript.

Ambas cuentas sintéticas tenían exactamente un evento de aceptación y su instantánea
en PostgreSQL. Se borraron cuentas, invitación, sesiones, outbox/auditoría sintéticas
y scripts temporales; el navegador de QA quedó cerrado. No se guardaron listas nuevas.
La invitación de QA fue consumida por API antes del envío y el worker canceló ese
correo; este recorrido no se declara una prueba de entrega SMTP.

Capturas de verificación locales fuera de Git: `/tmp/task22-public-modal.png` y
`/tmp/task22-pending-mobile.png`. No contienen credenciales ni personas reales.

## Operación y límites

No hay variables nuevas. Desplegar migración, API y frontend coordinadamente;
reiniciar procesos al actualizar código/documentos. Usuarios existentes completan
el paso una vez. El contenido servido puede cambiar, pero la instantánea original
se conserva y no se fuerza reaceptación dentro de este alcance.

Downgrade elimina los campos/evidencia de aceptación; para recuperar esa evidencia
se requiere respaldo. No elimina usuarios ni datos electorales. Procedimiento en
[operación](../../AUTH_OPERATIONS.md). Textos definitivos/revisión institucional
pendientes; no equivalen a consentimiento de candidatos o personas en el padrón.

## Git

Se preservó la planificación de Task 22 ya presente al iniciar. Los cambios incluyen
implementación, migración, tests y documentación de esta task; `.env` reales no se
versionan. Sin cambios a reglas electorales, integración RENAPER o datos operativos.
No se realizó commit ni push.
