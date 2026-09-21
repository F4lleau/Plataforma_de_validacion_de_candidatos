# Operación de login, sesiones y correo

## Preparación local

1. Generar entorno nuevo con `python3 scripts/init_local_env.py`. Si ya existe,
   conservarlo y agregar las variables de `backend/.env.example`; generar una
   `MAIL_OUTBOX_KEY` Fernet con el comando del ejemplo, solo dentro del entorno.
2. `docker compose -f local-deps.yml up -d --wait`: PostgreSQL 17 y Mailpit v1.27.4.
3. Desde `backend/`, instalar `requirements.txt` y ejecutar
   `.venv/bin/alembic upgrade head`. Revisión: `a72e903d418f`.
4. Iniciar API: `.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --no-proxy-headers`.
5. En otra terminal desde `backend/`: `.venv/bin/python -m app.commands.mail_worker`.
6. Desde `frontend/`: `npm ci` y `npm run dev -- --host 127.0.0.1 --port 5173 --strictPort`.

App: http://localhost:5173 · Mailpit: http://localhost:8025 · SMTP: 127.0.0.1:1025.
Los puertos Docker se publican solo en loopback; Mailpit captura, no retransmite.
Su volumen conserva hasta 500 correos de prueba, que pueden contener enlaces de
recuperación; eliminar esos mensajes tras la prueba. Nunca importar datos reales
ni exponer Mailpit a una red pública.

El `.env.example` raíz contiene Compose; `backend/.env.example` documenta todas las
variables de JWT, sesiones, cookies, bloqueo, SMTP y outbox; `frontend/.env.example`
contiene `VITE_API_URL`. Son ejemplos versionables sin valores reales. `.env` sigue
ignorado. La clave outbox es obligatoria también localmente.

## Worker y entrega

PostgreSQL contiene outbox durable. Evento de dominio, digest de reset, auditoría y
correo pendiente se confirman en una transacción. El payload de texto/HTML está
cifrado con Fernet y clave fuera de BD. La tabla de reset solo guarda digest.

Worker reclama con `FOR UPDATE SKIP LOCKED`, registra lease (120 s) y un identificador
de reclamo. Un proceso caído permite retomar tras lease. Antes del transporte verifica
que la cuenta/token sigan vigentes; el claim queda bloqueado durante SMTP para que
otro worker no envíe simultáneamente. `SMTP_TIMEOUT=10`, lease debe superar 4 timeouts.

Estados: `pending`, `processing`, `sent` (aceptado por SMTP), `failed`, `cancelled` (invitación invalidada). Backoff:
60/120/240/480 segundos, máximo 5 intentos. Errores SMTP 5xx son terminales. No se
registra respuesta cruda del proveedor, cuerpo, destinatario ni enlace en logs.
Un Message-ID estable ayuda a diagnóstico, pero **SMTP no garantiza exactamente
una entrega**: si el proceso muere después de aceptación y antes del commit, puede
reenviar el mismo mensaje, sin crear otro token ni extender su vigencia.

`python -m app.commands.mail_worker --once` procesa como máximo un mensaje.
`python -m app.commands.mail_worker --status` muestra recuentos por estado, sin datos personales.

Para fallos transitorios, corregir conectividad y dejar el retry automático. Al agotar
intentos o ante error permanente se borra payload; corregir configuración y solicitar
un enlace nuevo desde la aplicación (respetando cooldown). No revivir tokens vencidos
ni cambiar estados manualmente para reenviar mensajes secretos. Una contraseña ya
cambiada sigue cambiada aunque la notificación falle.

La limpieza al iniciar worker y cada hora elimina contadores con más de un día;
purga payload de pendientes vencidos; elimina sesiones, resets, invitaciones, outbox e historial
**de seguridad/correo** de más de `SECURITY_RETENTION_DAYS=30` según su expiración o
creación. La auditoría electoral no se elimina. No ejecutar dos políticas distintas
sobre estas tablas sin coordinación. Monitorear cola pendiente antigua, failed y
salud/proceso del worker; la API sola no envía correo.

## Producción y claves

Producción exige `APP_ENV=production`, `DEBUG=false`, HTTPS, `COOKIE_SECURE=true`,
CORS explícito HTTPS, `FRONTEND_URL` canónica y SMTP `starttls` o `ssl` con certificado
verificado. `none` solo se acepta para localhost/127.0.0.1/mailpit en desarrollo.
Falta seleccionar proveedor, remitente/dominio, validar SPF/DKIM/DMARC y realizar
prueba externa a destinatario autorizado. Mailpit no demuestra entregabilidad.

