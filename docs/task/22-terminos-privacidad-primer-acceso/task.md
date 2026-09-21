# TASK 22 — First-Login Terms Acceptance and Privacy Documents

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado: implementada y verificada localmente el 21/09/2026. Textos definitivos pendientes de revisión institucional.**

**Dependencias:** Tasks 16, 20 y 21; auditoría de Task 14.
**Fuente:** solicitud del usuario del 21/09/2026; no procede del PDF electoral.
**Cobertura:** AUTH-10 y AUTH-11 del [plan de login](../LOGIN_SEGURIDAD.md).

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`,
`frontend/AGENTS.md`, `docs/AUTHENTICATION.md`, `docs/AUTH_OPERATIONS.md`,
`docs/INTERFAZ_VISUAL.md` y los estados de las dependencias. Rutas desde la raíz.

==================================================
## OBJETIVO
==================================================

Solicitar aceptación explícita de los términos y condiciones una única vez por
cuenta, después de validar las credenciales y antes de permitir el ingreso a las
funciones de la aplicación. Permitir consultar términos y políticas de privacidad
en modales reutilizados desde login y desde el footer de la app.

Los documentos tendrán inicialmente textos provisorios identificados como tales.
La aceptación requerida corresponde a **términos y condiciones**; consultar las
políticas no registra consentimiento adicional ni exige otro checkbox.

## Punto de partida verificado

- Task 20 crea cuenta y contraseña al aceptar la invitación; después dirige a login,
  sin iniciar sesión automáticamente.
- `Login.tsx` y `auth.store.ts` actualmente habilitan ingreso al autenticar;
  `ProtectedRoute.tsx` controla autenticación y rol.
- `User` no tiene registro de aceptación de términos. La API verifica sesión,
  usuario activo y permisos, pero no esta condición adicional.
- `AppLayout.tsx` ya tiene footer común con enlace de ayuda; agregar allí las consultas.
- No se encontró un flujo existente de términos o privacidad en las capas revisadas.

==================================================
## 1. AUDITORÍA Y REGLAS DEL FLUJO
==================================================

- [x] Revisar rama, estado de Git, instrucciones y contratos reales antes de implementar.
- [x] Definir estados diferenciados: sin sesión, identidad autenticada con aceptación
  pendiente y acceso habilitado. No confundir autenticación con acceso a módulos.
- [x] Aplicar la condición tanto a ADMIN como a APODERADO, conservando permisos vigentes.
- [x] Adoptar para cuentas existentes sin registro la aceptación en el siguiente
  acceso/restauración de sesión. No inventar una aceptación retroactiva ni inferirla
  de `created_at`, login histórico, email verificado o aceptación de invitación.
- [x] Mantener la aceptación por cuenta entre dispositivos, navegadores, logout,
  cambio/reset de contraseña y desbloqueo. No depender de localStorage ni cookies.
- [x] No exigir aceptación nuevamente por un cambio de versión del documento en
  esta task: el requisito es una única vez. Una política futura de reaceptación
  requerirá alcance explícito; preservar qué texto aceptó originalmente cada cuenta.

==================================================
## 2. LOGIN Y ACEPTACIÓN INICIAL
==================================================

- [x] Mostrar debajo del botón «Ingresar» enlaces «Ver términos y condiciones» y
  «Ver políticas de privacidad», disponibles incluso antes de autenticar.
- [x] Validar email/contraseña mediante el login existente. No exponer si una cuenta
  aceptó términos antes de validar sus credenciales ni agregar una consulta pública por email.
- [x] Si falta aceptación, permanecer en la pantalla de acceso: mostrar debajo del
  botón de login el aviso «Antes de ingresar, aceptá los términos y condiciones»,
  checkbox inicialmente desmarcado y acción «Aceptar y continuar».
- [x] Usar como etiqueta del checkbox «He leído y acepto los términos y condiciones»
  con enlace al modal. Incluir cerca el enlace a políticas, sin aceptación implícita
  por abrir/cerrar documentos o por pulsar «Ingresar».
- [x] En este estado, evitar nuevos envíos del formulario de credenciales y limpiar
  la contraseña de memoria del formulario; no pedirla otra vez para aceptar mientras
  la sesión sea válida. Ofrecer «Salir / usar otra cuenta» con cierre de sesión.
- [x] Deshabilitar «Aceptar y continuar» sin checkbox y durante el envío; persistir
  antes de navegar. Al fallar la red/servidor, mostrar error y permitir reintentar
  sin habilitar acceso ni registrar éxito solo en el navegador.
- [x] Si no acepta, puede leer documentos o salir; no ingresa a módulos ni se elimina
  o desactiva su cuenta. Cerrar el modal no cancela ni completa la aceptación.
- [x] Si ya aceptó, ingresar normalmente sin aviso, checkbox ni paso adicional.
- [x] Respetar el destino interno permitido solicitado originalmente o usar dashboard;
  no permitir redirecciones externas o a rutas sin autorización.
- [x] Cubrir recarga, atrás, URL directa, sesión restaurada y múltiples pestañas sin
  mostrar fugazmente datos protegidos. Una sesión vencida vuelve a login sin aceptación ficticia.

==================================================
## 3. DOCUMENTOS Y MODALES REUTILIZABLES
==================================================

- [x] Crear una única fuente versionada para cada documento: identificador, título,
  versión, fecha y contenido; identificar claramente la versión como provisoria.
- [x] Conservar contenido de versiones aceptadas o una instantánea verificable;
  no reemplazar un texto manteniendo el mismo identificador de versión.
- [x] Implementar un modal reutilizable con contenido de términos o políticas,
  utilizado tanto en login como dentro de la app, sin duplicar textos entre pantallas.
- [x] Agregar al footer común enlaces «Términos y condiciones» y «Políticas de
  privacidad», visibles para ambos roles y en móvil, conservando el enlace de ayuda.
- [x] Abrir en la misma pantalla y conservar formulario, ruta y trabajo en curso.
  Leer desde el footer no vuelve a pedir aceptación ni modifica su registro.
- [x] Incluir título accesible, foco inicial, contención de foco, cierre visible,
  Escape y devolución del foco al enlace de origen. Permitir scroll del contenido,
  navegación por teclado y lectura en pantallas pequeñas sin desbordamiento horizontal.
- [x] No condicionar aceptación a llegar al final del scroll ni marcar el checkbox
  automáticamente. Abrir un documento nunca ejecuta una mutación.

### Borradores de contenido para pruebas

Usar los siguientes textos como base, con un aviso visible en ambos documentos:
**«Texto provisorio para pruebas. Pendiente de revisión institucional antes de su
uso en producción.»** No presentarlos como documentos legales aprobados.

**Términos y condiciones — versión provisional 0.1**

> Esta plataforma permite a usuarios autorizados gestionar listas, candidatos y
> validaciones para la Junta Electoral del Partido Justicialista, Distrito Chaco.
> Al utilizarla, te comprometés a cuidar tus credenciales, cargar información que
> consideres correcta y realizar únicamente las acciones correspondientes a tu rol
> y asignaciones. La información consultada debe utilizarse para las tareas
> electorales autorizadas. Las validaciones y observaciones de la plataforma
> acompañan la revisión administrativa y no sustituyen las decisiones de la Junta
> Electoral. Ante errores o inconvenientes, utilizá el canal de ayuda disponible
> en la aplicación.

**Políticas de privacidad — versión provisional 0.1**

> La plataforma utiliza información de las cuentas, listas y candidatos, el padrón
> cargado por la administración y registros de actividad para gestionar el trabajo
> electoral, controlar accesos y permitir la revisión de operaciones. El acceso a
> la información depende del rol y de las asignaciones de cada usuario. Los flujos
> de invitación y recuperación utilizan el correo de la cuenta. Este documento
> provisorio describe el funcionamiento general; falta completar y revisar la
> información institucional sobre responsables, contacto, conservación de datos,
> destinatarios y canales para consultas sobre privacidad.

- [x] Contrastar los borradores con el comportamiento final y mostrar versión/fecha
  real de publicación. No inventar responsables, domicilios, proveedores, plazos,
  bases legales, transferencias o garantías de seguridad.
- [x] Registrar como pendiente externo la revisión y provisión del texto definitivo;
  el desarrollo y las pruebas locales pueden completarse con estos borradores.

==================================================
## 4. PERSISTENCIA, API Y CONTROL DE ACCESO
==================================================

- [x] Crear migración Alembic aditiva para guardar por usuario la primera aceptación:
  fecha/hora UTC del servidor y versión de términos vinculada a su contenido.
  Preservar cuentas, roles, listas, asignaciones y sesiones existentes.
- [x] Asegurar unicidad por cuenta e idempotencia ante reintentos/doble clic/pestañas
  concurrentes; no sobrescribir fecha ni versión de la aceptación original.
- [x] Exponer el estado necesario en login, restauración de sesión y perfil mínimo;
  el backend es la autoridad, sin confiar en un booleano del cliente o JWT obsoleto.
- [x] Implementar lectura pública de documentos y POST autenticado para aceptar,
  `GET /api/v1/legal/documents` y `POST /api/v1/auth/terms/accept`.
  Contratos implementados y documentados en `docs/AUTHENTICATION.md`.
- [x] Validar aceptación explícita y versión efectivamente presentada; no aceptar
  usuario, fecha o texto arbitrarios desde el cliente. Si cambia el texto antes de
  confirmar una primera aceptación, solicitar lectura/confirmación de la versión nueva.
- [x] Mantener sesión pendiente con acceso restringido en servidor. Permitir solo
  documentos, identidad/estado mínimo, aceptación, renovación y cierre de sesión;
  revisar explícitamente cualquier otra excepción necesaria, sin acceso electoral
  o administrativo, exportaciones, archivos ni cargas mientras falte aceptación.
- [x] Aplicar la restricción centralmente y revisar cobertura de todas las rutas;
  no basta con el guard del frontend. Devolver error identificable, por ejemplo
  `403 TERMS_ACCEPTANCE_REQUIRED`, distinto de sesión inválida y falta de rol.
- [x] Conservar JWT, rotación, revocación y CSRF existentes. Separar autenticación de
  autorización para no bloquear el endpoint que permite aceptar ni crear bucles de refresh.
- [x] Persistir aceptación y evento de auditoría en una transacción, con usuario,
  fecha y versión. No registrar contraseñas, tokens ni cuerpos completos, ni sumar
  IP/dispositivo como evidencia por defecto. La limpieza temporal de auth/mail no
  debe borrar el registro duradero de aceptación de una cuenta vigente.
- [x] No permitir que ADMIN acepte en nombre de otro usuario ni que edición de perfil,
  invitación, reset o desbloqueo modifiquen el registro.
- [x] Mantener endpoint → service → repository; documentar migración y rollback.

==================================================
## 5. CHECKLIST DE ACEPTACIÓN Y REGRESIÓN
==================================================

- [x] Invitación → datos y clave → login correcto → aviso → leer modales → aceptar
  → ingresar con los módulos/listas asignados, sin cambios de rol ni asignaciones.
- [x] Segundo login y otro navegador/dispositivo: no piden aceptación nuevamente.
- [x] ADMIN y APODERADO existentes sin registro: solicitan aceptación una vez;
  migración no fabrica evidencia histórica.
- [x] Credenciales inválidas, cuenta bloqueada/inactiva y sesión revocada mantienen
  sus controles; no se puede aceptar sin identidad/sesión válida.
- [x] Sin aceptar: URL directa, API, refresh y manipulación del estado del cliente
  no habilitan lecturas ni escrituras protegidas.
- [x] Checkbox desmarcado, lectura/cierre del modal o abandono no persisten aceptación.
- [x] Reintentos, concurrencia, caída de red y rollback transaccional no duplican
  evidencia ni habilitan acceso si la persistencia falló.
- [x] Reset/cambio de clave, desbloqueo y logout conservan aceptación ya registrada.
- [x] Actualizar documentos no exige reaceptación a cuentas que ya aceptaron;
  primera aceptación concurrente con actualización detecta versión desactualizada.
- [x] Modales idénticos en login/footer, navegación por teclado, Escape, foco,
  scroll, móvil y formularios en curso verificados en navegador.
- [x] Ejecutar tests backend apropiados, pruebas de migración con base vacía/existente,
  tests frontend, build y lint; registrar comandos y resultados reales.
- [x] Verificar `git diff --check`, ausencia de secretos/datos reales y regresión de
  autenticación/RBAC; no modificar reglas electorales ni integración RENAPER.

==================================================
## 6. DOCUMENTACIÓN Y CIERRE
==================================================

- [x] Actualizar contratos de autenticación, manuales por rol y operación cuando
  exista implementación; explicar el comportamiento para cuentas existentes.
- [x] Actualizar `status.md`, checklist, índice y matriz AUTH con evidencia;
  crear `report.md` al ejecutar, no como prueba de una implementación inexistente.
- [x] Separar aceptación funcional local de revisión institucional de los textos.
- [x] No hacer commit/push salvo instrucción expresa.

## Fuera de alcance

Redacción legal definitiva, certificación de cumplimiento, consentimiento de
candidatos/terceros, firma electrónica, editor administrativo de documentos,
reaceptación periódica o por versión y cambios de reglas electorales. La aceptación
de un usuario operativo no representa consentimiento de personas incluidas en el padrón.
