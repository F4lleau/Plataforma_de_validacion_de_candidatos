# Cobertura del manual por capacidad

Fuente: [manual y criterio de lectura](FUENTE_MANUAL.md). Estado contrastado con el
repositorio después de Tasks 03–15 (20/09/2026). Las referencias de página incluyen las capturas;
«derivado» identifica trabajo técnico para hacer verificable la capacidad, no una
obligación textual adicional. Cada ID aparece en al menos una consigna.

| ID | Capacidad / criterio verificable | Fuente | Estado actual | Task responsable / apoyo |
| --- | --- | --- | --- | --- |
| CAP-01 | Login ADMIN/APODERADO, JWT, sesión persistente validada, logout, rutas por rol; mostrar contraseña/recuperación de la captura. | pp. 2–3, 8 | Implementado; sesión/roles/revocación/descarga 401 verificados. | 03, 05; regresión 15 |
| CAP-02 | Catálogos reales de elecciones, Diputados/Consejos y municipios, con habilitación. | pp. 2, 8, 11 | API y UI reales; catálogos activos por alcance. | 04 |
| CAP-03 | Elección activa, nombre de proceso, apertura/cierre de carga y guardado de configuración. | pp. 7–8 | Configuración y ventana inclusiva Argentina implementadas. | 04 |
| CAP-04 | Reglas parametrizadas por cargo: edades, afiliación, RENAPER, paridad, alternancia y cantidad. | pp. 8, 11 | Reglas versionadas configurables; criterios institucionales pendientes. | 04; ejecución 08–10 |
| CAP-05 | Alta/edición/activación/desactivación de apoderados; nombre/email/contraseña inicial segura. | pp. 5–6 | Gestión real de cuentas y recuperación asistida. | 05 |
| CAP-06 | Asignar uno/ambos módulos y municipio por elección; hacer efectiva revocación y aislamiento. | pp. 2, 6, 8–9 | Módulo + asignación explícita; aislamiento y revocación verificados. | 05, 07 |
| CAP-07 | Importar Excel oficial de 18 columnas, controlar lotes/vigencia y errores sin perder padrón previo. | p. 7 | XLSX de 18 campos, lote atómico y concurrencia; muestra oficial pendiente. | 06 |
| CAP-08 | Consulta de padrón con nombre/apellido/matrícula, filtros y tabla; total afiliados, secciones, última actualización. | p. 7 | Consulta/paginación/filtros/indicadores reales. | 06 |
| CAP-09 | Exportar padrón filtrado desde acción ADMIN. | p. 7, captura | XLSX/CSV ADMIN de todo el filtro, 18 campos, texto seguro. | 13; contrato/UI 06 |
| CAP-10 | Crear lista: nombre, número y cargo autorizado; Mis listas con búsqueda/estado, ver y continuar carga. | pp. 9, 11 | Crear/editar/listar listas con número/contexto/permisos reales. | 07 |
| CAP-11 | Plantillas/posiciones por cargo, titulares/suplentes, cantidades y orden definidos. | pp. 10–11; modelado derivado | Plantillas versionadas; demo 24=16+8 y 22; oficial pendiente. | 07; reglas 04 |
| CAP-12 | Seleccionar lista, DNI/nombres/apellidos/nacimiento/género/posición; guardar borrador, guardar-validar y corregir. | pp. 9–10 | Borrador, guardar-validar, corrección y vínculos transaccionales. | 08 |
| CAP-13 | Requisitos del cargo: edad mínima 25/21 con fecha de referencia acordada; ciudadanía citada sin criterio. | pp. 5, 8, 11 | Edad configurable calculada; requisitos no confirmados permanecen pendientes. | 08; configuración 04 |
| CAP-14 | Afiliación por padrón vigente; candidato ausente se guarda con warning y revisión. | pp. 5, 10–11 + AGENTS | Padrón vigente; ausencia guarda warning y permite continuar/enviar lista completa. | 06, 08 |
| CAP-15 | Identidad RENAPER obligatoria con proveedor real, estados honestos, fallo técnico y reintento controlado. | pp. 2, 5, 10–11 | Preparación local verificada; proveedor/API real diferidos por el usuario. | 09 |
| CAP-16 | Resultado inmediato/granular al guardar-validar, feedback de pendiente/error/corrección. | p. 10 | Controles granulares y reintento; RENAPER no configurado muestra pendiente. | 09; formulario 08 |
| CAP-17 | Composición exacta, paridad 50/50, alternancia según cargo, cargos/posiciones/duplicados. | pp. 5, 11 | Composición exacta y reglas por versión verificadas con ambas plantillas demo. | 10 |
| CAP-18 | Borrador → validación → envío ADMIN → aprobación automática solo si cumple; transiciones y corrección coherentes. | p. 11; estados pp. 4–5 | Envío idempotente y lectura posterior; aprobación preparada, positiva solo en tests aislados. | 10 |
| CAP-19 | Bandeja ADMIN de todas las listas, filtros/búsqueda, número/cargo/municipio/cantidad/estado/detalle. | pp. 2, 4 | Bandeja ADMIN filtrada/paginada y detalle enriquecido. | 11; exportación 13 |
| CAP-20 | Validaciones por lista y candidato: posiciones, paridad, alternancia, afiliación, requisitos, RENAPER y estado; revisión ADMIN. | p. 5 | Controles actuales/históricos por candidato, composición y revisión contextual. | 11 |
| CAP-21 | Dashboard ADMIN: total/aprobadas/enviadas/rechazadas/incompletas/apoderados activos y últimas listas. | pp. 3–4 | Métricas SQL reales, estados excluyentes y alcance electoral explícito. | 12 |
| CAP-22 | Dashboard APODERADO: módulos/municipio, sus listas, cantidades/fechas, crear y continuar carga. | pp. 8–9 | Panel por módulos/listas propias con fechas, cantidades y acciones reales. | 12; acciones 07–08 |
| CAP-23 | Reportes por cargo/localidad/estado/apoderado; totales/tasa de aprobación, gráficos por estado/cargo; Excel/PDF y listas Excel/CSV. | pp. 4–5 | Reportes/gráficos compartidos y archivos XLSX/CSV/PDF reales y verificados. | 13 |
| CAP-24 | ADMIN audita acciones y recorrido de listas; consulta historial atribuible. | pp. 2, 11 | Auditoría transaccional y consulta ADMIN filtrada/contextual, sin secretos. | 14; captura base 04 y tareas productoras |
| CAP-25 | Ayuda, reporte de errores, solicitud de credenciales y recuperación/contacto real. | pp. 3, 11 | Ayuda y recuperación asistida implementadas; contacto institucional configurable aún sin valor. | 05, 15 |
| CAP-26 | Aceptación end-to-end de ambos roles, manual actualizado y UI institucional responsive/accesible. | pp. 1–11; verificación derivada | Aceptación local y manuales completos; aceptación institucional externa pendiente. | 15; transversal 04–14 |

