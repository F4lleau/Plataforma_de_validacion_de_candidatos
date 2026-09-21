# Configuración y carga electoral — Tasks 04 a 09

Implementación local del 20/09/2026. El usuario autorizó datos/plantillas de prueba y
preparar RENAPER sin una API disponible. Las plantillas de prueba no son normativa.

## Recorrido

1. ADMIN abre **Configuración**, crea/edita elección, apertura/cierre, cargos y localidades.
2. Selecciona elección y cargo, configura reglas y posiciones. **Generar plantilla de prueba**
   propone 24 posiciones (16 titulares + 8 suplentes) para Diputados o 22 posiciones
   genéricas para Consejos. Es editable y queda marcada como prueba.
3. ADMIN invita un apoderado por correo en **Apoderados → Invitaciones**, con módulos por
   elección/cargo/distrito. Puede editarlo, desactivarlo o enviar recuperación por correo desde Seguridad de cuenta.
4. APODERADO crea una lista dentro de la ventana de carga. Se asigna explícitamente al
   creador. ADMIN puede crear listas y asignarlas a uno o varios apoderados con módulo compatible.
5. **Continuar carga** abre el detalle y la plantilla de esa lista. Permite agregar,
   corregir y guardar candidatos, consultar los controles y volver a validar.
6. **Padrón** permite importación XLSX, consulta paginada, filtros, indicadores e historial.

Envío, bandeja, dashboards, exportaciones y auditoría se completaron en Tasks 10–14.
Ver [contratos y estados](SUBMISSION_REPORTING_AUDIT.md). RENAPER real sigue pendiente.

## Reglas y decisiones técnicas

- Pueden coexistir elecciones activas. Las fechas de carga son días inclusivos en
  `America/Argentina/Cordoba`; ambas fechas deben existir para habilitar carga.
- Reglas por elección/cargo, con versiones inmutables. Guardar una configuración idéntica
  reutiliza la versión. Las listas guardan `rule_version_id` y conservan esa versión.
- La edad usa la fecha configurable: electoral, cierre o pendiente. Configuración de
  prueba: 25/21 años y fecha electoral; no constituye confirmación institucional.
  Para nacidos el 29/02 se cumple el año el 01/03 cuando el año no es bisiesto.
- Ciudadanía, antigüedad y residencia no se inventan. Por defecto, otros requisitos
  siguen pendientes. Una plantilla de prueba tampoco produce requisitos definitivos OK.
- Alternancia se lee de la versión: no obligatoria en Diputados, requerida en Consejos
  para las plantillas de prueba. Categorías de género sin política confirmada producen
  observación de composición que impide el envío hasta definir la política, sin impedir el registro.
- Número único dentro de elección, cargo y distrito. Se serializa la creación/edición
  con bloqueo de la elección. El nombre no es identificador único.
- Asignación compartida explícita por lista, además del módulo. Revocar cualquiera
  retira el acceso en la próxima solicitud. `created_by` se conserva como autor histórico.
- Se editan listas `borrador`/`incompleta`/`rechazada_composicion` dentro de la ventana.
  Las enviadas/aprobadas quedan en lectura. No se implementó reapertura sin criterio institucional.
- No se impide que la misma persona participe en distintas listas/elecciones: no hay
  una prohibición institucional confirmada. Sí se rechaza DNI repetido dentro de una
  lista y posición ocupada. Cambiar datos de una persona compartida requiere corrección
  administrativa coordinada, todavía fuera de esta UI; evita alterar otra lista sin permiso.

## Borradores y validaciones

Un borrador requiere DNI, nombre, apellido, fecha de nacimiento, género y posición.
No se guardan personas con identidad parcial ni se relajan columnas no nulas. La lista
puede permanecer incompleta. **Guardar borrador** registra afiliación y deja requisitos
pendientes; **Guardar y validar** también evalúa edad/requisitos. Ambos guardan aun cuando
el candidato está ausente/inactivo en padrón.

Persona, candidatura, posición, validaciones y auditoría se guardan en una transacción.
Cada edición incrementa la revisión; los resultados anteriores conservan historial pero
no representan los datos corregidos. Revalidar la misma revisión actualiza un resultado
por control, sin duplicar la persona ni la candidatura. El contexto conserva versión de
reglas, lote y fechas: cambiar padrón/fechas obliga a revalidar el resultado dependiente.

RENAPER tiene un contrato interno `IdentityResult` y un cliente **no configurado**, sin
URL inventada, llamadas de red ni respuesta OK ficticia. Devuelve pendiente, origen y
`approvable=false`. Los dobles de prueba se usan solo en tests. La futura integración
necesitará contrato autorizado, adaptador HTTP, credenciales por entorno, timeout,
rate limits y prueba real; no se habilita con una variable ficticia.

## Padrón

Solo XLSX con openpyxl, máximo 20 MB / 500000 filas. XLS se rechaza explícitamente.
Se mapean los 18 campos del manual, normalizando encabezados, acentos y espacios.
Matrícula se interpreta provisionalmente como documento; no como número de afiliado.
Se conserva el formato simple DNI/Nombre/Apellido. DNI admite 7–9 dígitos, incluyendo
celdas numéricas enteras; no agrega el decimal `.0`. Fechas: Excel, DD/MM/AAAA,
AAAA-MM-DD o DD-MM-AAAA. Campos opcionales vacíos quedan nulos.

