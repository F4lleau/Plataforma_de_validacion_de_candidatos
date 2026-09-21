# TASK 04 — Election Configuration, Catalogs and Validation Rules
> Estado al 20/09/2026: **Completada con configuración y plantillas de prueba**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 03.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2, 7–8 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-02, CAP-03, CAP-04; ver [matriz](../CAPACIDADES.md).
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

Completar elecciones, cargos y localidades con configuración real por elección, fechas de carga y reglas parametrizadas. Dejar una base estable para asignaciones, listas y validaciones, sin tratar parámetros de ejemplo como normativa legal.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `Election`, `Office`, `Municipality`, sus schemas/endpoints, `Configuracion.tsx`, `Localidades.tsx`, `ListRoleDefinition`, `ListValidationService`, Alembic y `AuditLog`. Los catálogos HTTP siguen siendo placeholders; los servicios de requisitos/RENAPER no están implementados.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. CONTRATO ELECTORAL Y DECISIONES
==================================================

- [x] Resolver o registrar D01–D05 y D09 de DECISIONES.md; distinguir la fecha electoral de apertura/cierre de carga.
- [x] Definir cardinalidad de elecciones activas, zona horaria y límites inclusivos de fechas; no asumir una sola elección ni ventanas retroactivas sin documentarlo.
- [x] Tomar como objetivo del manual: Diputados 25 años, 16 titulares + 8 suplentes, paridad 50/50 y sin alternancia obligatoria; Consejos 21 años, 22 cargos, paridad y alternancia obligatoria. Mantener D01/D02 antes de fijar plantillas definitivas.
- [x] Diferenciar reglas activas/requeridas de verificaciones efectivamente ejecutadas; un switch no debe convertir una validación pendiente en exitosa.

==================================================
## 3. MODELOS Y MIGRACIONES
==================================================

- [x] Reutilizar los modelos actuales; agregar por Alembic solo fechas, parámetros, relación elección/cargo o versión de reglas que realmente falten.
- [x] Mantener catálogos de cargos y localidades con claves estables, nombres y activación; no hardcodear IDs.
- [x] Preservar datos existentes y definir qué ocurre con listas que usan una versión anterior de reglas; no modificar su aprobación silenciosamente.
- [x] Agregar restricciones de coherencia de rangos/fechas/cantidades y migraciones reversibles cuando sea seguro.

==================================================
## 4. API Y AUDITORÍA BASE
==================================================

- [x] Reemplazar respuestas placeholder por services/repositories y schemas tipados para consulta y gestión ADMIN de elecciones, cargos y localidades.
- [x] Exponer a APODERADO solo catálogos/elecciones necesarios y permitidos para sus módulos; separar consultas de las mutaciones administrativas.
- [x] Validar permisos, referencias existentes, ventanas y errores de configuración en backend.
- [x] Reutilizar AuditLog con un servicio común mínimo para registrar cambios administrativos con actor, entidad y fecha; no incluir secretos. La consulta del historial se completa en Task 14.

==================================================
## 5. FRONTEND CONFIGURACIÓN
==================================================

- [x] Construir la pantalla ADMIN sobre el layout existente: proceso activo, nombre, apertura/cierre, cargos habilitados y reglas por cargo.
- [x] Mostrar parámetros y estados desde API, guardar cambios reales y explicar errores de validación.
- [x] Agregar navegación Configuración solo cuando funcione; estados de carga, vacío, error y operación exitosa.
- [x] Conservar tipografías, paleta y accesibilidad responsive; no reutilizar cifras ni fechas de las capturas como datos.

==================================================
## 6. TESTS
==================================================

- [x] ADMIN puede consultar/crear/editar configuración; anónimo 401 y APODERADO 403 en mutaciones.
- [x] Fechas inválidas y parámetros inconsistentes no se guardan; catálogos no exponen elecciones/módulos ajenos.
- [x] Migración sobre la DB existente conserva seed/usuarios; una modificación de reglas queda auditada.
- [x] Las reglas distinguen los dos cargos y no obligan alternancia en Diputados.

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

- [x] ADMIN configura una elección y ambos cargos; recarga y comprueba persistencia.
- [x] Cambia reglas/fechas y verifica feedback y auditoría; APODERADO no puede modificarlas.

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

D01, D02, D03, D04, D05 y D09: reglas ambiguas del manual deben quedar resueltas o aisladas como mini tasks pendientes; avanzar con catálogos independientes.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
