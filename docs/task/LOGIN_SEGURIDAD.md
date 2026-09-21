# Plan de login, seguridad de cuentas e invitaciones

Fecha: 20/09/2026. **Planificación documental; Tasks 16–21 aún no implementadas.**
Fuente: pedido del usuario de JWT/estándares, SMTP, recuperación, bloqueo por
reintentos, desbloqueo ADMIN e invitación con enlace único para completar datos y
contraseña. Amplía Tasks 03/05/15; no procede del PDF electoral.

## Estado real al planificar

| Área | Implementado | Brecha |
| --- | --- | --- |
| JWT | HS256 configurable, firma, exp/sub/type, usuario activo y rol actual en BD | Sin iss/aud/sid, familias de sesión ni revocación individual |
| Renovación | API emite refresh con expiración de 7 días | No existe endpoint refresh; cliente lo descarta |
| Navegador | Access en localStorage/Zustand, /me, manejo 401/403 | Logout solo local; token copiado válido hasta expirar o desactivar cuenta |
| Claves | passlib/bcrypt; ADMIN fija contraseña inicial o nueva | Sin reset por correo, cambio propio ni política compartida nueva |
| Cuentas | ADMIN gestiona APODERADO, is_active, módulos y listas | Sin bloqueo temporal, invitación ni primer acceso |
| Correo | SUPPORT_CONTACT y recuperación asistida | Sin SMTP, outbox, worker ni plantillas |
| Auditoría | Historial electoral y gestión de cuentas | Faltan eventos específicos del nuevo ciclo de autenticación |

Evidencia: `backend/app/core/security.py`, `core/config.py`, `services/auth_service.py`,
`services/management_service.py`, `models/user.py`, `schemas/auth.py`,
`api/v1/endpoints/auth.py`; `frontend/src/stores/auth.store.ts`,
`services/api.ts`, `pages/Login.tsx`, `pages/Usuarios.tsx`. Rutas backend bajo `backend/app/`.

No se presenta el login actual como carente de JWT ni el refresh emitido como
renovación implementada. Se preservan usuarios, datos electorales y permisos.

## Orden y cobertura

| Capacidad | Requisito | Task | Estado |
| --- | --- | --- | --- |
| AUTH-01 | JWT reforzado, refresh rotativo, sesiones revocables, cookies/CSRF | [16](16-jwt-sesiones-seguras/task.md) | Pendiente |
| AUTH-02 | SMTP, plantillas, outbox/worker y capturador local | [17](17-smtp-correo-transaccional/task.md) | Pendiente |
| AUTH-03 | Límites de login y bloqueo temporal por reintentos | [18](18-bloqueo-desbloqueo-cuentas/task.md) | Pendiente |
| AUTH-04 | ADMIN consulta/desbloquea cuentas con auditoría | [18](18-bloqueo-desbloqueo-cuentas/task.md) | Pendiente |
| AUTH-05 | Recuperación por correo con token de un uso | [19](19-recuperacion-cambio-clave/task.md) | Pendiente |
| AUTH-06 | Cambio de clave, política común, migración de hash y cierre de sesiones | [19](19-recuperacion-cambio-clave/task.md) | Pendiente |
| AUTH-07 | Invitaciones ADMIN, reenvío, expiración y cancelación | [20](20-invitaciones-onboarding/task.md) | Pendiente |
| AUTH-08 | Primer acceso, datos propios, email verificado y contraseña inicial | [20](20-invitaciones-onboarding/task.md) | Pendiente |
| AUTH-09 | E2E, regresión electoral, migración y operación segura | [21](21-aceptacion-seguridad-login/task.md) | Pendiente |

Ejecutar 16 → 17 → 18 → 19 → 20 → 21. El esquema de tokens, normalización de emails,
eventos y política de cuenta se define en 16 para evitar implementaciones divergentes.
17 prepara plantillas/infraestructura; 19 y 20 conectan sus eventos de dominio reales.
Cada task incluye sus propios tests; 21 agrega el recorrido integral.

## Diseño técnico propuesto

Estas decisiones permiten ejecutar las tasks sin inventar requisitos legales.
Son valores iniciales configurables y revisables mediante evidencia al implementar;
**no se consideran una confirmación institucional ni un estándar universal**.

