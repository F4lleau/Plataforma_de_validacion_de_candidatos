# Reglas funcionales de negocio

## 1. Roles y permisos

### ADMIN

- administra usuarios y apoderados;
- importa el padrón de afiliados PJ;
- realiza revisión administrativa de candidatos y listas;
- revisa observaciones y validaciones;
- gestiona datos electorales.

### APODERADO

- trabaja solamente sobre las listas y módulos asignados;
- agrega y completa candidatos;
- consulta validaciones;
- envía listas para revisión.

## 2. Asignaciones

El apoderado requiere módulo habilitado y asignación explícita por lista. El distrito
proviene de la lista; no del domicilio de Person. La asignación puede ser compartida;
revocar módulo/asignación retira el acceso sin borrar autoría histórica.

Número único por elección/cargo/distrito. Las fechas de carga son inclusivas en hora
argentina. Las listas conservan una versión de reglas y solo se editan en borrador o
incompletas. Ver [decisiones técnicas y datos de prueba](ELECTORAL_WORKFLOWS.md).

## 3. Padrón de afiliados PJ

### Regla crítica

La afiliación partidaria se valida contra el padrón de afiliados PJ importado por el administrador.

No existe API externa del padrón. El padrón se importa mediante Excel y se persiste en base de datos.

### Comportamiento esperado

Si un candidato no aparece en el padrón:

1. debe guardarse;
2. debe registrarse la validación de afiliación;
3. debe mostrarse una advertencia al apoderado;
4. debe marcarse para revisión administrativa;
5. debe permitir continuar con el trabajo sobre la lista.

La ausencia en padrón es una observación/alerta y no un rechazo automático.

## 4. Afiliación

La validación de afiliación se realiza por DNI contra `PartyMember`/padrón importado. El flujo implementado deja claro que la ausencia no bloquea automáticamente la inscripción del candidato ni la carga de la lista.

## 5. Candidato

Los candidatos deben poder registrarse con distintas condiciones de validación y revisión. Cuando no estén en el padrón, deben quedar marcados con alerta y revisión por administración, no por rechazo automático.

## 6. Listas

Las listas requieren:

- completitud de cargos requeridos;
- control de posiciones duplicadas;
- control de candidatos repetidos;
- validación de paridad y alternancia cuando la lógica esté presente;
- revisión administrativa final.

La validación actual `ListValidationService` incluye controles sobre:

- lista incompleta;
- candidatos repetidos;
- posiciones duplicadas;
- cargos faltantes;
- paridad 50/50;
- alternancia de género.

## 7. Validaciones

Las validaciones del proyecto se modelan con tipos y resultados como:

- `AFILIACION`
- `RENAPER`
- `REQUISITOS_CARGO`
- `COMPOSICION_LISTA`

Resultados posibles:

- `ok`
- `error`
- `warning`
- `pendiente`

## 8. Alertas y observaciones

Cuando no se cumple una validación o un dato no coincide con el padrón, la plataforma debe dejar un registro claro de observación, además de permitir continuar con el flujo de trabajo.

Esto es especialmente relevante para la afiliación. La ausencia en padrón debe visualizarse como advertencia y no como rechazo automático.

## 9. Revisión administrativa

La revisión administrativa es la etapa final de control. El administrador debe poder resolver o confirmar casos con observaciones, especialmente los relacionados con:

- afiliación;
- requisitos de cargo;
- composición de listas;
- casos pendientes o no conformes.

## 10. Paridad, requisitos y pendientes

Paridad/alternancia se leen de la versión vinculada a cada lista. Las plantillas de
prueba usan 24 posiciones (16+8) para Diputados sin alternancia obligatoria y 22
posiciones genéricas para Consejos con alternancia. No son plantillas oficiales.
La política no definida para otros géneros queda pendiente, sin impedir carga.

Edad se calcula con referencia configurable; el entorno de prueba usa día electoral.
Otros requisitos no confirmados y RENAPER sin proveedor permanecen pendientes.
Ausencia/inactividad en padrón produce warning, nunca rechazo automático del registro.
Editar genera nueva revisión; los resultados históricos no validan los datos nuevos.

## 11. Pendientes institucionales

Confirmar plantilla de Consejos, reglas oficiales, fecha de cómputo, ciudadanía,
antigüedad y estados del padrón antes de operar con datos reales. El envío con
composición correcta y pendientes a revisión fue confirmado para pruebas; resolución
manual/reapertura requieren definición institucional. RENAPER real queda diferido por instrucción del usuario.

## 12. Principio general

No inventar requisitos electorales no presentes en el repositorio. Toda regla funcional debe reflejar el estado real del proyecto, y las partes incompletas deben dejarse explícitamente identificadas como pendientes o mockeadas.

## 13. Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [frontend/AGENTS.md](../frontend/AGENTS.md)
- [docs/PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)

## Actualización Tasks 10–15 (20/09/2026)

Envío transaccional, bandeja ADMIN, dashboards, reportes/exportaciones y auditoría
están implementados y verificados localmente. El contenido enviado queda en lectura.
Las reglas demo y RENAPER pendiente impiden afirmar aprobación institucional.
Ver `docs/SUBMISSION_REPORTING_AUDIT.md`, `docs/MANUAL_ADMIN.md`,
`docs/MANUAL_APODERADO.md` y `docs/task/INFORME_10_15.md` desde la raíz.
