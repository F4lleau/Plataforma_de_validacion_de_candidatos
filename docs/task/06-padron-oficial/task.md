# TASK 06 — Official Membership Register Import, Search and History
> Estado al 20/09/2026: **Completada con muestras sintéticas**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 03, Task 04.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 7 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-07, CAP-08, CAP-09; ver [matriz](../CAPACIDADES.md).
**Decisiones:** [DECISIONES.md](../DECISIONES.md). Los ejemplos visuales no sustituyen reglas ni autorizan datos/credenciales de prueba.

Leer obligatoriamente antes de modificar código:

- `/AGENTS.md`
- `/backend/AGENTS.md`
- `/frontend/AGENTS.md`
- `/docs/PROJECT_CONTEXT.md`
- `/docs/BUSINESS_RULES.md`
- `/docs/AUTHENTICATION.md`
- La consigna, estado y evidencia de las dependencias; no asumir que un archivo equivale a una capacidad implementada.

==================================================
## OBJETIVO
==================================================

Adaptar el padrón Excel al formato del manual y completar consulta, filtros, indicadores y control de lotes. Mantener ausencia de afiliación como advertencia no bloqueante de carga.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `PartyMember`, `AffiliateImportBatch`, sus repositories, `AffiliateImportService`, `AffiliationValidationService`, `padron.py`, `Padron.tsx` y tests Task 02B. El importador actual solo resuelve columnas básicas y no representa todos los campos oficiales.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. MAPEO DE EXCEL
==================================================

- [ ] Resolver D11 sobre Matrícula/documento, tipos y fechas usando una muestra autorizada; no confundir matrícula con número de afiliado. **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [x] Cubrir las 18 columnas: Sección, Cod. Sección, Circuito, Cod. Circuito, Apellido, Nombre, Género, Tipo documento, Matrícula, Fecha nacimiento, Clase, Estado actual elector, Estado afiliación, Fecha afiliación, Analfabeto, Profesión, Fecha domicilio y Domicilio.
- [x] Normalizar encabezados/acentos/espacios y documentos preservando identidad; manejar vacíos, fechas Excel/texto, celdas numéricas y filas duplicadas con criterios explícitos.
- [x] Documentar obligatorios y opcionales y compatibilidad del formato simple previo; no declarar soporte .xls si la dependencia/lectura no está probada.

==================================================
## 3. PERSISTENCIA E IMPORTACIÓN
==================================================

- [x] Agregar por Alembic solo campos requeridos que falten, manteniendo histórico por lote.
- [x] Validar archivo/tamaño/estructura y procesar filas con resumen de válidas, inválidas y duplicadas; devolver errores accionables.
- [x] Activar el nuevo lote completo de forma atómica; un archivo fallido o sin filas válidas no reemplaza el padrón vigente.
- [x] Conservar imported_by=current_user.id, histórico y fecha real; evitar múltiples lotes vigentes bajo importaciones concurrentes.
- [x] Resolver estado de afiliación activo/inactivo según D06; no usar mera presencia de una fila inactiva como afiliación válida.

==================================================
## 4. CONSULTA E INDICADORES ADMIN
==================================================

- [x] Crear consultas paginadas del padrón vigente con búsqueda por apellido/nombre/matrícula y filtros por sección/circuito/estado aplicables.
- [x] Devolver columnas del manual, total de afiliados, número real de secciones y fecha de última actualización.
- [x] Agregar consulta de lotes y resultados de importación sin mezclar históricos con afiliaciones vigentes.
- [x] Proteger lectura/importación/exportación con ADMIN y auditar actualización de padrón.

==================================================
## 5. FRONTEND PADRÓN
==================================================

- [x] Ampliar la pantalla actual con tarjetas de indicadores, tabla paginada, búsqueda y filtros; conservar upload real.
- [x] Mostrar estados de progreso/carga/error/vacío, resumen de importación y datos del lote activo.
- [x] Conservar tabla legible en móvil mediante columnas priorizadas/scroll accesible; no cargar todo el padrón en memoria del navegador.
- [x] Conectar el botón Exportar con Task 13; hasta entonces indicarlo como pendiente o no mostrarlo.

==================================================
## 6. TESTS
==================================================

- [x] Excel con los 18 campos, aliases, documento numérico/texto, duplicados, vacíos y fechas inválidas.
- [x] Un fallo o importación vacía conserva el padrón activo; concurrencia no produce dos lotes vigentes.
- [x] Búsqueda, filtros y paginación coinciden con totales; ADMIN permitido y APODERADO/anónimo denegados.
- [x] DNI afiliado válido y candidato ausente/inactivo mantienen el contrato verified/warning y revisión administrativa.

==================================================
## 7. VERIFICACIÓN
==================================================

- [x] Mantener separación endpoint → service → repository → model; roles/permisos se validan en backend.
- [x] Ejecutar desde backend, con entorno configurado: `python -m pytest -q`, `alembic current` y `alembic heads`.
- [x] Si cambia el esquema, aplicar y verificar Alembic sobre una base de prueba vacía y otra con datos existentes; no usar create_all como migración.
- [x] Ejecutar desde frontend: `npm run test`, `npm run build` y `npm run lint`.
- [x] Verificar los flujos modificados en navegador y los permisos por API; registrar resultados reales y errores pendientes.
- [x] Ejecutar `git diff --check` y comprobar que no se versionan secretos, .env, padrones reales ni fixtures con datos personales del manual.

==================================================
## 8. PRUEBA MANUAL ESPERADA
==================================================

- [x] ADMIN importa una muestra sintética del formato oficial, consulta varios filtros y revisa indicadores.
- [x] Intentar importar un archivo inválido y comprobar que los candidatos siguen consultando el lote válido anterior.

==================================================
## 9. DOCUMENTACIÓN E INFORME FINAL
==================================================

- [x] Actualizar documentación de setup, contratos, reglas y flujos realmente modificados.
- [x] Entregar archivos creados/modificados, endpoints/contratos, estrategia de permisos, modelos/migraciones y decisión sobre reutilización.
- [x] Informar resultados de pytest, migraciones, tests frontend, build, lint y navegador; distinguir tests con mocks de integración real.
- [x] Informar pendientes reales, decisiones y dependencias externas; no marcar completada una mini task que solo tiene un placeholder.
- [x] Actualizar este checklist, `status.md` y `report.md`; enlazar evidencia y actualizar el índice `docs/task/README.md`.
- [x] Incluir `git status --short` y `git diff --stat` en el informe. No hacer commit ni push.

## Dependencias y decisiones abiertas

D06 y D11; muestra oficial autorizada necesaria para cerrar ambigüedades de tipos/estados. Probar con datos sintéticos, sin versionar padrón real.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