| Aspecto | Propuesta inicial |
| --- | --- |
| Access JWT | 15 minutos, en memoria; sid permite verificar revocación en servidor |
| Refresh | Opaco, 32 bytes CSPRNG, digest en BD; cookie HttpOnly; rotación por uso |
| Sesión | Límite absoluto 7 días, inactividad 24 horas; renovar no extiende el absoluto |
| Bloqueo | 5 fallos en ventana de 15 minutos → bloqueo temporal de 15 minutos |
| Rate limiting | Cuenta/identificador e IP, compartido por workers; cuotas separadas para login, refresh, reset e invitación, a fijar con pruebas de carga |
| Reenvío correo | Cooldown inicial de 60 segundos y cuotas horarias configurables; no enviar por cada intento fallido |
| Recuperación | Token opaco, 32 bytes CSPRNG, propósito exclusivo y 30 minutos de vigencia |
| Invitación | Token opaco, 32 bytes CSPRNG, propósito exclusivo y 48 horas de vigencia |
| Contraseña nueva | 15–128 caracteres; Unicode/espacios; blocklist local; sin reglas arbitrarias de composición ni rotación periódica |
| Hash | Argon2id nuevo con parámetros medidos; bcrypt legacy verificable y rehash progresivo |
| Primer acceso | Nombre completo, username si se conserva y contraseña; email fijo de invitación |
| Roles invitados | APODERADO; ADMIN asigna módulos y luego listas explícitas |
| Correo local | Capturador SMTP en Docker accesible solo localmente (propuesta Mailpit) |
| Producción | TLS SMTP verificado, HTTPS, remitente autorizado y configuración de dominio verificable |

No crear una implementación propia de criptografía. Usar bibliotecas mantenidas y
revisar sus versiones al ejecutar. Una firma simétrica bien gestionada es válida
para un backend único; varias entidades verificadoras pueden justificar firma
asimétrica. Documentar la elección antes de cambiar claves/formato.

### Estados y transiciones

- La invitación vive separada de `User` hasta aceptarse; evita inventar contraseña,
  nombre o username para campos obligatorios. Sus estados son pendiente, aceptada,
  expirada y cancelada; `superseded`/generación registra reenvíos.
- `is_active=false` es desactivación administrativa. `locked_until` es bloqueo
  temporal de nuevos login; no altera rol ni permisos. Las sesiones existentes no
  se revocan por fallos provocados por terceros. ADMIN dispone de revocación expresa.
- Desactivar usuario revoca sesiones y tokens pendientes vinculados; una cuenta
  inactiva no se reactiva por reset ni por desbloqueo. Revocar invitaciones de ese
  destinatario y comprobar la autorización del invitador al aceptar.
- Desbloqueo ADMIN limpia intentos/bloqueo, con motivo y autenticación reciente
  (propuesta 5 minutos). Un ADMIN activo puede desbloquear otro ADMIN; no por ello
  puede crearlo, editar su rol ni conocer su contraseña.
- Reset exitoso limpia bloqueo temporal, cambia hash y revoca todas las sesiones y
  enlaces reset del usuario. Solicitar reset nunca bloquea ni modifica una cuenta.
- Una nueva solicitud de reset respeta cooldown y permite que enlaces vigentes
  coexistan hasta consumo; evita invalidarlos por una solicitud maliciosa. Se
  limitan tokens pendientes por cuenta sin invalidar silenciosamente enlaces activos.
- Reenviar invitación, acción exclusiva ADMIN, sí revoca el token anterior. La
  aceptación y cancelación/reenvío se serializan para impedir doble alta.
- JWT access, refresh, reset e invitación son credenciales de propósitos distintos.
  No aceptar ninguna en el lugar de otra. Abrir un enlace no consume ni autentica:
  se requiere POST explícito. Tras alta/reset el usuario inicia sesión normalmente.

### Navegador y correo

Preferir frontend/API del mismo sitio en producción. Documentar dominio, Path,
SameSite, Secure y CORS según despliegue; no asumir que dos orígenes son mismo sitio.
Las operaciones basadas en cookie requieren protección CSRF, también login/logout.
Access/refresh no van en localStorage, query de API, logs o historial de auditoría.

La página de enlace debe evitar recursos/analítica de terceros, limpiar el secreto
de la URL y usar no-store/no-referrer. Preferir token en fragmento de URL y enviarlo
por POST desde la app; validar la estrategia con clientes de correo y redacción de
logs de proxy antes de elegir query como alternativa. No guardar el secreto en
storage persistente ni imprimirlo en mensajes de error.

Guardar digest de credenciales en sus tablas. Una outbox durable necesita transportar
el enlace original: cifrar ese payload con clave externa a BD, acceso mínimo y
retención corta; borrar contenido al enviarse o expirar. No afirmar que todo es
«solo hash» mientras se persiste texto de correo con token. Reintentar el mismo
mensaje no renueva validez, y un worker comprueba token vigente antes de enviarlo.

Un SMTP que acepta un mensaje no confirma entrega al buzón. El flujo mantiene
estado de dominio y estado de entrega separados. Logs y auditoría registran IDs,
actor, resultado y razón sanitizada; nunca contraseña, cookie, token o enlace.

## Contratos previstos, no existentes todavía

