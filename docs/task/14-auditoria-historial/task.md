# TASK 14 — Audit Trail and Electoral Action History

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 04, Task 05, Task 06, Task 07, Task 08, Task 10, Task 11, Task 13.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-24; ver [matriz](../CAPACIDADES.md).
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

Completar la consulta ADMIN de auditoría y el historial por recurso usando eventos capturados desde las tasks previas; permitir reconstruir quién hizo qué y cuándo.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `AuditLog`, el servicio común de Task 04, eventos de usuarios/asignaciones/padrón/listas/candidatos/validaciones/envíos/exportaciones. El modelo existe, pero no hay bandeja completa de auditoría.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. COBERTURA DE EVENTOS
==================================================

- [x] Inventariar y completar eventos de alta/edición/desactivación de usuario, asignaciones, configuración, importación de padrón, creación/corrección de lista/candidato, validación, envío, aprobación y exportación.
- [x] Registrar actor autenticado o acción de sistema, fecha, recurso, tipo de operación y cambio relevante; no aceptar actor del payload.
- [x] Vincular eventos automáticos con la operación que los originó y versión de reglas/datos cuando aplique.
- [x] Resolver huecos de captura en el servicio productor correspondiente; no fabricar eventos históricos para aparentar cobertura.

==================================================
## 3. INTEGRIDAD Y DATOS
==================================================

- [x] Hacer consistentes mutación y evento en la transacción pertinente; registrar fallos externos con semántica distinta de éxito.
- [x] No guardar passwords, JWT, URLs con credenciales, padrón completo ni payload íntegro de identidad en details_json.
- [x] Definir presentación de antes/después con campos mínimos útiles; mantener atribución tras desactivar usuarios.
- [x] No ofrecer edición/borrado arbitrario de auditoría; una política de retención futura requiere definición explícita.

==================================================
## 4. CONSULTA ADMIN
==================================================

- [x] Implementar consulta paginada con filtros por fecha, actor, acción y entidad, y detalle de evento.
- [x] Agregar historial contextual accesible desde lista/candidato y enlace a recurso cuando exista.
- [x] Usar schemas de respuesta seguros e índices Alembic solo si el patrón de consulta lo necesita.
- [x] Proteger todas las rutas por ADMIN; el manual no concede una bandeja global de auditoría al apoderado.

==================================================
## 5. FRONTEND E HISTORIAL
==================================================

- [x] Integrar historial contextual y una entrada ADMIN de auditoría si se adopta esa organización; la navegación exacta es una propuesta técnica, no una pantalla detallada en el PDF.
- [x] Mostrar actor, fecha con zona, acción, entidad y motivo/cambio legible.
- [x] Resolver filtros, paginación, vacío/error y enlaces sin duplicar información sensible.
- [x] Documentar diferencias entre validaciones vigentes e historial de acciones.

==================================================
## 6. TESTS
==================================================

- [x] Operaciones exitosas generan eventos con actor real; fallos/rollback no dejan eventos engañosos de éxito.
- [x] Evento de sistema y evento de usuario se distinguen; captura no expone secretos.
- [x] Filtros/orden/paginación e historial por lista/candidato coinciden con acciones realizadas.
- [x] Anónimo/APODERADO no consulta auditoría global ni detalle por ID directo.

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

- [x] ADMIN sigue la secuencia crear lista → cargar candidato → validar → enviar → aprobar/observar y consulta el historial.
- [x] Filtra por usuario/fecha/entidad y verifica registro de cambios de configuración y exportación.

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
