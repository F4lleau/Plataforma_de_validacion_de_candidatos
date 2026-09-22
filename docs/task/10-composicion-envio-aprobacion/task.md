# TASK 10 — List Composition, Submission and Automatic Approval

> Actualización 22/09/2026: RENAPER fue retirado por el usuario. Las consignas de identidad externa y dependencias de Task 09 que aparecen abajo son antecedentes, no trabajo pendiente. Se conservan los controles locales y el feedback granular. Ver [alcance vigente](../RETIRO_RENAPER.md).


Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** El estado ejecutado y sus límites se registran en status.md y report.md.

**Dependencias:** Task 07, Task 08, Task 09.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 4–5 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-17, CAP-18; ver [matriz](../CAPACIDADES.md).
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

Completar validación de composición y el ciclo Borrador → envío administrativo → aprobación automática si todos los controles obligatorios están satisfechos, con transiciones consistentes y trazabilidad.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `ListValidationService`, `ListValidation`, `ListStatus`, `CandidateStatus`, `ListCandidate`, validaciones de candidatos y endpoints de validación. Hoy el validador exige alternancia para todos los cargos y controla mínimos, no necesariamente cantidades exactas.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. COMPOSICIÓN POR CARGO
==================================================

- [x] Aislar D01/D02/D05 con reglas de prueba autorizadas (confirmación institucional pendiente); cargar reglas/plantilla desde la elección/cargo, no confiar en un office_type arbitrario enviado por el cliente.
- [x] Exigir exactamente 16 titulares y 8 suplentes en Diputados y 22 posiciones en Consejos cuando esas plantillas estén confirmadas; detectar faltantes y excedentes.
- [x] Validar posiciones únicas, cargos requeridos, candidatos/DNI repetidos según alcance definido y correspondencia con elección/cargo/lista.
- [x] Aplicar paridad 50/50 al ámbito acordado en D05; alternancia obligatoria solo en Consejos, no en Diputados.
- [x] Devolver todos los incumplimientos útiles, con posición/grupo afectado; persistir evaluación y versión de reglas.

==================================================
## 3. ESTADOS Y TRANSICIONES
==================================================

- [x] Resolver D08 y mapear Borrador, Incompleta, En validación, Rechazada por composición, Enviada al Admin y Aprobada por Sistema al modelo existente.
- [x] Documentar transición permitida, actor, condición, posibilidad de corregir/reabrir y consecuencias sobre validaciones.
- [x] No permitir que el cliente escriba el estado final ni marcar aprobada una lista por comprobar solo paridad.
- [x] Definir si los errores de composición impiden envío o quedan observados; no inferirlo de listas de demostración con pocos candidatos.

==================================================
## 4. ENVÍO Y APROBACIÓN
==================================================

- [x] Implementar acción de envío por apoderado autorizado dentro de plazo, revalidando datos actuales y fijando submitted_at desde backend.
- [x] Persistir evento de envío antes del de aprobación aunque ambos ocurran en una misma operación.
- [x] Aprobar automáticamente solo si composición, afiliación, requisitos e identidad obligatorios están verificados y vigentes; warnings o pendientes conservan revisión/pendiente.
- [x] Preservar carga no bloqueante de ausentes del padrón; no convertir una advertencia en aprobación ni en rechazo de registro.
- [x] Controlar doble envío/concurrencia y edición simultánea; usar transacciones y una referencia coherente a las validaciones evaluadas.

==================================================
## 5. UI Y REGRESIONES
==================================================

- [x] Mostrar cantidad exacta, paridad, alternancia, validaciones individuales y mensajes por posición.
- [x] Agregar Enviar lista y feedback de estado real; explicar qué falta y permitir corregir cuando corresponde.
- [x] Distinguir Enviada al Admin de Aprobada por Sistema; no prometer aprobación por click.
- [x] Auditar transiciones y cambios; refrescar detalle/listado sin estados optimistas falsos.

==================================================
## 6. TESTS
==================================================

- [x] Diputados con 24 (16+8) y sin alternancia cumple si resto OK; con 23/25 o grupos erróneos no cumple.
- [x] Consejos con 22 cumple; 21/23, paridad incorrecta, alternancia rota y posiciones/DNI duplicados muestran errores.
- [x] Lista estructuralmente correcta con afiliación warning o RENAPER pendiente no se aprueba automáticamente.
- [x] Envío doble/concurrente no duplica eventos y los recursos ajenos/fuera de plazo quedan protegidos.
- [x] Aprobación usa datos vigentes; editar no conserva aprobación obsoleta.

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

- [x] Armar listas sintéticas completas de ambos cargos, validar y enviarlas.
- [x] Comparar el caso totalmente verificado con uno con afiliación observada y otro con RENAPER pendiente.
- [x] Provocar error de composición, corregir y comprobar transición e historial.

==================================================
## 9. DOCUMENTACIÓN E INFORME FINAL
==================================================

- [x] Actualizar documentación de setup, contratos, reglas y flujos realmente modificados.
- [x] Entregar archivos creados/modificados, endpoints/contratos, estrategia de permisos, modelos/migraciones y decisión sobre reutilización.
- [x] Informar resultados de pytest, migraciones, tests frontend, build, lint y navegador; distinguir tests con mocks de integración real.
- [x] Informar pendientes reales, decisiones y dependencias externas; no marcar completada una mini task que solo tiene un placeholder.
- [x] Actualizar este checklist, `status.md` y `report.md`; enlazar evidencia y actualizar el índice `docs/task/README.md`.
- [x] Incluir `git status --short` y `git diff --stat` en el informe. No hacer commit ni push.

## Alcance verificado

Los checks de composición y aprobación corresponden al entorno sintético autorizado.
Las plantillas institucionales y RENAPER real no están certificados. D08 fue confirmado
por el usuario. Ver [informe](report.md).

## Dependencias y decisiones abiertas

D01/D02/D05/D08. Puede implementarse contra el contrato de Task 09 con tests controlados, pero aprobar datos reales exige proveedor real y reglas resueltas.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
