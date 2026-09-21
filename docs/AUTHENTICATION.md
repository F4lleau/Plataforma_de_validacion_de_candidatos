# Autenticación y seguridad de cuentas

Tasks 16–19 implementadas sobre el login/RBAC previo. Las invitaciones y primer
acceso corresponden a Task 20 y continúan pendientes. No se afirma certificación
OWASP/NIST ni integración de correo productiva por superar pruebas locales.

## Sesiones y corte de versión

JWT access HS256, 15 minutos por defecto; claims obligatorios `sub`, `iss`, `aud`,
`iat`, `exp`, `jti`, `sid`, `type=access`. Algoritmo fijo, clave aleatoria >=32 bytes,
`kid` limitado al inventario del entorno; tolerancia de reloj de 5 segundos. HS256
se conserva porque una sola API emite y verifica. Usuario activo/rol/módulos/listas
se consultan en BD; un claim de rol no autoriza.

Access solo en memoria; la cookie `je_refresh` contiene un secreto aleatorio de
32 bytes, `HttpOnly`, `SameSite=Strict`, `Path=/api/v1/auth`, `Secure` en producción.
La BD guarda digest SHA-256, nunca el refresh original. Cada uso rota y conserva el
digest consumido hasta la limpieza. Reutilizarlo revoca la familia completa sin
ventana de gracia. Una respuesta de refresh perdida requiere volver a ingresar;
no reintentar el mismo secreto desde un cliente propio.

La sesión vence a los 7 días absolutos o 24 horas sin renovación. Cada request
comprueba su vigencia; logout, cambio/reset y desactivación revocan inmediatamente
los access asociados. Las sesiones ya abiertas no se expulsan por intentos fallidos
provocados por terceros. La actividad se actualiza en la renovación (máximo cada
15 minutos durante uso continuado).

**Corte coordinado API/frontend:** los JWT anteriores sin `sid` dejan de funcionar;
el frontend elimina las claves legacy de localStorage. Los usuarios, hashes bcrypt,
asignaciones y datos electorales se conservan. El siguiente ingreso pide credenciales.

`JWT_KEY_ID`/`SECRET_KEY` eligen la clave nueva; `JWT_PREVIOUS_KEYS` es un objeto JSON
kid → clave anterior. Mantener claves anteriores durante 15 minutos + 5 segundos,
y retirarlas al terminar la transición. Ante compromiso revocar también sesiones.
Cambiar la clave de JWT reinicia de hecho el espacio HMAC de cuotas; coordinarlo.

## Navegador y CSRF

`GET /auth/csrf` entrega un nonce y una cookie HttpOnly `je_csrf` con Path de la API.
Login, refresh, logout, recuperación y acciones sensibles requieren el nonce en
`X-CSRF-Token` **y** un `Origin` exacto autorizado. CORS permite credenciales solo
para orígenes explícitos. Un cliente no navegador debe obtener cookie/nonce y enviar
Origin configurado; no hay excepción de seguridad para Swagger o scripts.

Frontend/API deben compartir sitio: usar ambos `localhost` o ambos `127.0.0.1`,
HTTPS en producción. `VITE_API_URL` permite configurar la API; por defecto conserva
el hostname del navegador y usa puerto 8000. Despliegues entre sitios distintos
requieren un diseño adicional de cookies; no basta ampliar CORS.

El cliente coordina refresh concurrentes dentro de una pestaña; Web Locks serializa
login/refresh/logout entre pestañas y BroadcastChannel comunica cambios de cuenta
sin persistir tokens. Usar navegadores actuales con Web Locks y contexto seguro
(HTTPS o localhost). Si no está disponible, dos renovaciones simultáneas pueden
forzar nuevo login por detección de replay, nunca aceptar dos usos del mismo secreto.

Un 401 puede renovar y repetir una vez: la autenticación se evalúa antes del handler
de dominio. Un 403, error de red o respuesta exitosa no se reintenta. Upload y descarga
usan el mismo cliente. Respuestas de una sesión anterior no restauran datos tras logout.
Si el logout no llega al servidor, se informa que la revocación remota no fue confirmada.

## Endpoints implementados

Prefijo `/api/v1`. Todas las respuestas llevan `Cache-Control: no-store`,
`Referrer-Policy: no-referrer` y `X-Content-Type-Options: nosniff`.

