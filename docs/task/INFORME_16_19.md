# Informe Tasks 16–19 — seguridad de acceso y correo local

Fecha: 21/09/2026. Rama: `develop`. Implementación local; sin commit/push.

## Resultado

- **16:** JWT con claims/clave/kid estrictos, sesiones persistentes revocables,
  refresh opaco rotativo, replay detectado, reautenticación, CSRF y página de sesiones.
  Access en memoria; cookies HttpOnly; coordinación de pestañas y cliente API común.
- **17:** SMTP TLS configurable, Mailpit Docker con healthcheck/loopback, outbox
  cifrada transaccional, worker con lease/retry/purga, plantillas españolas HTML/texto.
- **18:** cuotas en PostgreSQL por IP/identificador, bloqueo 5/15/15, ADMIN consulta,
  confirma su clave y desbloquea con motivo; no reactiva cuentas. Recuperación de
  emergencia por comando de servidor auditado.
- **19:** recuperación por correo con token de un uso, cambio autenticado, revocación
  global, Argon2id y compatibilidad bcrypt. ADMIN ya no reemplaza claves existentes.

Task 20 (invitaciones/primer acceso) y Task 21 (aceptación integral adicional) siguen
pendientes. En 18, el estado «invitación pendiente» depende del modelo de Task 20.
SMTP externo necesita proveedor/remitente/HTTPS y aceptación autorizada; Mailpit
solo demuestra el circuito local. RENAPER/reglas electorales no fueron modificados.

## Archivos y migración

Nueva revisión `6cb192ebc9fe` sobre `e271bb89a403`: `auth_sessions`,
`refresh_credentials`, `password_resets`, `auth_rate_limits`, `mail_outbox` y columnas
de bloqueo/versión en users. Migración aditiva, sin borrar cuentas/listas/asignaciones.

Backend: core config/security/passwords/cookies/timing, repositorios auth/mail,
servicios auth/mail, endpoints auth/account_security, comandos mail_worker/unlock_account,
schemas, gestión de cuentas y bootstrap. Argon2-cffi 25.1.0; bcrypt nativo solo legado;
requirements normalizado a UTF-8. Blocklist SecLists MIT con licencia/fuente/hash y
ampliaciones locales; no envía contraseñas a terceros.

Frontend: cliente API/store, PasswordRecovery, AccountSecurity, rutas, login,
gestión de apoderados, ayuda y menú. Validación de longitud por caracteres Unicode,
no unidades UTF-16. Se retiró carga externa de fuentes en las vistas sensibles.

Infraestructura: Mailpit v1.27.4 en `local-deps.yml`; ejemplos raíz/backend/frontend;
generador local crea clave outbox sin mostrarla. Variantes `.env*` ignoradas, salvo
`.env.example`. La configuración existente se preservó y se agregó la clave de
outbox solo al archivo local ignorado.

## Contratos y permisos

Listado completo en [AUTHENTICATION.md](../AUTHENTICATION.md). Los roles y recursos
se resuelven desde BD. APODERADO solo administra sus propias sesiones/clave. ADMIN
puede consultar/desbloquear ADMIN/APODERADO y enviar recuperación, con reautenticación;
no crea ADMIN ni accede a tokens/cuerpos de correo. Los endpoints de negocio conservan
sus validaciones electorales y aislamiento por asignación.

Auditoría de login/fallo agregado/bloqueo/reauth/sesiones/replay/reset/desbloqueo/SMTP,
sin credenciales. Recuperación pública registra actor anónimo y destinatario como
entidad; recuperación ADMIN registra el actor real. Cuotas sobreviven transacciones
rechazadas; cambios de dominio/correo/auditoría se confirman juntos.

## Evidencia

- Suite completa backend con PostgreSQL opt-in: **144 passed** (4 requieren opt-in
  PostgreSQL), incluida caída entre aceptación SMTP y commit y umbral concurrente.
- Frontend: pruebas de sesión/cliente/Unicode/respuestas obsoletas, build y lint.
  **15 tests**; resultado final registrado en los status/report de cada task.
- PostgreSQL desechable: cadena Alembic desde cero; downgrade/upgrade con usuario
  conservado y `alembic check`; dos refresh simultáneos revocan replay; dos reset
  producen un solo cambio/notificación; contadores/umbral no pierden incrementos;
  dos workers no reclaman el mismo envío simultáneo. Las bases de prueba se eliminaron.
- Base local existente migrada; `alembic check` sin diferencias.
- Navegador real: solicitud → Mailpit → enlace → nueva clave → login; token retirado
  de URL, sin credenciales en localStorage ni cookies visibles a JS. Recarga restaura.
  Dos pestañas comparten cierre. APODERADO sin controles ADMIN. ADMIN desbloquea
  cuenta sintética con motivo y reautenticación; sin alertas ni overflow a 390×844.
- Mensajes capturados por Mailpit, sin envío externo. Cuenta y correos sintéticos
  temporales retirados al terminar; no se versiona seed ni material secreto de prueba.
- Argon2id en este host: mediana 22,6 ms / máximo 22,8 ms (5 verificaciones, 64 MiB,
  t=3, p=4). Repetir medición bajo concurrencia en producción antes de dimensionar.
- Advertencias preexistentes: datetime.utcnow en modelos/servicios electorales y
  Browserslist desactualizado. Sin errores de test/build/lint.

Capturas de verificación quedaron en `/tmp`, fuera del repositorio. No se incluyen
correos, enlaces ni contraseñas en este informe.

## Decisiones y límites operativos

HS256 se conserva para una única API. Las claves retiradas se resuelven solo desde
inventario local. El corte exige volver a ingresar con frontend/API actualizados.
Refresh no ofrece replay grace: respuesta perdida exige nuevo login. Web Locks
requiere navegador moderno en contexto seguro; fallback conserva seguridad y puede
pedir nuevo login ante carrera. No hay garantía de tiempo constante bajo saturación.

SMTP es al menos un intento con posible duplicado tras caída posterior a aceptación,
no exactly-once. Payload cifrado se purga tras entrega/expiración/agotamiento; no se
reenvían enlaces consumidos deliberadamente. Producción requiere monitoreo y proveedor
real; ver [operación](../AUTH_OPERATIONS.md). No se presenta Mailpit como integración
externa ni se declara certificación de seguridad.

Hasta Task 20 se conserva alta manual APODERADO con política nueva; no hay invitaciones
ni estado pendiente ficticio. Cambiar email/desactivar revoca enlaces y sesiones,
sin tocar módulos/listas. No hay MFA/SSO ni creación de nuevos ADMIN por estos flujos.

## Git

Cambios sobre develop, sin cambios ajenos al iniciar. `git diff --check` y revisión
de archivos/secretos realizadas al cierre. No se ejecutó commit ni push.

## Continuación

Las limitaciones históricas sobre invitaciones/alta manual fueron resueltas en
Tasks 20–21. Ver [informe consolidado vigente](INFORME_16_21.md).