Mantener API y frontend en el mismo sitio. Configurar frontend sin caché para páginas
de recuperación/invitación y `Referrer-Policy: no-referrer`. No registrar bodies de auth en
proxy/APM. Restringir cabeceras de IP al proxy confiable; en local no se aceptan.

Respaldar `MAIL_OUTBOX_KEY` en el gestor de secretos, separado del dump de BD.
Para rotarla, detener productores y drenar mensajes vigentes antes de cambiarla;
si se perdió/comprometió, purgar payloads pendientes y emitir enlaces nuevos. No
sobrescribir la clave con cola activa: esos mensajes serán indescifrables.
Rotación JWT y corte de clientes: [contrato de autenticación](AUTHENTICATION.md).

## Recuperación si todos los ADMIN están bloqueados

Primero esperar la expiración del bloqueo o usar recuperación por correo de un ADMIN
activo. Una cuenta desactivada requiere gestión autorizada, no se reactiva por reset.

Si no es posible, un operador autenticado en el servidor, con acceso autorizado al
entorno/BD, puede ejecutar desde `backend/`:

```bash
.venv/bin/python -m app.commands.unlock_account --user-id ID --operator IDENTIDAD_OPERADOR --reason 'Motivo documentado del incidente'
```

El comando conserva contraseña, rol y activación, limpia solo bloqueo temporal y
registra `auth.operator_unlock` con operador/motivo. No tiene endpoint público,
clave universal ni crea ADMIN. El control de identidad del operador corresponde
al acceso del host/SSH; revisar la auditoría después de usarlo. No poner contraseñas
ni datos de candidatos en el motivo.

## Verificación reproducible

Desde backend: `python -m pytest -q`; adicionalmente,
`SECURITY_POSTGRES_TESTS=1 python -m pytest tests/test_security_postgres.py -q`.
Esta suite requiere PostgreSQL local y permiso de crear BD; genera nombres aleatorios,
aplica Alembic, verifica concurrencia/upgrade/downgrade y elimina solo sus propias bases.
Desde frontend: `npm run test`, `npm run build`, `npm run lint`.

Recorrido manual: login → Seguridad → sesiones/reauth; cinco fallos sobre una cuenta
sintética → ADMIN desbloquea; «Olvidé mi contraseña» → Mailpit → enlace → nueva clave
→ login. La clave anterior, access y refresh previos deben rechazarse, el enlace no
puede reutilizarse y el APODERADO no ve controles ADMIN. Probar recarga y dos pestañas.

