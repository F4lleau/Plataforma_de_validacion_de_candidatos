# Envío, revisión, reportes y auditoría

Implementación local de Tasks 10–15, actualizada al 22/09/2026. Las plantillas
siguen siendo de prueba. RENAPER fue retirado del alcance por el usuario.

## Composición y estados

La regla vinculada a cada lista es una versión inmutable. Se comprueban cantidad
exacta, posiciones, nombres/grupos de cargos, identidad y contexto de candidaturas,
DNI repetidos, paridad global F/M y alternancia cuando la versión lo exige.
La demo usa Diputados 24 (16 titulares + 8 suplentes) sin alternancia y Consejos
22 posiciones genéricas con alternancia. No constituyen una plantilla oficial.
Las categorías de género sin política confirmada conservan el registro y requieren
resolver la composición antes de enviar; nunca se elimina al candidato.

El usuario confirmó para pruebas: lista incompleta/composición inválida no se envía;
lista completa con afiliación observada o requisitos pendientes puede enviarse a revisión.

| Acción / condición | Estado resultante | Edición de lista y candidatos |
| --- | --- | --- |
| Crear o corregir | `borrador` | Sí, dentro de plazo |
| Evaluar/enviar con posiciones faltantes o sin plantilla | `incompleta` | Sí |
| Evaluar/enviar con otro incumplimiento de composición | `rechazada_composicion` | Sí; UI: Composición observada |
| Enviar composición correcta, controles pendientes/observados | `enviada_admin` | No |
| Enviar con todos los obligatorios verificados y reglas confirmadas | `aprobada_sistema` | No |

`en_validacion` es un estado interno de la transacción, no una cola asíncrona.
`POST /lists/{id}/evaluate` persiste evaluación pero no envía. `POST /lists/{id}/submit`
revalida contra el padrón vigente y la configuración actual; devuelve `submitted`,
`already_submitted`, `state`, `composition` cuando se evaluó, `submitted_at` y
`approval_blockers`. Un intento con composición inválida devuelve HTTP 200 y
`submitted=false`, sin evento de envío. Conflictos de permisos/plazo/lectura son 403/409.

Se bloquea la fila de lista y la elección, y se comparte el lock transaccional del
importador de padrón. Doble envío es idempotente. El envío y la aprobación son eventos
distintos: el primero identifica al usuario; el segundo al sistema y referencia al
primero. La evaluación conserva reglas, revisiones de candidatos y resultados/evidencias
mínimas usados al enviar. No se ofrece reapertura ni decisión manual inventada.
ADMIN puede mantener asignaciones de acceso, sin editar el contenido enviado.

Aprobar exige composición OK, plantilla no experimental, otros requisitos confirmados
y todos los controles obligatorios OK de la revisión actual: requisitos del cargo
y afiliación cuando es requerida. La aprobación positiva se verifica con padrón y
reglas sintéticos en tests aislados; no acredita reglas institucionales reales.
RENAPER no se evalúa, aunque una versión histórica conserve `requires_renaper=true`.
Cambios posteriores del padrón/fecha electoral se muestran como controles pendientes;
una aprobación histórica conserva su evidencia del momento del envío.

## Consultas y permisos

Todos los paths siguientes tienen prefijo `/api/v1`. ADMIN consulta globalmente;
APODERADO necesita módulo habilitado y asignación explícita a la lista.

| Método / path | Uso |
| --- | --- |
| GET `/lists/{id}` | Datos legibles, asignados, regla, candidatos/controles/historial y composición |
| POST `/lists/{id}/evaluate`, `/submit` | Evaluar/enviar lista autorizada |
| GET `/admin/lists` | Bandeja ADMIN paginada |
| GET `/admin/candidate-review` | Observaciones actuales, nombres/DNI y vínculos a listas |
| GET `/candidates/review` | Compatibilidad ADMIN: array enriquecido, page=1/page_size=100 por defecto |
| GET `/dashboard/summary` | Métricas y últimas seis listas por alcance del usuario |
| GET `/admin/reports` | Resumen y distribución por estado/cargo |
| GET `/admin/exports/lists?format=xlsx\|csv` | Listas filtradas completas |
| GET `/admin/exports/reports?format=xlsx\|pdf` | Reporte filtrado completo |
| GET `/admin/exports/padron?format=xlsx\|csv` | Padrón vigente filtrado, 18 campos |
| GET `/admin/audit`, `/admin/audit/{id}` | Historial y detalle de eventos |

