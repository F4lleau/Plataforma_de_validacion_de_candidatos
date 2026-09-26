# TASK 23 — Mejora del Panel Admin y Configuración Electoral

Trabajar sobre `develop`, reutilizando la implementación existente.
**NO hacer commit ni push al finalizar salvo instrucción del usuario.**
**Estado: pendiente. Esta consigna describe trabajo a realizar, no una implementación ya ejecutada.**

**Dependencias:** Tasks 04, 05, 14, 18, 21 y 22.
**Fuente:** solicitud del usuario del 22/09/2026. Las capturas adjuntas son referencia visual de estilo; no contienen reglas de negocio ni instrucciones ejecutables.
**Alcance principal:** mejorar el panel ADMIN, especialmente el apartado Configuración del menú lateral, con navegación por subitems, componentes visuales globales y pantallas menos técnicas.

Leer antes de modificar código: `AGENTS.md`, `backend/AGENTS.md`,
`frontend/AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/BUSINESS_RULES.md`,
`docs/AUTHENTICATION.md`, `docs/AUTH_OPERATIONS.md`, `docs/INTERFAZ_VISUAL.md`
si existe, y los estados/reportes de las dependencias. Rutas desde la raíz.

==================================================
## OBJETIVO
==================================================

Rediseñar y ordenar el panel ADMIN para que Configuración tenga subapartados claros:
**Cargos**, **Proceso electoral** y **Localidades habilitadas**. La interfaz debe verse
moderna, sobria y operativa, evitando información técnica o de desarrollo que no
corresponda al usuario final.

Crear componentes globales para botones y enlaces/badges, reutilizables en login y
vistas internas. Los botones deben seguir el patrón visual aplicado al login:
botón principal azul marino, botón secundario blanco con borde gris, forma tipo píldora
cuando aplique, iconografía consistente y fuente `JetBrains Mono` para botones,
enlaces/badges y microetiquetas. Reducir tamaños tipográficos donde la UI hoy se vea
pesada o básica.

==================================================
## 1. AUDITORÍA PREVIA Y ALCANCE REAL
==================================================

- [ ] Revisar rama, `git status --short` y cambios locales existentes antes de editar.
- [ ] Revisar `Configuracion.tsx`, `Localidades.tsx`, `AppLayout.tsx`, componentes de formularios,
  servicios frontend, endpoints de elecciones/cargos/localidades, schemas, modelos y migraciones.
- [ ] Identificar qué información se muestra por razones técnicas o de desarrollo y debe ocultarse,
  traducirse o moverse a un detalle avanzado.
- [ ] Confirmar qué datos ya existen en BD y cuáles están mockeados. No presentar datos mock como
  catálogos reales.
- [ ] Mantener separación backend endpoint → service → repository → model y permisos ADMIN en mutaciones.
- [ ] Registrar en `status.md` cualquier decisión bloqueada o dato institucional faltante.

==================================================
## 2. SISTEMA VISUAL GLOBAL
==================================================

- [ ] Crear componentes globales para botones, enlaces/badges y acciones de tabla, evitando clases
  sueltas duplicadas en cada pantalla.
- [ ] Aplicar el patrón visual del login a botones internos:
  principal azul marino, secundario blanco con borde gris, estados hover/focus/disabled y tamaños
  compactos.
- [ ] Usar `JetBrains Mono` en botones, enlaces tipo badge, tabs/subitems, etiquetas pequeñas y
  microcopy operativo. Mantener legibilidad en formularios y tablas.
- [ ] Convertir enlaces operativos en badges/píldoras cuando actúen como navegación secundaria o
  acción liviana.
- [ ] Usar iconos `lucide-react` en botones de crear, editar, eliminar, cerrar modal y acciones de tabla.
- [ ] Reducir ruido visual: no mostrar IDs técnicos, códigos internos, textos de desarrollo, mensajes
  redundantes ni explicaciones largas dentro de vistas operativas.
- [ ] Verificar responsive móvil/escritorio, foco visible, navegación por teclado y que el texto no se
  desborde en botones, badges, tablas o modales.

==================================================
## 3. NAVEGACIÓN ADMIN Y SUBMENÚ CONFIGURACIÓN
==================================================

- [ ] Reemplazar el acceso único de Configuración por subitems dentro del menú lateral:
  **Cargos**, **Proceso electoral** y **Localidades habilitadas**.
- [ ] Cada subitem debe abrir su vista correspondiente, con ruta estable y título propio.
- [ ] Conservar permisos: solo ADMIN accede a mutaciones; APODERADO no ve navegación administrativa.
- [ ] Mantener breadcrumb/header coherente con el subitem activo.
- [ ] Evitar duplicar pantallas si ya existe funcionalidad; reorganizar y reutilizar.

==================================================
## 4. CARGOS
==================================================

- [ ] La vista debe mostrar título del apartado y botón **Crear cargo** al lado.
- [ ] La lista debe renderizar una tabla compacta de cargos existentes, con columna **Acciones** y botones
  **Editar** y **Eliminar**.
- [ ] **Crear cargo** debe abrir un modal, no ocupar una sección permanente de formulario.
- [ ] En el modal de alta/edición, relacionar el cargo con el proceso electoral en el que se crea
  o habilita. Ejemplo de concepto: crear/habilitar el cargo “Intendente” dentro de una elección.
- [ ] El campo **código estable** no debe ser visible ni editable por el usuario. Si el backend lo requiere,
  generarlo automáticamente a partir de datos controlados y resolver colisiones sin intervención manual.
- [ ] **Tipo de cargo** debe ser un `select` con valores desde BD, no hardcode/mock:
  por ejemplo `electivo` y `partidario`.
