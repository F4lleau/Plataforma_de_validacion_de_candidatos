# TASK 07 — Electoral Lists, Templates and Assigned Ownership
> Estado al 20/09/2026: **Completada con plantillas de prueba**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 04, Task 05.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2, 4, 8–11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-10, CAP-11; ver [matriz](../CAPACIDADES.md).
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

Completar Crear lista, Mis listas, detalle y Continuar carga con plantillas por cargo y acceso efectivo a cada lista. Reutilizar la consulta real de Task 03 y eliminar la dependencia del domicilio del candidato para decidir permisos.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `ElectoralList`, `ListCandidate`, `ListRoleDefinition`, `UserModule`, `ListService`, `ListRepository`, `ListTemplateService`, `AccessService`, schemas y `Listas.tsx`.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. MODELO Y ASIGNACIÓN POR LISTA
==================================================

- [x] Resolver D09: si una lista pertenece a un apoderado o admite varios, y cómo se asigna/transfiere.
- [x] Persistir asignación/propiedad explícita cuando haga falta; no inferirla solo de created_by ni conceder todas las listas del municipio por compartir módulo.
- [x] Guardar elección, cargo, municipio electoral de la lista, nombre, número identificador y fecha de creación; definir unicidad del número (D09).
- [x] Actualizar autorización de consulta/edición/carga/validación a módulo habilitado más lista asignada; separar municipio electoral de domicilio personal.
- [x] Migrar listas/candidatos existentes con una política explícita de vinculación y sin pérdida de autoría ni datos.

==================================================
## 3. PLANTILLAS POR CARGO
==================================================

- [x] Reutilizar roles/posiciones con carga idempotente y reglas de Task 04.
- [x] Diputados: preparar distribución 16 titulares + 8 suplentes conforme decisión D01; no tomar 16 como total sin resolver contradicción.
- [ ] Consejos: total exacto 22; obtener nombres/orden/grupos oficiales antes de presentar cargos inventados como definitivos (D02). **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [x] Preservar código estable, orden y tipo titular/suplente; prevenir plantillas que contradigan la configuración activa.

==================================================
## 4. API DE LISTAS
==================================================

- [x] Implementar alta, consulta paginada, detalle y edición de borrador con schemas y servicios; conservar GET existente.
- [x] Permitir crear solo sobre elecciones/cargos/municipios habilitados, en ventana de carga; fijar actor y estado inicial Borrador en backend.
- [x] Agregar nombre/número, búsqueda por nombre y filtro por estado; detalle con plantilla, posiciones y cantidad cargada.
- [x] No aceptar un estado Aprobada/Enviada controlado por payload; transiciones de envío/aprobación se implementan en Task 10.
- [x] Auditar creación/edición/asignación y aplicar política definida para listas no editables.

==================================================
## 5. FRONTEND MIS LISTAS
==================================================

- [x] Crear modal/pantalla Crear lista con nombre, número y selector de cargo/módulo; mostrar solo opciones autorizadas.
- [x] Mostrar número, lista, cargo, municipio, candidatos, estado y acciones Ver/Continuar carga.
- [x] Conectar selección de lista con carga de candidatos de Task 08; navegar con identificador real sin pedir IDs técnicos al usuario.
- [x] Mantener vista ADMIN global y APODERADO asignada, estados de carga/vacío/error y diseño responsive.

==================================================
## 6. TESTS
==================================================

- [x] Alta restringida a módulo, elección, municipio y ventana válidos; payload no suplanta creador/estado.
- [x] Dos apoderados del mismo municipio no acceden a listas ajenas salvo asignación explícita.
- [x] Número duplicado se controla dentro del alcance acordado; filtros/paginación/cantidad son correctos.
- [x] Plantillas tienen posiciones únicas, cantidades y grupos aprobados; migración conserva listas existentes.

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

- [x] APODERADO crea una lista permitida y la retoma desde Mis listas; intenta abrir otra ajena por URL/API.
- [x] ADMIN inspecciona ambas listas y comprueba plantilla, número, municipio y estado.

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

D01/D02 para plantillas oficiales y D09 para propiedad, número y transición desde el alcance por módulos actual.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
