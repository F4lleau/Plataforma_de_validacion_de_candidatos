# TASK 13 — Reports, Statistics and Excel CSV PDF Exports

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 06, Task 11, Task 12.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 4–5 y 7; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-09, CAP-23; ver [matriz](../CAPACIDADES.md).
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

Implementar reportes ADMIN filtrables y exportaciones reales: listas Excel/CSV, reportes Excel/PDF y padrón según formato acordado. Compartir filtros y recuentos con las vistas.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: Reportes.tsx, Padron.tsx, bandeja ADMIN, librerías pandas/openpyxl ya instaladas, queries de dashboard y servicios API. No hay una implementación completa de reportes/exportación.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. CONTRATOS Y FILTROS
==================================================

- [x] Definir reporte por cargo, localidad, estado, apoderado y elección; validar combinaciones y alcance ADMIN.
- [x] Compartir filtros con bandeja y padrón para que exportar incluya el resultado filtrado completo, no solo la página visible.
- [x] Definir columnas, etiquetas, orden, fecha de generación y formatos; distinguir número de lista e ID interno.
- [x] Confirmar formato de exportación de padrón (botón visible p. 7; formato no especificado); propuesta XLSX/CSV documentada, no obligación textual inventada.

==================================================
## 3. ESTADÍSTICAS Y GRÁFICOS
==================================================

- [x] Calcular total listas, total candidatos, apoderados activos y tasa de aprobación con denominador explícito.
- [x] Agregar distribución por estado y comparación de listas/candidatos por cargo como en p. 5.
- [x] Reutilizar consultas agregadas con dashboard para evitar métricas contradictorias.
- [x] Ofrecer tabla/resumen accesible junto a gráficos y estados vacíos sin divisiones por cero.

==================================================
## 4. EXPORTACIÓN BACKEND
==================================================

- [x] Generar XLSX y CSV de listas, XLSX y PDF de reportes, y el formato acordado del padrón desde servicios dedicados.
- [x] Proteger cada descarga con ADMIN, validar filtros y auditar tipo/alcance/cantidad sin guardar el contenido sensible exportado en logs.
- [x] Preservar DNI/matrícula como texto, tildes y fechas; evitar ejecución de fórmulas provenientes de datos ingresados en CSV/XLSX.
- [x] Aplicar límites/memoria/tiempos según tamaño del padrón y evitar truncamientos silenciosos.
- [x] Diseñar PDF legible con encabezados, filtros, totales y paginación; no agregar un runtime innecesario sin evaluar dependencias.

==================================================
## 5. FRONTEND Y DESCARGAS
==================================================

- [x] Implementar Reportes con filtros, indicadores, gráficos y selector de formato.
- [x] Conectar Exportar de listas/padrón y reporte al archivo real, con nombres/MIME correctos y estado de descarga.
- [x] Extender el cliente compartido para respuestas blob/binarias conservando Bearer, 401 y errores JSON; no duplicar lógica de token.
- [x] Mostrar errores de exportación de manera útil y evitar que los archivos contengan páginas HTML de error.

==================================================
## 6. TESTS
==================================================

- [x] Filtros idénticos producen mismos registros/totales en pantalla, XLSX, CSV y PDF; incluir más de una página de datos.
- [x] DNI con ceros iniciales, tildes, comillas/saltos y valores que parecen fórmula se conservan de manera segura.
- [x] ADMIN descarga; APODERADO/anónimo no puede descargar mediante URL directa.
- [x] PDF multipágina revisado visualmente, XLSX/CSV abiertos y comprobados, reporte vacío y volumen representativo.
- [x] Cliente de descarga maneja 401 y errores del servidor sin guardar archivos corruptos.

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

- [x] Filtrar por cargo/localidad/estado/apoderado, exportar todos los formatos y comparar totales con la UI.
- [x] Exportar padrón filtrado como ADMIN y comprobar que solo incluye los datos acordados.

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

Ninguno externo identificado; revisar las decisiones aplicables antes de implementar.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