Prefijo API `/api/v1`. Los nombres se consolidarán antes de implementar; métodos
con efectos usan POST/DELETE y todas las operaciones tienen límites y validación.

| Contrato | Acceso / efecto | Responsable |
| --- | --- | --- |
| POST /auth/login | Credenciales; crea sesión y cookie; respuesta genérica ante rechazo | 16, 18 |
| POST /auth/refresh | Refresh cookie + CSRF; rota, valida usuario/sesión; devuelve access | 16 |
| POST /auth/logout | Revoca sesión actual, limpia cookie; idempotente | 16 |
| POST /auth/logout-all | Sesión + reautenticación reciente; revoca todas | 16 |
| GET /auth/sessions | Lista únicamente sesiones propias con datos mínimos | 16 |
| DELETE /auth/sessions/{id} | Propietario autenticado; revoca sesión seleccionada | 16 |
| GET /admin/users/locks | ADMIN; listado paginado/filtrable de bloqueos | 18 |
| POST /admin/users/{id}/unlock | ADMIN + reautenticación + motivo; no reactiva cuenta | 18 |
| POST /auth/password/forgot | Público; siempre respuesta genérica, mail si corresponde | 19 |
| POST /auth/password/reset | Token de reset + clave; consume y revoca sesiones | 19 |
| POST /auth/password/change | Sesión + clave actual/reautenticación; cambia y revoca sesiones | 19 |
| POST /admin/users/{id}/password-recovery | ADMIN autenticado recientemente; envía enlace, no fija clave | 19 |
| GET/POST /admin/invitations | ADMIN; listar/crear invitación a APODERADO | 20 |
| POST /admin/invitations/{id}/resend | ADMIN; nuevo enlace y revocación anterior | 20 |
| POST /admin/invitations/{id}/cancel | ADMIN; revoca invitación pendiente | 20 |
| POST /auth/invitations/inspect | Token en body; contexto mínimo y sin consumir | 20 |
| POST /auth/invitations/accept | Token + perfil + clave; aceptación atómica | 20 |

16 debe definir también mecanismo de reautenticación reciente, con alcance ligado
al usuario y sesión, TTL corto y límites de intentos. No depender de un timestamp
manipulable en frontend. 19/20 reutilizan ese mecanismo para acciones sensibles.

Vistas previstas: login, solicitar recuperación, restablecer clave, aceptar
invitación, perfil/seguridad/sesiones propias y administración de bloqueos e
invitaciones. Reutilizar estilos/componentes de [interfaz visual](../INTERFAZ_VISUAL.md).

## Auditoría, privacidad y pruebas transversales

Eventos mínimos: login aceptado/fallido con cuotas de registro, sesión creada,
renovada/revocada/replay, bloqueo/desbloqueo, recuperación solicitada/consumida,
contraseña cambiada, invitación creada/reenviada/cancelada/aceptada y entrega SMTP.
Evitar almacenamiento ilimitado por ataques; índices/retención configurables y
agregación de fallos. Proteger identificadores de cuentas inexistentes e IP; no
registrar cuerpos de solicitudes. Cada cambio crítico y su auditoría son atómicos.

Pruebas: consumo único bajo concurrencia, CSRF, diferencias entre roles, JWT
revocado, múltiples pestañas/workers, fallos SMTP, cuentas legacy y permisos
electorales. Las comprobaciones de email no equivalen a validación RENAPER.

## Referencias consultadas

Consultadas el 20/09/2026; verificar actualizaciones al implementar. Las guías
sustentan controles concretos; no se declara certificación ni conformidad global.

- [IETF RFC 8725 — JWT Best Current Practices](https://datatracker.ietf.org/doc/html/rfc8725): validación de algoritmo, claves, claims y separación de tipos.
- [IETF RFC 9700 — OAuth Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html): referencia para rotación/detección de replay. Esta app no se declara proveedor OAuth/OIDC por usar JWT.
- [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html): limitación de intentos, reautenticación y errores que no revelan cuentas.
- [OWASP Forgot Password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html): recuperación con tokens limitados y respuestas genéricas.
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): ciclo de sesión y controles de cookies.
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): hash adaptativo y transición desde bcrypt.
- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html): referencia de política de contraseña para autenticación de un factor; no se afirma nivel de aseguramiento NIST.

## Límites y datos externos pendientes

Proveedor SMTP, dominio/remitente, secretos, URL HTTPS y destinatario de prueba
externa se definirán antes de habilitar correo real. No hacen falta para crear estas
tasks ni para su implementación local con capturador. Secretos solo por entorno.

MFA/passkeys/SSO, cambio de email con doble verificación y nuevas facultades para
crear ADMIN requieren alcance posterior; no quedan implícitamente completados en
«estándar de la industria». Evaluar MFA para ADMIN antes de producción sensible.
