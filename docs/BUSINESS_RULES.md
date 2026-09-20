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

La asignación de módulos/listas a apoderados es un requisito funcional central, pero la implementación real del repositorio debe tratarse como una base parcial o pendiente de consolidación en capas de UI y permisos.

No inventar reglas de asignación que no estén en el proyecto ni documentadas por el código actual.

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

## 10. Paridad y alternancia

La lógica existente aborda la paridad 50/50 y la alternancia simple por género en la validación de listas. Esto aparece implementado en `ListValidationService` como regla de validación estructural.

Sin embargo, el repositorio no demuestra un nivel completo de integración de los flujos de UX y permisos para estas reglas; por eso debe documentarse como parte de la lógica actual y no como un requisito externo no verificado.

## 11. Reglas pendientes de confirmación

Se recomienda tratar como pendientes o a confirmar las siguientes cuestiones si no hay evidencia fuerte en el código:

- detalles completos de asignación de apoderados por lista/municipio;
- especificación fina de campos del padrón Excel de origen;
- flujo exacto de revisión administrativa y estados finales de lista/candidato;
- definición completa del proceso de validación RENAPER y su activación real.

## 12. Principio general

No inventar requisitos electorales no presentes en el repositorio. Toda regla funcional debe reflejar el estado real del proyecto, y las partes incompletas deben dejarse explícitamente identificadas como pendientes o mockeadas.

## 13. Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [frontend/AGENTS.md](../frontend/AGENTS.md)
- [docs/PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)
