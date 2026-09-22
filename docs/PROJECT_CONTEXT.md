# Proyecto: Junta Electoral / Plataforma de Validación de Candidatos

## 1. Problema de negocio

La plataforma busca apoyar a la Junta Electoral del Partido Justicialista, Distrito Chaco, en la administración de listas electorales y candidatos, con foco en la validación automática y asistida antes de la revisión administrativa.

La solución debe facilitar:

- la gestión del padrón de afiliados PJ;
- la carga de candidatos por parte de apoderados;
- la validación de afiliación y requisitos de lista;
- la identificación de observaciones;
- la revisión final por parte del administrador.

## 2. Actores

### ADMIN

- administra usuarios y apoderados;
- importan y actualizan el padrón;
- revisa candidatos, listas y observaciones;
- gestiona información electoral.

### APODERADO

- trabaja sobre los módulos/listas asignados;
- carga candidatos;
- completa listas;
- consulta validaciones;
- remite listas para revisión.

## 3. Flujo general

1. El administrador importa el padrón de afiliados desde Excel.
2. El apoderado trabaja sobre una lista asignada y carga candidatos.
3. El sistema valida la composición, requisitos y afiliación.
4. Se registran observaciones o alertas si algo no coincide con el padrón o con los requisitos del cargo.
5. La lista se envía para revisión administrativa.
6. El administrador confirma, corrige o rechaza la propuesta según la validación.

## 4. Estado actual del repositorio

Autenticación/RBAC, configuración electoral, reglas versionadas, administración de
apoderados/asignaciones, padrón XLSX de 18 campos, listas y carga/edición contextual
de candidatos tienen backend y frontend reales. PostgreSQL local usa Alembic.

Las rutas incluyen `/configuracion`, `/usuarios`, `/padron`, `/listas`, `/listas/:id`,
`/candidatos` y revisión administrativa. Las operaciones se autorizan en backend.

Las plantillas/datos locales son de prueba por pedido del usuario. RENAPER fue
retirado del alcance el 22/09/2026. Reglas institucionales ambiguas conservan su
estado pendiente; no hay aprobación productiva por simulación.

Envío/aprobación condicionada, bandeja administrativa, métricas, exportaciones e historial
visual están implementados en Tasks 10–14. La revisión consulta advertencias vigentes;
no se incorporaron facultades de resolución administrativa manual.

Ver [flujos y contratos actuales](ELECTORAL_WORKFLOWS.md),
[autenticación](AUTHENTICATION.md) y [seguimiento](task/README.md).

## 9. Consideraciones clave para agentes

- No documentar como implementado lo que está mockeado o incompleto.
- Mantener la regla crítica del padrón: ausencia en padrón = observación/alerta, no bloqueo automático.
- Respetar la separación de capas.
- Documentar cambios reales y no asumir que existen integraciones productivas no verificadas.

## 10. Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [frontend/AGENTS.md](../frontend/AGENTS.md)
- [backend/README.md](../backend/README.md)
- [frontend/README.md](../frontend/README.md)

## Actualización Tasks 10–15 (20/09/2026)

Envío transaccional, bandeja ADMIN, dashboards, reportes/exportaciones y auditoría
están implementados y verificados localmente. El contenido enviado queda en lectura.
Las reglas demo impiden afirmar aprobación institucional.
Ver `docs/SUBMISSION_REPORTING_AUDIT.md`, `docs/MANUAL_ADMIN.md`,
`docs/MANUAL_APODERADO.md` y `docs/task/INFORME_10_15.md` desde la raíz.