Si aparece una fila inválida, fecha inválida o DNI duplicado, el lote falla y conserva
el padrón vigente completo. El historial muestra hasta 30 errores con número de fila.
Un lote vacío no se activa. Las importaciones se serializan con advisory lock PostgreSQL
y conservan el índice único parcial de lote vigente.

Solo estado normalizado **ACTIVO** verifica afiliación; otros estados producen warning.
En formato simple sin columna de estado se mantiene compatibilidad como activo. Un
estado vacío en una columna presente queda sin informar. Confirmar estos catálogos con
una muestra oficial antes de uso institucional. El padrón no consulta ninguna API externa.

## Contratos HTTP

Prefijo `/api/v1`. Backend valida permisos independientemente de la navegación.

| Contrato | Acceso |
| --- | --- |
| GET/POST `/elections/`, `/offices/`, `/municipalities/`; PUT `/{id}` | GET autenticado y filtrado por módulos; escritura ADMIN |
| GET `/elections/{id}/rules`; POST `/elections/{id}/rules/{office_id}` | Lectura acotada; escritura ADMIN |
| GET/POST `/users/`; GET/PUT `/users/{id}` | ADMIN; únicamente apoderados en este flujo |
| GET `/auth/modules` | Módulos habilitados del usuario actual |
| GET `/auth/support` | Público; contacto opcional y recuperación asistida |
| GET/POST `/lists/`; GET `/lists/page` | Autenticado; asignación + módulo para APODERADO |
| GET/PUT `/lists/{id}` | Acceso a lista; PUT exige editable/ventana |
| PUT `/lists/{id}/assignments` | ADMIN; valida módulos de los destinatarios |
| POST `/lists/{id}/rules/adopt` | ADMIN; solo lista editable vacía |
| POST `/lists/{id}/candidates` | Alta transaccional en lista autorizada |
| PUT `/lists/{id}/candidates/{candidate_id}` | Edición en lista autorizada/editable |
| POST `/lists/{id}/candidates/{candidate_id}/validate` | Revalidación con igual alcance |
| GET `/padron`; GET `/padron/batches`; POST `/padron/import` | ADMIN |

`/lists/page`: `page`, `page_size` (1–100), `search`, `status`; responde items/total.
Se conserva GET `/lists/` como colección por compatibilidad. Padrón usa los mismos
parámetros de paginación más `search`, `section`, `circuit`, `state`.

El POST antiguo `/candidates` queda como compatibilidad administrativa; APODERADO debe
usar la carga contextual por lista. Los candidatos históricos sin vínculo no se exponen
al apoderado. El cálculo de composición ignora el tipo indicado por cliente y usa la
versión vinculada a la lista; no es aprobación.

## Migración y datos existentes

`dc5da19db749`: reglas versionadas, asignación por lista, fechas de carga, número/fecha
opcional en listas históricas, revisión de candidato y los diez campos faltantes del padrón.
`e271bb89a403`: restricciones de coherencia de fechas y cantidad positiva de posiciones.

La migración asigna explícitamente al creador cuando era APODERADO. Las listas creadas
por ADMIN requieren asignación manual. No inventa fechas históricas ni transforma las
plantillas de seis/ocho posiciones del seed en plantillas oficiales. Listas históricas
con candidatos conservan su contenido; para el nuevo flujo se crean nuevas listas con
versión. Las vacías pueden adoptar reglas desde API. No se borran usuarios ni padrones.

Se dejaron tres listas **DEMO tareas 04 a 09** y candidatos ficticios locales para recorrer
el flujo. El script de carga fue ejecutado y eliminado; no forma parte del repositorio.

## Recuperación y operación

Login incluye mostrar/ocultar contraseña y recuperación por correo. Desde Tasks 16–19,
ADMIN envía enlaces tras reautenticación; no asigna claves a cuentas existentes. Cambio/reset
y desactivación revocan sesiones inmediatamente. Ver [contrato vigente](AUTHENTICATION.md).
`SUPPORT_CONTACT` opcional en `backend/.env` permite mostrar el canal real de soporte,
sin inventar dirección. Nunca se devuelve hash ni contraseña en los contratos de usuarios.

Configuración y carga producen auditoría con actor/entidad/fecha y metadatos mínimos;
no se incluyen passwords ni respuesta íntegra de identidad. La pantalla ADMIN de
auditoría e historial contextual está implementada en Task 14.

## Actualización Tasks 10–15 (20/09/2026)

Envío transaccional, bandeja ADMIN, dashboards, reportes/exportaciones y auditoría
están implementados y verificados localmente. El contenido enviado queda en lectura.
Las reglas demo y RENAPER pendiente impiden afirmar aprobación institucional.
Ver `docs/SUBMISSION_REPORTING_AUDIT.md`, `docs/MANUAL_ADMIN.md`,
`docs/MANUAL_APODERADO.md` y `docs/task/INFORME_10_15.md` desde la raíz.
