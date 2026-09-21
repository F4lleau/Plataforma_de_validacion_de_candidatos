# TASK 12 — Role-Based Dashboards and Live Electoral Metrics

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 05, Task 07, Task 10, Task 11.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 3–4 y 8–9; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-21, CAP-22; ver [matriz](../CAPACIDADES.md).
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

Completar el panel principal de ADMIN con estadísticas reales y el de APODERADO con módulos, municipio y listas asignadas; conectar accesos a flujos funcionales.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: Dashboard.tsx, dashboard.py, AppLayout, estado auth y consultas de listas/usuarios. El endpoint summary actual devuelve ceros fijos y el frontend solo saluda.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. MÉTRICAS ADMIN
==================================================

- [x] Calcular total de listas, aprobadas, enviadas, rechazadas, incompletas y apoderados activos desde DB.
- [x] Definir denominadores y agrupación de estados coherentes con Task 10; no sumar una lista en categorías incompatibles.
- [x] Resolver el alcance por elección activa/seleccionada de D09; no mezclar elecciones sin mostrarlo.
- [x] Devolver últimas listas con número, nombre, cargo, municipio, candidatos y estado, ordenadas por la fecha acordada.

==================================================
## 3. PANEL APODERADO
==================================================

- [x] Devolver solo módulos habilitados y municipio(s) asignado(s), respetando revocaciones y propiedad de listas.
- [x] Mostrar sus listas con número/nombre, cargo, municipio, estado, candidatos cargados y fecha de creación.
- [x] Conectar Crear lista y Continuar carga con Tasks 07–08; no habilitar cargos ajenos.
- [x] Definir estado sin asignaciones/listas con instrucciones útiles, sin aparentar error técnico.

==================================================
## 4. CONTRATOS Y FRONTEND
==================================================

- [x] Crear/ajustar schemas y queries agregadas por rol con control backend; no descargar datos globales y filtrarlos en frontend.
- [x] Reutilizar layout y componentes de tarjetas/listas; mostrar datos reales y accesos que funcionen.
- [x] Actualizar panel después de crear/editar/enviar listas o al regresar a la pantalla con estrategia de refresco documentada.
- [x] Resolver loading/error/empty y responsive sin copiar números/nombres de las capturas.

==================================================
## 5. TESTS
==================================================

- [x] Métricas calculadas con varios estados y elecciones, base vacía, apoderados inactivos y filtros coherentes.
- [x] ADMIN ve resumen global autorizado; APODERADO solo módulos/listas asignadas y sin contadores globales filtrados en cliente.
- [x] Cambios de lista/asignación se reflejan en panel; última lista y recuentos coinciden con bandeja.
- [x] Rutas de las tarjetas/acciones son reales y siguen protegidas.

==================================================
## 6. VERIFICACIÓN
==================================================

- [x] Mantener separación endpoint → service → repository → model; roles/permisos se validan en backend.
- [x] Ejecutar desde backend, con entorno configurado: `python -m pytest -q`, `alembic current` y `alembic heads`.
- [x] Si cambia el esquema, aplicar y verificar Alembic sobre una base de prueba vacía y otra con datos existentes; no usar create_all como migración.
- [x] Ejecutar desde frontend: `npm run test`, `npm run build` y `npm run lint`.
- [x] Verificar los flujos modificados en navegador y los permisos por API; registrar resultados reales y errores pendientes.
- [x] Ejecutar `git diff --check` y comprobar que no se versionan secretos, .env, padrones reales ni fixtures con datos personales del manual.

==================================================
## 7. PRUEBA MANUAL ESPERADA
==================================================

- [x] ADMIN compara tarjetas y últimas listas contra la bandeja filtrada.
- [x] APODERADO con uno o ambos módulos ve sus cargos/localidades y retoma carga; sin asignaciones ve un estado claro.

==================================================
## 8. DOCUMENTACIÓN E INFORME FINAL
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