| Endpoint | Requisito / efecto |
| --- | --- |
| GET /auth/csrf | Cookie/nonce CSRF; no autentica |
| POST /auth/login | Email/clave + CSRF; access y usuario en JSON, refresh solo cookie |
| POST /auth/refresh | Cookie + CSRF; rotación atómica |
| POST /auth/logout | Cookie + CSRF; idempotente |
| GET /auth/me, /auth/modules | Bearer válido y usuario activo |
| GET /auth/sessions | Solo sesiones vigentes del propietario, sin secretos |
| DELETE /auth/sessions/{sid} | Propietario + CSRF; cierre individual |
| POST /auth/reauthenticate | Bearer + clave actual + CSRF, hasta 5 intentos/15 min |
| POST /auth/logout-all | Bearer + reautenticación de últimos 5 minutos + CSRF |
| GET /admin/users/locks | ADMIN, `locked_only`, `offset`, `limit` (máximo 100) |
| POST /admin/users/{id}/unlock | ADMIN + reautenticación + motivo, no reactiva cuenta |
| POST /admin/users/{id}/password-recovery | ADMIN + reautenticación; envía enlace, no fija clave |
| POST /auth/password/forgot | Email + CSRF; respuesta genérica |
| POST /auth/password/reset | Token + nueva clave + CSRF; consume y cierra sesiones |
| POST /auth/password/change | Bearer + clave actual/nueva + CSRF; cierra sesiones |

## Bloqueo y recuperación

Cinco fallos en 15 minutos bloquean nuevos login por 15 minutos; no se extiende
el bloqueo por seguir intentando durante ese plazo. Login válido o expiración
reinicia contadores. Hay cuotas compartidas por BD e identificador/IP: 100 por IP
por operación/15 min, 20 por identificador en login y 5 en recuperación, cambio y
reauth. IP se toma de `request.client`; ejecutar Uvicorn con `--no-proxy-headers`
en local. Tras proxy, restringir proxy headers a IPs realmente confiables y asegurar
que el proxy reemplace cabeceras del cliente; nunca usar `--forwarded-allow-ips='*'`.

Los errores de credenciales no revelan cuenta inexistente/inactiva/bloqueada.
Se verifica hash ficticio para cuentas ausentes; login/forgot compensan caminos
rápidos hasta al menos 350–379 ms. No es garantía de tiempo constante bajo carga;
medir nuevamente en el servidor de producción. Las cuotas retornan 429 uniforme.
Las colisiones de email normalizado legado fallan cerradas y requieren resolución
administrativa; no se elige una identidad arbitraria.

Forgot no cambia contraseña, bloqueo ni sesiones. Cooldown de 60 segundos y cuota
de 5/15 minutos por identificador, sin invalidar enlaces previos. Tokens independientes opacos de 32 bytes,
digest en tabla exclusiva, 30 minutos de vigencia y versión de credenciales.
GET no consume. Un POST válido serializado por usuario cambia hash, consume todos
los resets, limpia bloqueo temporal y revoca sesiones. Nunca reactiva una cuenta.
Una notificación queda en outbox; un fallo SMTP posterior no revierte el cambio.

El enlace lleva token en fragmento, se captura en memoria y se retira de historial
al abrir. La pantalla no carga fuentes/analítica externas. En el hosting servir SPA
con `Cache-Control: no-store` para `/restablecer-clave`; Vite local ya entrega HTML
con `Cache-Control: no-store`. No registrar cuerpos ni URLs completas en proxies/analítica.

## Contraseñas

Nuevas claves: 15–128 caracteres Unicode, espacios y pegado permitidos; sin reglas
arbitrarias de mezcla ni caducidad periódica. Lista local de 10.015 claves comunes,
fuente/licencia y actualización en `backend/app/core/COMMON_PASSWORDS.md`. Rechaza
además secuencias de un único carácter repetido; no es un catálogo
completo de filtraciones. Nunca envía claves a servicios externos.

Argon2id (64 MiB, 3 iteraciones, 4 vías) para nuevos hashes; bcrypt legado verificable
y rehash al ingreso válido. Una clave heredada corta sigue pudiendo iniciar sesión;
las nuevas reglas se aplican en alta/cambio/reset. Bcrypt histórico solo distingue
los primeros 72 bytes; tras rehash Argon2id se conserva el texto exacto ingresado.
No se altera un hash sin conocer la clave correcta.

La edición ADMIN rechaza `password` por API/UI; recuperación desde **Seguridad de
cuenta**. El alta manual devuelve 410: las cuentas nuevas de APODERADO se crean solo al
aceptar invitaciones. No existe alta pública sin enlace ni creación de ADMIN.

## Correo, operación y pruebas

Ver [operación de autenticación y SMTP](AUTH_OPERATIONS.md), ejemplos de entorno
en raíz/backend/frontend, y [informe 16–19](task/INFORME_16_19.md).

## Invitaciones y primer acceso (Tasks 20–21)

ADMIN usa `GET/POST /admin/invitations` (listado paginado de 25, máximo 100) y
`POST /admin/invitations/{id}/resend|cancel`. Las mutaciones requieren CSRF,
sesión ADMIN y reautenticación reciente. Solo APODERADO; el cuerpo de alta contiene
email y módulos, nunca contraseña, rol elegido por el cliente ni enlace de retorno.

La invitación existe separada de User, con email normalizado único, digest SHA-256,
invitador, módulos, generación y estado. La vigencia predeterminada es 48 horas;
cuota por ADMIN de 20 operaciones/hora y cooldown de envío de 60 segundos. Reenvío
rota el secreto de 32 bytes, cancela los correos pendientes anteriores y conserva
historial mediante generación/auditoría. Cancelar invalida aceptación y correos
pendientes. `expired` se deriva del vencimiento; SMTP y aceptación son estados
independientes. Un correo ya aceptado por SMTP no puede retirarse del buzón,
pero su enlace invalidado deja de servir.