Fuentes: [Mailpit Docker](https://mailpit.axllent.org/docs/install/docker/),
[Argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/howto.html),
[OWASP recuperación](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html).

## Invitaciones, migración y despliegue coordinado

`INVITATION_EXPIRE_HOURS=48`, `INVITATION_HOURLY_LIMIT=20` y
`MAIL_COOLDOWN_SECONDS=60` están en `backend/.env.example`. El remitente y transporte
son los mismos que recuperación. La outbox de invitación tiene `user_id=NULL`,
`invitation_id` y digest de generación; el worker revalida autorización del invitador,
estado, digest y vencimiento antes de enviar. El cuerpo cifrado se purga al enviar,
cancelar o fallar definitivamente. Las invitaciones se retienen 30 días desde su
vencimiento, según `SECURITY_RETENTION_DAYS`; no se borran usuarios aceptados.

Antes de migrar, hacer backup y verificar restauración en una base aislada. Detener
API y worker; conservar dump y clave de cifrado por canales separados. La migración
`a72e903d418f` verifica colisiones `lower(trim(email))` sin imprimir correos y aborta
si hay alguna. Un operador autorizado debe resolver esas cuentas con sus titulares;
no aplicar normalización destructiva, fusión ni eliminación automática. Volver a
intentar el upgrade cuando el conflicto esté resuelto.

Aplicar Alembic, desplegar API/frontend/worker de la misma revisión y reiniciar los
tres. Verificar `alembic current`, `alembic heads` y `alembic check`, capturador/SMTP,
login legacy e invitación antes de habilitar altas. Los JWT anteriores al corte de
Task 16 son inválidos; las sesiones nuevas tienen vencimiento absoluto de siete días,
aunque se renueven. No ejecutar workers viejos con el esquema nuevo.

Rollback de Task 20: detener los tres procesos y respaldar; downgrade a
`6cb192ebc9fe` elimina invitaciones, sus correos y marcas de verificación, pero
conserva usuarios ya creados y asignaciones. Los enlaces emitidos dejan de tener un
registro válido. Para recuperar invitaciones y evidencia de verificación, restaurar
el backup completo y su clave; un upgrade solo no reconstruye esa información.
La suite PostgreSQL comprueba backup/restore con `pg_dump -Fc` y `pg_restore` de
PostgreSQL 17 dentro de Docker, exclusivamente sobre bases desechables de prueba.
Para esa prueba se requiere Docker Compose además del permiso de crear bases.

## Monitoreo y respuesta

- Vigilar crecimiento de `mail_outbox` en pending/failed y antigüedad, proceso worker,
  tasa de 429, bloqueos y eventos `auth.refresh_replay`. Correlacionar por IDs,
  nunca copiar tokens, destinatarios o cuerpos a logs externos.
- Ante abuso de bloqueo, mantener las sesiones válidas y cuotas; revisar IP del proxy
  confiable y recuperación del titular. No desactivar cuentas masivamente por fallos.
- Ante compromiso de una cuenta: desactivar APODERADO desde gestión (revoca sesiones
  y resets), cancelar invitaciones sospechosas y restablecer credencial por flujo
  autorizado. ADMIN dispone de cierre propio de todas sus sesiones. Incidentes de
  ADMIN requieren operador autorizado para desactivación/revisión de rol; no hay
  endpoint público que cree ni eleve administradores.
- Ante secreto JWT comprometido, retirar `kid` de confianza y rotar clave; no mantener
  la clave comprometida en anteriores. Ante outbox comprometida, cancelar/purgar los
  mensajes y enlaces afectados antes de generar nuevos; conservar evidencia mínima.
- MFA/passkeys/SSO no están implementados. Evaluar MFA para ADMIN antes de un
  despliegue sensible. Estas pruebas no certifican cumplimiento NIST/ASVS.

La habilitación productiva sigue abierta hasta verificar HTTPS, cookies Secure en
el dominio real, proxy/CORS, SMTP autorizado, SPF/DKIM/DMARC y recepción externa.
Mailpit solo demuestra el recorrido local. La inspección de un enlace no equivale
a validación de identidad electoral ni a consulta RENAPER.

## Task 22: despliegue y documentos de primer acceso

Aplicar `python -m alembic upgrade head` desde backend con su entorno cargado.
Head: `b8316d72c4ef`, sobre `a72e903d418f`. Agrega tres columnas nullable a `users`
y una restricción de integridad; no modifica usuarios, asignaciones o sesiones.
Desplegar API y frontend coordinadamente: clientes anteriores no presentan el paso
nuevo y recibirán 403 hasta actualizarse. Reiniciar procesos que cargan código,
incluido el worker si se despliega toda la versión. No se agregan variables de entorno.

Fuente única: `backend/app/legal/documents.json` desde raíz. Antes de publicar
textos definitivos, obtener revisión institucional, completar datos pendientes,
aumentar la versión y actualizar fecha/aviso/contenido. Reiniciar API en todos los
workers con la misma versión. El hash detecta cambios del contenido leído durante
la primera aceptación; no modificar contenido conservando deliberadamente la misma
versión. Cada cuenta conserva su instantánea original aunque cambie el documento
actual. No hay editor de textos en la UI ni reaceptación automática por versión.

La limpieza de auth/mail no elimina los campos de aceptación ni la auditoría
`legal.terms_accepted`. No registrar cuerpos con credenciales ni sumar IP/dispositivo
al registro de aceptación. ADMIN no puede aceptar por otra persona.

Rollback: respaldar la base antes del despliegue. Volver a `a72e903d418f` elimina
columnas/evidencia de aceptación; conserva cuentas y datos electorales. El código
anterior no aplica esta restricción. Reaplicar la migración deja aceptación pendiente;
para recuperar evidencia previa hace falta restaurar el respaldo correspondiente.
No ejecutar downgrade sobre datos operativos como una reparación rutinaria.
