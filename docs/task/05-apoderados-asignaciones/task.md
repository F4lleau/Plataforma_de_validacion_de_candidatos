# TASK 05 — Apoderado Management, Assignments and Account Access

> Actualización 22/09/2026: RENAPER fue retirado por el usuario. Las consignas de identidad externa y dependencias de Task 09 que aparecen abajo son antecedentes, no trabajo pendiente. Se conservan los controles locales y el feedback granular. Ver [alcance vigente](../RETIRO_RENAPER.md).

> Estado al 20/09/2026: **Completada**. El usuario indicó «no tengo la plantilla oficial, vamos con datos de prueba» y «renaper aún no, solo prepara el proyecto». Ver [informe](report.md) y [decisiones](../DECISIONES.md).
> Las casillas de muestras/contratos institucionales pendientes no impiden el cierre del alcance de prueba autorizado; no significan capacidad productiva verificada.

Trabajar sobre `develop`, reutilizando el checkpoint y la implementación existente.
**NO hacer commit ni push al finalizar.** Esta consigna describe trabajo pendiente, no una implementación ya realizada.

**Dependencias:** Task 03, Task 04.
**Fuente:** Manual_Plataforma_PJ_Chaco Presentación.pdf, páginas 2–3, 5–6, 8–9 y 11; ver [fuente](../FUENTE_MANUAL.md).
**Cobertura:** CAP-01, CAP-05, CAP-06, CAP-25; ver [matriz](../CAPACIDADES.md).
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

Permitir al ADMIN crear, editar, activar/desactivar apoderados y asignar módulos/cargos/localidades. Completar acceso y recuperación asistida sin duplicar la autenticación de Task 03.

==================================================
## 1. AUDITORÍA PREVIA
==================================================

- [x] Revisar rama y `git status --short`; conservar cambios locales y datos ajenos a esta task.
- [x] Revisar: `User`, `UserModule`, `UserRepository`, `UserService`, auth/security, `AccessService`, `UserModuleRepository`, bootstrap, `Usuarios.tsx`, login y los contratos de catálogo de Task 04.
- [x] Verificar dependencias y registrar qué se reutiliza, qué falta y qué mini tasks tienen impedimentos concretos en `status.md`.
- [x] Resolver o aislar las decisiones pendientes antes de implementar comportamiento dependiente; continuar el trabajo independiente.

==================================================
## 2. CONTRATOS Y CONSISTENCIA
==================================================

- [x] Definir schemas de alta/edición sin aceptar escalamiento de rol desde APODERADO; el rol de alta en este flujo es APODERADO.
- [x] Normalizar email/usuario y rechazar duplicados con mensajes claros.
- [x] Permitir uno o ambos módulos habilitados; asociarlos a elección y cargo reales; requerir localidad para Consejos y evitar localidad ficticia para Diputados.
- [x] Definir y documentar revocación/reasignación conservando listas y autoría histórica; coordinar granularidad por lista con Task 07 (D09).

==================================================
## 3. ADMINISTRACIÓN BACKEND
==================================================

- [x] Completar endpoints de listado/detalle/alta/edición/estado usando servicios y repositorios existentes.
- [x] Guardar contraseña inicial exclusivamente como hash; no devolver hashes ni guardar/loguear contraseña en auditoría.
- [x] Persistir usuario y asignaciones de forma transaccional y evitar módulos duplicados o con cargo incompatible.
- [x] Aplicar efecto inmediato a desactivación y retiro de módulos en requests con JWT ya emitido; auditar antes/después no sensible.

==================================================
## 4. GESTIÓN FRONTEND
==================================================

- [x] Implementar Gestión de Apoderados con nombre, email, módulos, municipio, estado y acción Editar.
- [x] Crear formulario/modal con nombre completo, email/usuario, contraseña inicial, selección de módulos y municipio cuando aplica.
- [x] Agregar alta, edición, activar/desactivar, validación de campos, confirmación apropiada de desactivación y feedback persistido.
- [x] Mostrar datos de API; no cargar usuarios ni claves de las capturas del manual.

==================================================
## 5. ACCESO, CONTRASEÑA Y SOPORTE
==================================================

- [x] Conservar login JWT y restauración de Task 03; agregar mostrar/ocultar contraseña con etiqueta accesible si falta (captura p. 3).
- [x] Resolver D10: el enlace Olvidó su contraseña debe tener un flujo real de ayuda/recuperación, no una acción ficticia.
- [x] Implementar como mínimo recuperación asistida por ADMIN o el canal definido por la Junta; sin proveedor de correo confirmado, no inventar envío automático.
- [x] Si se define restablecimiento, usar un mecanismo seguro y probar que una clave nueva invalida la anterior; no revelar existencia de cuentas ni publicar credenciales de prueba.
- [x] Documentar entrega inicial de credenciales y canal configurable de soporte; las solicitudes no envían mensajes externos sin autorización.

==================================================
## 6. TESTS
==================================================

- [x] Matriz ADMIN/APODERADO/anónimo en todas las operaciones; no se puede cambiar el propio rol desde el cliente.
- [x] Alta duplicada/inválida revierte también asignaciones; contraseña persistida hasheada y ausente de respuestas/logs.
- [x] Usuario desactivado y asignaciones revocadas pierden acceso aun con token previo; reactivación preserva datos.
- [x] Apoderados de distinto municipio/elección no consultan ni modifican recursos ajenos; recuperación acordada funciona sin endpoint engañoso.

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

- [x] ADMIN crea un apoderado de Consejos, otro de Diputados y uno con ambos módulos.
- [x] Ingresar con cada usuario y comprobar alcance; desactivar/reasignar y verificar el cambio inmediato.
- [x] Probar mostrar contraseña y la vía real de recuperación/ayuda.

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

D09 (granularidad y reasignación) y D10 (contacto y mecanismo de recuperación); gestionar cuentas no depende de disponer de correo automático.

## Definición de done

- [x] Todos los criterios aplicables implementados y verificados; cualquier no aplicable tiene justificación explícita.
- [x] Regla crítica conservada: candidato ausente del padrón se guarda con advertencia y revisión, permitiendo continuar.
- [x] Documentación consistente con código real; sin secretos, datos electorales reales ni credenciales del manual en Git.
- [x] Sin commits ni push; informe revisable y estado actualizado.