## Reglas y límites a conservar

- No volver a implementar login/RBAC ya comprobados en Task 03: extenderlos y probar regresión.
- La ausencia del padrón no bloquea registro; la aprobación automática sí requiere controles obligatorios satisfechos.
- Los prototipos no autorizan copiar personas, documentos ni passwords visibles.
- No declarar RENAPER, aprobación automática, exportaciones o auditoría como completados por existir sus archivos.
- Detalles no definidos del manual quedan en [DECISIONES.md](DECISIONES.md), no en requisitos inventados.

## Evidencia vigente

- CAP-01: suites auth backend/frontend y regresión 15; [autenticación](../AUTHENTICATION.md).
- CAP-02–08 y CAP-10–14: API/UI/configuración/padrón/listas/candidatos en
  [informe 04–09](INFORME_04_09.md), extendidos y regresados en 15.
- CAP-09 y CAP-17–24: [informe 10–15](INFORME_10_15.md), servicios y endpoints
  trazados en [contratos](../SUBMISSION_REPORTING_AUDIT.md); 37 tests específicos
  en `backend/tests/test_tasks_10_15.py` y recorridos reales en navegador.
- CAP-15–16: [Task 09](09-renaper-validacion-identidad/report.md), estados honestos;
  la verificación externa sigue pendiente. Un doble de tests no completa CAP-15.
- CAP-25–26: [guía ADMIN](../MANUAL_ADMIN.md), [guía APODERADO](../MANUAL_APODERADO.md),
  [recuperación/operación](../OPERACION_LOCAL.md), ayuda UI y aceptación local del informe 10–15.

La aceptación de producción requiere resolver las decisiones institucionales y ejecutar
la integración autorizada de identidad. La ausencia en padrón siempre conserva el registro.

## Ampliación de autenticación fuera del manual

La solicitud del usuario del 20/09/2026 agrega AUTH-01–AUTH-09: JWT/sesiones,
SMTP, bloqueo/desbloqueo, recuperación/cambio de clave e invitación/primer acceso.
Son capacidades **planificadas**, trazadas en [LOGIN_SEGURIDAD.md](LOGIN_SEGURIDAD.md)
y asignadas a Tasks 16–21. No se atribuyen al PDF ni modifican retrospectivamente
el cierre del alcance anterior.

En CAP-01, «revocación» de la evidencia previa se refiere a cambios de acceso por
usuario/rol/asignación y limpieza del cliente; no equivale a revocación individual
de JWT/sesiones en servidor. Esa capacidad sigue pendiente en Task 16.
