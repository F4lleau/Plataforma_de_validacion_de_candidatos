# TASK 08 — Candidate Drafts, Editing and Office Requirements
> Estado al 20/09/2026: **Completada en alcance de prueba**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 06, Task 07.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 5, 9–11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-12, CAP-13, CAP-14; ver [matriz](../CAPACIDADES.md).
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

Implementar selección de lista, carga y corrección de candidatos con Guardar borrador y Guardar y validar. Resolver requisitos reales de edad y conservar la advertencia no bloqueante de afiliación.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `Person`, `Candidate`, `ListCandidate`, `CandidateValidation`, CandidateService/repositories/schemas, OfficeValidationService, AffiliationValidationService, Candidatos.tsx y tests existentes.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. CONTRATO Y CONSISTENCIA DE DATOS
==================================================

- [x] Recibir lista y posición/cargo de plantilla, DNI, nombres, apellidos, fecha de nacimiento y género; derivar elección/cargo/municipio electoral desde la lista.
- [x] No aceptar created_by ni estado de validación/autoría enviados por el frontend.
- [x] Crear/editar persona, candidatura y vínculo con posición dentro de una transacción; resolver reuso de persona por DNI sin violar unicidad ni producir registros huérfanos.
- [x] Definir política de duplicados dentro de lista y entre listas/elecciones con D09; no imponer exclusiones electorales no definidas.
- [x] Corregir el dato de postulación/localidad usado en permisos actuales sin deducirlo del domicilio de Person.

==================================================
## 3. BORRADOR Y EDICIÓN
==================================================

- [x] Diferenciar Guardar borrador de Guardar y validar con contratos y estados explícitos.
- [x] Permitir corregir campos/posición de una candidatura accesible y editable, manteniendo autoría e historial.
- [x] Invalidar resultados previos que dependan de campos modificados; no conservar aprobaciones antiguas como si validaran datos nuevos.
- [x] Resolver borradores incompletos sin relajar silenciosamente campos no nulos; si requiere cambios estructurales, usar Alembic.
- [x] La ausencia en padrón nunca impide guardar ni continuar trabajando.

==================================================
## 4. VALIDACIÓN DE REQUISITOS Y AFILIACIÓN
==================================================

- [x] Implementar edad mínima parametrizada: 25 Diputados, 21 Consejos, usando la fecha de referencia acordada en D03.
- [x] Probar cumpleaños exacto y años bisiestos; no sustituir cálculo por diferencia de años.
- [x] Consultar padrón vigente y persistir verified/warning con requires_admin_review; conservar casos ausentes para revisión.
- [x] No implementar ciudadanía, antigüedad o residencia como si sus umbrales estuvieran definidos: D04 debe resolverse primero.
- [x] Preparar orquestación con Task 09 para RENAPER; mientras falte, responder pendiente/no disponible, nunca OK ficticio.

==================================================
## 5. FORMULARIO Y RESULTADO
==================================================

- [x] Reemplazar IDs manuales por selector de lista autorizada y posición/cargo disponible.
- [x] Implementar campos del manual, feedback por campo, estados de guardado y ambas acciones.
- [x] Mostrar resultado granular de afiliación y requisitos, advertencias no bloqueantes, pendientes de identidad y acciones de corrección.
- [x] Conservar datos del formulario frente a errores y evitar doble envío; reflejar actualización en lista y cantidad cargada.

==================================================
## 6. TESTS
==================================================

- [x] Guardar borrador y guardar-validar persisten lo acordado; fallo intermedio revierte persona/candidato/vínculo.
- [x] Afiliado y no afiliado se guardan; el segundo queda con warning y revisión, sin rechazo de carga.
- [x] Edad mínima justo antes/en/después del cumpleaños y año bisiesto para ambos cargos.
- [x] DNI/posición duplicados, cambio de datos, lista ajena/cerrada y autoría manipulada no generan inconsistencias.
- [x] Editar invalida validaciones anteriores pertinentes; proveedor ausente no produce aprobación automática.

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

- [x] Seleccionar una lista y crear un borrador; retomarlo y guardar/validar un candidato afiliado.
- [x] Cargar uno ausente del padrón, comprobar advertencia y continuar con otro candidato.
- [x] Corregir fecha/posición, comprobar revalidación y actualizaciones del detalle.

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

D03/D04 y política de borrador/edición/duplicados de D08/D09. RENAPER real se incorpora en Task 09; su ausencia debe quedar visible.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