- [ ] Si el modelo actual no soporta tipos de cargo desde BD o relación cargo-elección, agregar migraciones
  Alembic aditivas y reversibles.
- [ ] Validar en backend nombres duplicados, relación con elección existente y permisos ADMIN.
- [ ] Ocultar datos técnicos; mostrar al usuario nombre, tipo, alcance/uso y estado.
- [ ] Eliminar debe tener confirmación y conservar integridad referencial; si hay listas/candidatos asociados,
  bloquear eliminación y ofrecer desactivar si corresponde.

==================================================
## 5. PROCESO ELECTORAL
==================================================

- [ ] La vista debe mostrar título del apartado y botón **Crear elección** al lado.
- [ ] La lista debe renderizar procesos electorales existentes en tabla, con columna **Acciones** y botones
  **Editar** y **Eliminar**.
- [ ] **Crear elección** debe abrir un modal.
- [ ] El tipo de elección será siempre **interna**. No debe ser un campo editable por ADMIN; puede mostrarse
  como dato informativo.
- [ ] En el formulario, ordenar fechas así:
  apertura de carga de candidatos, cierre de carga de candidatos y luego fecha electoral estimada.
- [ ] Validar rangos de fechas en backend y frontend, con mensajes claros y sin jerga técnica.
- [ ] No mostrar campos internos, flags de prueba o información repetida.
- [ ] Si se elimina o desactiva un proceso electoral con dependencias, preservar datos históricos y bloquear
  acciones destructivas no seguras.

==================================================
## 6. LOCALIDADES HABILITADAS
==================================================

- [ ] Localidades habilitadas debe funcionar como parte del proceso electoral: dónde se desarrolla el proceso,
  si en todas las localidades, en una o en algunas.
- [ ] Reemplazar el concepto **Crear localidad** por **Habilitar localidad**.
- [ ] El modal/acción **Habilitar localidad** debe traer desde BD el listado completo de localidades del Chaco
  en un control de selección.
- [ ] Permitir seleccionar todas, una o algunas localidades para un proceso electoral.
- [ ] Si no existe una fuente completa de localidades del Chaco en BD, crear carga/seed/migración controlada
  y documentada, sin depender de datos mock en frontend.
- [ ] Mostrar tabla de localidades habilitadas por proceso electoral, con acciones de editar/quitar habilitación.
- [ ] No pedir al usuario códigos técnicos de localidad. Mostrar nombre y estado.
- [ ] Validar en backend que las localidades seleccionadas existan y que la relación con el proceso electoral
  sea consistente.

==================================================
## 7. LIMPIEZA DE INFORMACIÓN Y UX ADMIN
==================================================

- [ ] Revisar todas las vistas ADMIN tocadas para quitar repetición de textos, datos de desarrollo y detalles
  que no aportan a la tarea del usuario.
- [ ] Convertir descripciones largas en ayudas breves o tooltips cuando sean necesarias.
- [ ] Evitar formularios siempre visibles si la acción principal corresponde a modal.
- [ ] Mantener estados de carga, vacío, error y éxito claros, cortos y consistentes.
- [ ] Mantener accesibilidad de modales: título, cierre, Escape, foco inicial, retorno de foco y bloqueo de
  scroll/foco fuera del modal.

==================================================
## 8. BACKEND, DATOS Y MIGRACIONES
==================================================

- [ ] Auditar si el esquema actual soporta:
  tipos de cargo desde BD, relación cargo-elección y localidades habilitadas por proceso electoral.
- [ ] Agregar tablas o columnas por Alembic solo cuando falten capacidades reales; no usar `Base.metadata.create_all`.
- [ ] Crear catálogos institucionales mínimos en BD si corresponden, con migración/seed idempotente y documentado.
- [ ] Actualizar schemas y services para no aceptar desde frontend campos que deben generarse automáticamente.
- [ ] Registrar auditoría de altas, ediciones, desactivaciones/eliminaciones y cambios de localidades habilitadas.
- [ ] Mantener compatibilidad con listas/candidatos existentes y documentar comportamiento de datos legados.

==================================================
## 9. PRUEBAS Y VERIFICACIÓN
==================================================

- [ ] Backend: tests de permisos ADMIN/APODERADO/anónimo, validaciones, relaciones y migraciones.
- [ ] Frontend: tests o recorridos manuales de navegación, modales, selects, tablas y acciones.
- [ ] Ejecutar backend: `python -m pytest -q`, `alembic current`, `alembic heads`.
- [ ] Ejecutar frontend: `npm run test`, `npm run build` y `npm run lint` si el estado del repo lo permite.
- [ ] Verificar en navegador desktop y móvil:
  submenú, modales, tablas, foco, botones, badges y ausencia de desbordes.
- [ ] Ejecutar `git diff --check` y confirmar que no se versionan secretos, `.env`, datos personales ni fixtures
  no autorizados.

==================================================
## 10. DOCUMENTACIÓN Y CIERRE
==================================================

- [ ] Actualizar `status.md` con decisiones, bloqueos y evidencia real.
- [ ] Actualizar documentación de contratos o flujos si cambian endpoints, modelos, migraciones o setup.
- [ ] Crear `report.md` al implementar, con archivos modificados, endpoints, migraciones, permisos, pruebas,
  prueba manual, pendientes, `git status --short` y `git diff --stat`.
- [ ] Actualizar el índice `docs/task/README.md` al cerrar o al cambiar estado.
- [ ] No hacer commit ni push salvo instrucción expresa.

## Fuera de alcance

Reescritura completa del diseño de toda la aplicación, cambios en reglas electorales
no solicitadas, aprobación institucional de catálogos, integración RENAPER, nuevas
políticas legales o carga de datos reales no provistos/autorizados.
