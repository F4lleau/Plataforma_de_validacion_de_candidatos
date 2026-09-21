# TASK 09 — RENAPER Integration and Candidate Validation Results
> Estado al 20/09/2026: **Preparación completada; conexión real diferida por el usuario**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 08.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2, 5, 10–11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-15, CAP-16; ver [matriz](../CAPACIDADES.md).
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

Reemplazar respuestas OK ficticias por resultados reales o pendientes de identidad, integrar RENAPER cuando exista contrato/acceso y mostrar validación granular inmediata sin bloquear el guardado por fallos externos.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `RenaperClient`, `RenaperValidationService`, `OfficeValidationService`, `CandidateValidation`, CandidateService y configuración. Hoy RENAPER no está implementado y algunos stubs devuelven status=ok.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. CONTRATO Y DISPONIBILIDAD
==================================================

- [ ] Resolver D07: proveedor autorizado, endpoint/documentación, credenciales, ambiente de pruebas, campos, límites y semántica de coincidencia. **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [x] Continuar las partes independientes sin inventar una API ni credenciales; registrar explícitamente la mini task de conexión real como bloqueada si falta acceso.
- [x] Distinguir proveedor real, mock de pruebas y no configurado; un mock no habilita aprobación productiva.
- [x] Definir condiciones de identidad coincidente/no coincidente/pendiente/error y qué datos mínimos se conservan.

==================================================
## 3. CLIENTE Y SERVICIO
==================================================

- [ ] Implementar cliente encapsulado con timeout y errores controlados; configuración/secretos por entorno. **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [ ] Validar respuesta y coincidencia según contrato; no hacer comparación improvisada de nombres o sexo. **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [x] Evitar exponer payload sensible completo; almacenar evidencia mínima y referencia técnica necesaria.
- [ ] Permitir reintentar fallos transitorios bajo límites; no mantener transacciones DB abiertas mientras se espera a la red. **Diferido: fuera del alcance de prueba confirmado por el usuario.**

==================================================
## 4. ORQUESTACIÓN Y PERSISTENCIA
==================================================

- [x] Persistir resultados separados de afiliación, requisitos e identidad con fecha, datos/versiones evaluadas y origen.
- [x] Devolver estado pendiente/error de integración ante timeout, indisponibilidad o falta de configuración; no marcar identidad rechazada por fallo técnico.
- [x] No perder al candidato guardado; prevenir doble ejecución/resultado duplicado ante reintentos.
- [x] Dejar verificaciones obligatorias pendientes como impedimento de aprobación automática, sin confundirlo con impedir la carga.
- [x] No usar resultados obsoletos luego de una corrección o cambio de reglas/padrón.

==================================================
## 5. RESULTADOS FRONTEND
==================================================

- [x] Mostrar afiliación, edad/requisitos y RENAPER por separado con estado, mensaje claro y próxima acción.
- [x] Distinguir validando, verificado, observación, pendiente, error y no disponible; no limitarse al toast de simulación de la captura.
- [x] Actualizar resultado tras guardar y validar; si el proceso es asíncrono, dar estado consultable sin spinner indefinido.
- [x] Permitir corregir/reintentar únicamente cuando rol y estado de lista lo habiliten; auditar la acción.

==================================================
## 6. TESTS
==================================================

- [ ] Contrato del proveedor: coincide, no coincide, no encontrado, datos incompletos, timeout, 429 y respuesta inesperada. **Diferido: fuera del alcance de prueba confirmado por el usuario.**
- [x] Proveedor no configurado/mock/error nunca produce un OK apto para aprobación real.
- [x] Resultados quedan persistidos y asociados al dato vigente; reintento no duplica candidato ni validación vigente.
- [x] Usuario ajeno no consulta ni relanza validación; errores externos conservan candidato y UI operable.

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

- [x] Guardar y validar muestra tres resultados claros; provocar fallo controlado del proveedor y comprobar candidato conservado.
- [ ] Con credenciales de pruebas autorizadas, verificar un caso real del proveedor y registrar evidencia sin secretos. **Diferido: fuera del alcance de prueba confirmado por el usuario.**

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

D07 es dependencia externa para integración real. La task no se marca completada con mocks; se puede cerrar por separado el manejo honesto de estados pendientes.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