Listas, dashboard, reportes y sus exportaciones comparten filtros `election_id`,
`office_id`, `municipality_id`, `apoderado_id`, `status`, `search` (nombre/número).
La bandeja usa `page=1`, `page_size=25` (máximo 100), ID descendente estable. Las últimas
listas usan ese mismo orden de creación; registros heredados pueden carecer de fecha.
El selector explicita todas las elecciones autorizadas o una elección elegida.

Estados son excluyentes. Tasa de aprobación = aprobadas / total de listas filtradas;
con cero listas es 0%. Candidatos cuenta posiciones cargadas en las listas seleccionadas,
no personas únicas entre listas. Sin filtros, apoderados activos cuenta todas las cuentas
activas; con filtros cuenta quienes tienen asignación en esas listas. Los módulos del
apoderado respetan la elección seleccionada y el dashboard no expone contadores globales.
La navegación vuelve a consultar datos al montar cada pantalla; cambios en detalle
incrementan la revisión local. No hay polling ni promesa de actualización en tiempo real.

## Archivos y límites

Listas/reportes: número, lista, elección, cargo, localidad, cantidad, estado y apoderados.
CSV UTF-8 BOM; XLSX con hoja Datos y hoja Información (filtros, generación UTC, totales).
PDF A4 horizontal, texto ajustado, encabezado repetido y pie numerado con hora UTC.
El filtro aparece con nombres legibles. XLSX/CSV del padrón usan los 18 campos del manual;
no exponen IDs internos, hashes ni lotes ajenos. Se exporta todo el filtro, nunca solo
los 25 registros visibles. El padrón comparte búsqueda/sección/circuito/estado con su tabla.

Límite explícito: 50.000 registros por descarga, 5.000 listas en PDF. Superarlo devuelve
413 con indicación de acotar filtros; no se trunca silenciosamente. XLSX usa escritura
secuencial y salida en memoria limitada por esa cantidad. Prueba de volumen: 10.000 filas
× 18 columnas; no es un benchmark de concurrencia productiva.

Las celdas XLSX de texto no se interpretan como fórmulas. CSV antepone apóstrofo a valores
con prefijos de fórmula. DNI conserva ceros como texto en XLSX y en el contenido CSV;
al abrir CSV en Excel hay que importar Matrícula como Texto para evitar inferencia numérica.
Las nuevas importaciones conservan tildes en nombres, profesión y domicilio; la columna
auxiliar de búsqueda se normaliza. No se reconstruyen tildes perdidas en lotes anteriores.

Descargas usan Bearer, MIME y Content-Disposition expuesto por CORS. El cliente central
maneja 401/errores JSON y rechaza HTML, antes de crear un archivo. Cada exportación exitosa
registra tipo, filtros, filas y/o lote; no registra el contenido del padrón.

## Auditoría e historial

Consulta ADMIN paginada: `actor_id`, `action`, `entity_type`, `entity_id`, `list_id`,
`date_from`, `date_to`. Días inclusivos en Argentina; registros almacenados en UTC.
`list_id` incluye eventos de lista y de sus candidatos. Orden por ID descendente.
Los usuarios desactivados conservan atribución. No hay endpoint de borrar/editar eventos.

Se capturan configuración/reglas, usuarios/módulos, asignaciones, importaciones,
listas, candidatos (incluida alta ADMIN heredada), evaluaciones, envíos, aprobación
sistémica y exportaciones. Mutación/evento comparten transacción; importación fallida
registra fallo, sin activar datos. El registro común filtra claves sensibles y URLs
con credenciales; las respuestas de consulta vuelven a filtrar datos históricos.

Las validaciones de candidato conservan una fila por tipo/revisión: reintentar la misma
revisión actualiza ese resultado. Auditoría agrega un evento de evaluación con antes/después
de estados, lote y reglas para conservar el recorrido. Envío guarda un snapshot adicional
inmutable. El historial de revisiones no debe confundirse con vigencia frente al padrón actual.
Las acciones anteriores sin captura no se inventan retroactivamente.
