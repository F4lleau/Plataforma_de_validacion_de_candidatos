# TASK 11 — Administrative List Inbox and Granular Validation Review

> Actualización 22/09/2026: RENAPER fue retirado por el usuario. Las consignas de identidad externa y dependencias de Task 09 que aparecen abajo son antecedentes, no trabajo pendiente. Se conservan los controles locales y el feedback granular. Ver [alcance vigente](../RETIRO_RENAPER.md).


Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 07, Task 08, Task 10.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2, 4–5 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-19, CAP-20; ver [matriz](../CAPACIDADES.md).
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

Construir la bandeja ADMIN y la pantalla Validaciones con detalle real por lista y candidato, filtros, búsqueda y estados. Preservar la revisión de afiliación existente.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: Listas.tsx, CandidatosRevision.tsx, Validaciones.tsx, list/candidate/validation repositories y contratos de Tasks 07–10. Revisar qué páginas siguen vacías y evitar reemplazar servicios ya implementados.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. BANDEJA ADMINISTRATIVA
==================================================

- [x] Listar todas las listas autorizadas para ADMIN con número, nombre, cargo, municipio, cantidad de candidatos, estado y acción Ver.
- [x] Agregar búsqueda por nombre/número y filtro por estado con paginación/orden estables.
- [x] Ofrecer detalle de lista, apoderado asignado, composición y fechas; no exponer respuestas placeholder como información válida.
- [x] Preparar exportación Excel/CSV compartiendo filtros con Task 13; no añadir un botón que no opere.

==================================================
## 3. VALIDACIONES GRANULARES
==================================================

- [x] Exponer detalle agregado y por candidato: posición, nombre, DNI, género, afiliación, requisitos/edad, RENAPER y estado.
- [x] Mostrar cantidades cargadas/requeridas, balance F/M y alternancia según corresponda al cargo; indicar no aplica cuando esté deshabilitada.
- [x] Distinguir resultado vigente, histórico, pendiente, error técnico y observación, con motivos verificables.
- [x] Permitir navegar desde una lista al candidato observado y desde candidatos en revisión a su lista.

==================================================
## 4. REVISIÓN Y PERMISOS
==================================================

- [x] Conservar /candidates/review como ADMIN only y enriquecer contrato/UI con nombres y contexto real en lugar de solo IDs.
- [x] No crear facultades de aprobar/rechazar manualmente o dispensar requisitos sin resolver D08; el manual describe supervisión y auditoría.
- [x] No aplicable: no se acordaron decisiones administrativas manuales. Se conserva evidencia automática sin agregar facultades nuevas.
- [x] APODERADO consulta únicamente resultados de sus listas mediante endpoints adecuados; no accede a la bandeja global.

==================================================
## 5. FRONTEND Y CONSULTAS
==================================================

- [x] Agregar navegación ADMIN Listas Cargadas y Validaciones cuando funcionen; conservar rutas o definir redirecciones compatibles.
- [x] Implementar búsqueda/filtros, detalle, badges y tabla responsive con nombres legibles y carga/error/vacío.
- [x] Reutilizar consultas/servicios evitando N+1 y descargas completas por cada filtro.
- [x] Mantener estados y recuentos consistentes con dashboard/reportes posteriores.

==================================================
## 6. TESTS
==================================================

- [x] Filtros y paginación devuelven listas correctas; el detalle coincide con DB y validaciones actuales.
- [x] Anónimo 401/APODERADO 403 en bandeja; ID de lista ajena no filtra nombres ni validaciones por otra ruta.
- [x] Advertencias, pendientes, error proveedor y aprobados se distinguen sin convertir fallo técnico en rechazo.
- [x] La revisión de afiliación de Task 02B sigue mostrando casos sin impedir carga.

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

- [x] ADMIN busca una lista enviada, entra a Ver y analiza los controles por candidato.
- [x] Abre un candidato con warning y verifica contexto, motivo e historial disponible.
- [x] APODERADO intenta URL/API global y confirma bloqueo.

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

D08 solo para acciones administrativas resolutivas; las consultas y visualización pueden completarse sin inventar esas facultades.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
