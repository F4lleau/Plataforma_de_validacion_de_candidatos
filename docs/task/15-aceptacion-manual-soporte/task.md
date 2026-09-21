# TASK 15 — End-to-End Acceptance, Role Manuals and Support

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 03, Task 04, Task 05, Task 06, Task 07, Task 08, Task 09, Task 10, Task 11, Task 12, Task 13, Task 14.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 1–11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-01, CAP-25, CAP-26; ver [matriz](../CAPACIDADES.md).
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

Verificar todas las capacidades del manual como un sistema integrado, cerrar brechas de UX por rol y publicar documentación operativa y soporte que describan funciones reales.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: Matriz CAPACIDADES.md, DECISIONES.md, tasks anteriores, tests, rutas frontend/backend, manuales README y evidencia de integración externa. Un checklist marcado no reemplaza verificar la implementación.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. TRAZABILIDAD Y DECISIONES
==================================================

- [x] Revisar cada CAP-01 a CAP-26 contra API, UI, pruebas y estado de la task responsable.
- [ ] Cerrar decisiones aplicables con evidencia aprobada y actualizar manual/reglas; no declarar reglas legales verificadas solo por aparecer en el PDF.
- [x] Revisar diferencias entre prototipos y producto, incluyendo cantidades, cargos, ausencia en padrón y aprobación automática.
- [x] Distinguir aceptación local con fixtures de aceptación de la integración real RENAPER; no cerrar el sistema completo si un obligatorio sigue mockeado.

==================================================
## 3. RECORRIDOS ADMIN Y APODERADO
==================================================

- [x] ADMIN configura elección/reglas, da de alta apoderados, asigna módulos/listas e importa el padrón oficial de prueba.
- [x] APODERADO ve solo módulos/listas propias, crea lista, carga borradores, guarda/valida, corrige y envía.
- [x] Comprobar listas completas por ambos cargos, casos incompletos, paridad/alternancia/edad, warnings de afiliación y pendientes/errores de RENAPER.
- [x] ADMIN revisa bandeja/validaciones, compara dashboards, genera reportes/exportaciones y reconstruye auditoría.
- [x] Probar sesión expirada, logout/recarga, desactivación y revocación durante el flujo; verificar bloqueo por API además de botones.

==================================================
## 4. CALIDAD Y UX
==================================================

- [x] Revisar responsive en móvil/escritorio, teclado, labels, foco, errores legibles, estados de carga/vacío y ausencia de enlaces ficticios.
- [x] Preservar identidad visual PJ, Plus Jakarta Sans, Inter y paleta del proyecto usando assets autorizados; no copiar datos de personas del manual.
- [x] Probar doble click, fallos de red, refresh durante operación, concurrencia y tamaño representativo del padrón/exportaciones.
- [x] Ejecutar tests de regresión y migraciones desde DB vacía y existente; validar respaldo/recuperación del entorno de prueba sin borrar datos de trabajo.

==================================================
## 5. MANUALES Y SOPORTE
==================================================

- [x] Actualizar manual de ADMIN y APODERADO con pasos y capturas reales sin credenciales ni datos personales de terceros.
- [x] Documentar setup, migraciones, bootstrap, formato de padrón, flujos, reglas efectivas, estados y solución de errores habituales.
- [x] Agregar ayuda/contacto real configurable para consultas, reportes de errores y solicitud/recuperación de credenciales conforme D10.
- [x] Explicar límites pendientes y recuperación tras fallos; no publicar claves demo ni presentar stubs como integraciones productivas.
- [x] Guardar informe de aceptación con versiones probadas, resultados, evidencias y pendientes; no desplegar ni publicar automáticamente.

==================================================
## 6. TESTS
==================================================

- [x] Suite completa backend/frontend y E2E para ambos roles con datos sintéticos reproducibles.
- [x] Capacidades, métricas, exportaciones y auditoría coherentes para un mismo proceso de extremo a extremo.
- [x] Escenarios negativos de aislamiento entre apoderados del mismo/distinto municipio y elecciones.
- [ ] Integración externa validada con entorno autorizado; sin credenciales, informar el bloqueo concreto, no simular aceptación productiva.
- [x] Los manuales y soporte describen exactamente lo comprobado.

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

- [x] Ejecutar todos los recorridos documentados en un entorno local limpio de prueba y en la DB existente sin perder datos.
- [x] Registrar evidencia por capacidad y entregar informe final de aceptación con pendientes explícitos.

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

Las decisiones sin resolver y la conexión real RENAPER pueden impedir la aceptación integral. Mantener el avance verificable de las partes independientes.

## Definición de done

- [ ] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.

## Límites del cierre local

Las tres casillas institucionales siguen abiertas: no hay plantilla/reglas oficiales ni
proveedor RENAPER autorizado. El usuario pidió continuar con datos de prueba y preparar
la integración. Todos los recorridos locales y verificaciones listados sí se ejecutaron.
El contacto real se configura mediante SUPPORT_CONTACT; no se inventó un canal.