`POST /auth/invitations/inspect` recibe el token en body y devuelve solamente email,
rol y vencimiento. No consume ni crea cuenta/sesión. `POST /auth/invitations/accept`
recibe token, full_name, username y password; rechaza campos extra como email,
rol, módulos o activación. Ambos requieren CSRF y cuotas por IP; aceptación también
limita por digest del identificador. Token de reset, refresh o JWT no sirve como invitación.

La aceptación bloquea invitador e invitación, revalida ADMIN activo, catálogos y reglas
habilitados. En una transacción crea User con Argon2id y `email_verified_at`, módulos,
auditoría y consumo del enlace. No asigna listas ni crea sesión automáticamente.
El destinatario inicia sesión normalmente. Si otro ADMIN reemplazó la invitación,
el enlace previo se rechaza aun tras una carrera. Una cuenta existente —activa o
inactiva— no se sobrescribe ni reactiva por invitación.

La página `/invitacion` captura solo su fragmento, lo elimina del historial y lo
conserva en memoria; recargar requiere reabrir el correo. No envía token por query,
no carga analítica externa ni cambia silenciosamente otra sesión abierta. Solicita
nombre, usuario (3–50 letras ASCII/números/punto/guion/guion bajo), contraseña y
confirmación, con email fijo. `/seguridad` muestra perfil, verificación y sesiones.

Usuarios legacy conservan datos, roles, módulos y listas; `email_verified_at=NULL`
indica ausencia de verificación histórica y no bloquea acceso. Cambio de email y
alta de ADMIN están fuera de alcance: PUT de apoderado rechaza cambiar el correo.
El índice único de `lower(btrim(email))` evita nuevas colisiones. La migración aborta
si detecta duplicados normalizados; nunca fusiona ni elimina cuentas automáticamente.

Ver [operación](AUTH_OPERATIONS.md) y [aceptación consolidada](task/INFORME_16_21.md).

## Task 22: términos y privacidad

Tras autenticar, una cuenta sin `terms_accepted_at` tiene sesión restringida. Login,
refresh y `/auth/me` devuelven `terms_accepted_at` y `terms_version` (NULL mientras
estén pendientes), sin exponer la instantánea del texto. El frontend permanece en
login y muestra debajo del botón el checkbox sin marcar y «Aceptar y continuar».
Crear contraseña mediante invitación no acepta términos ni inicia sesión.

`get_authenticated_user` verifica identidad/sesión y se utiliza únicamente para
`/auth/me` y aceptación. `get_current_user` agrega la condición de términos y es la
base de los permisos existentes. Mientras falte aceptación, las funciones protegidas
(incluidos módulos, administración, archivos, exportaciones y gestión de sesiones)
responden `403` con `detail.code=TERMS_ACCEPTANCE_REQUIRED`. Login, CSRF, refresh,
logout y los flujos públicos de ayuda/recuperación/invitaciones siguen disponibles;
no conceden acceso al dominio electoral. Una sesión revocada/inactiva devuelve 401.

| Endpoint | Contrato |
| --- | --- |
| GET `/api/v1/legal/documents` | Público, no-store. Términos y políticas con título, versión, fecha, aviso provisorio, párrafos y SHA-256 del contenido. Solo lectura. |
| POST `/api/v1/auth/terms/accept` | Sesión válida + CSRF. Body: `accepted: true` booleano estricto, `version` y `sha256` de términos. Devuelve perfil actualizado; campos extra rechazados. |

La aceptación serializa usuario→sesión, revalida estado y guarda fecha UTC del
servidor, versión e instantánea JSON del documento junto a auditoría
`legal.terms_accepted` en una transacción. Reintentos simultáneos preservan la primera
fecha/versión. Un texto cambiado antes de la primera confirmación devuelve `409
TERMS_DOCUMENT_CHANGED`; la UI recarga documentos y desmarca el checkbox.

La aceptación es única por cuenta, también ADMIN, y persiste entre navegadores,
logout, cambios/reset de clave y desbloqueo. Las cuentas existentes sin evidencia
la completan al siguiente acceso/restauración; la migración no inventa consentimiento.
Actualizar el documento no exige reaceptación de cuentas ya aceptadas. El cliente
no concede acceso basado en localStorage y no convierte un 403 de términos en un
bucle de refresh. Una pestaña pendiente actualiza el perfil al recuperar foco.

Los enlaces del login/footer abren el mismo modal accesible, con Escape, contención
y devolución de foco, scroll y diseño móvil. Lectura/cierre no aceptan ni modifican
la cuenta. Privacidad es informativa; no tiene checkbox adicional. Los documentos
son provisorios para pruebas, pendientes de revisión institucional para producción.
