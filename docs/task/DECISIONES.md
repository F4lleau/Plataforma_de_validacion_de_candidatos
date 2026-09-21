# Decisiones, contradicciones y dependencias

Estas entradas evitan transformar una captura o un ejemplo en una regla no confirmada.
No bloquean la redacción de las tasks ni todo el desarrollo: al ejecutar, resolver la
mini task dependiente y avanzar con las partes independientes. Registrar la decisión,
fecha, responsable y evidencia aquí; no interpretar el silencio como aprobación.

| ID | Fuente / diferencia observada | Criterio de planificación y punto a resolver | Tasks afectadas | Estado |
| --- | --- | --- | --- | --- |
| D01 | Configuración p. 8 muestra 16 posiciones para Diputados; tabla p. 11 indica 16 titulares + 8 suplentes. El seed local de prueba no tiene cantidades oficiales. | Objetivo provisional basado en la tabla explícita: 24 posiciones, 16+8. Confirmar antes de fijar plantilla/reglas definitivas; no copiar la cantidad del seed. | 04, 07, 10 | Pendiente |
| D02 | P. 11 exige 22 cargos en Consejos pero no enumera nombres, orden ni distribución titular/suplente. | Obtener plantilla oficial. Se puede implementar estructura configurable; no inventar denominaciones institucionales ni presentar 22 cargos genéricos como plantilla definitiva. | 04, 07, 10 | Pendiente |
| D03 | Edad mínima 25/21 en p. 11 sin fecha de cómputo. | Definir si se calcula al día electoral, cierre, presentación u otra fecha; hasta resolverlo no emitir un OK concluyente por edad. | 04, 08 | Pendiente |
| D04 | Captura p. 8 menciona requisitos de edad y ciudadanía; no hay umbral/criterio de ciudadanía, residencia o antigüedad. | Implementar edad cuando se defina D03. Mantener los demás requisitos pendientes/no configurados; no inventar verificaciones ni tratarlos como cumplidos. | 04, 08 | Pendiente |
| D05 | P. 11 establece paridad 50/50 y alternancia solo en Consejos. El servicio actual aplica alternancia a todo cargo y el PDF no define paridad por grupo ni tratamiento de categorías distintas de M/F. | Respetar diferencia por cargo. Confirmar paridad global o por titulares/suplentes, alcance de alternancia entre grupos y categorías antes de activar reglas definitivas. No inventar exclusiones de personas. | 04, 07, 10 | Pendiente |
| D06 | Manual pide afiliación obligatoria; AGENTS exige guardar ausentes del padrón con warning. Excel contiene estado de afiliación/estado elector. | La carga no bloqueante ya está resuelta por AGENTS y se conserva. Para aprobación, una observación no equivale a OK. Confirmar estados válidos del padrón y tratamiento administrativo sin inventar una dispensa. | 06, 08, 10, 11 | Regla de carga confirmada; detalle de estados pendiente |
| D07 | Manual exige RENAPER; repositorio solo tiene cliente base y stubs que pueden devolver OK. No se aportó contrato ni acceso a proveedor. | Corregir estados honestos y preparar integración. Solicitar proveedor/documentación/credenciales autorizadas al ejecutarla; no dar por integrada una prueba mock ni aprobar datos reales por simulación. | 09, 10, 15 | Dependencia externa pendiente |
| D08 | Flujo p. 11: validar composición → enviar → aprobar si todo cumple. Capturas muestran listas de pocos candidatos ya enviadas; no explican reabrir, corregir después del envío o resolver observaciones manualmente. | Definir máquina de estados, condiciones de envío, edición/reapertura y facultades administrativas. Conservar envío y aprobación como eventos distintos; ningún error/pendiente se trata como aprobación. | 08, 10, 11 | Pendiente |
| D09 | Manual habla de listas propias/asignadas y número de lista. UserModule actual da alcance por módulo; municipio de candidato está en Person. No se define propiedad compartida, unicidad del número, multiplicidad de elecciones activas ni cierre horario. | Definir propiedad/asignación por lista, transferencias, número, fechas/zona y duplicados entre listas. Separar distrito electoral de domicilio: lista determina contexto, no el domicilio personal. Proponer migración explícita de datos existentes. | 04, 05, 07, 08, 12 | Pendiente |
| D10 | Captura p. 3 muestra Olvidó su contraseña y p. 11 remite a la Junta para soporte/credenciales; no hay canal concreto ni proveedor de correo. | Definir contacto real configurable y recuperación asistida o automática. Se puede ofrecer ayuda funcional asistida; no inventar email/teléfono ni simular envíos. | 05, 15 | Pendiente |
| D11 | P. 7 enumera 18 columnas oficiales, usa Matrícula y muestra Exportar; no aporta archivo real, tipos, catálogo de estados ni formato de exportación. | Validar equivalencia Matrícula/documento, fechas, obligatoriedad/aliases, duplicados y soporte XLS/XLSX con muestra autorizada. Propuesta técnica: XLSX/CSV para exportar padrón; confirmar formato final. | 06, 13 | Pendiente |

## Reglas ya suficientemente explícitas para planificar

- Dos roles: ADMIN con supervisión global y APODERADO restringido por habilitaciones.
- Padrón importado desde Excel, sin API externa de afiliación.
- Diputados y Consejos Locales como cargos de esta etapa.
- Guardar borrador y Guardar y validar son acciones distintas del formulario.
- Paridad 50/50 en ambos cargos; alternancia no obligatoria para Diputados y sí para Consejos.
- Listas se envían y solo se aprueban automáticamente si todos los controles obligatorios cumplen.
- Bandeja de listas: búsqueda/estado, exportación Excel/CSV.
- Reportes: cargo/localidad/estado/apoderado, exportación Excel/PDF.
- Capturas, conteos y fechas de ejemplo no representan criterios de aceptación reales.

## Registro de decisiones al ejecutar

Para cada ID resuelto agregar: decisión, evidencia o respuesta del usuario, fecha,
impacto en código/migración/tests y tasks a actualizar. No marcar resuelto por una
suposición técnica que cambia el comportamiento electoral.

## Decisiones de ejecución — 20/09/2026

El usuario autorizó **datos de prueba sin plantilla oficial** y **preparar RENAPER sin API**.
Esto ajusta el cierre de Tasks 04–09; no confirma normativa ni acceso externo.

- D01/D02: configuración de prueba 24 (16+8) y 22 posiciones genéricas, `template_is_test=true`. Pendiente plantilla oficial.
- D03/D04: referencia de edad configurable; demo usa fecha electoral, edad 25/21. Otros requisitos permanecen pendientes. Cumpleaños del 29/02: 01/03 en año no bisiesto para esta implementación de prueba.
- D05: reglas versionadas distinguen alternancia por cargo; género sin política confirmada queda pendiente.
- D06/D11: interpretación de prueba Matrícula=DNI; solo ACTIVO verifica. Otros estados/ausencia generan warning no bloqueante. XLSX probado; XLS rechazado. Muestra institucional pendiente.
- D07: preparación completada con cliente no configurado; no se implementó contrato HTTP ficticio. Acceso, adapter HTTP, límites y prueba real diferidos expresamente.
- D08 (actualizado): el usuario confirmó composición completa para enviar, observaciones/pendientes permiten revisión y el contenido queda en lectura tras enviar. Borrador/incompleta/rechazada por composición admiten corrección.
- D09: decisión técnica para el entorno de prueba: asignación compartida explícita, módulo más lista; número único por elección/cargo/distrito, días inclusivos Argentina, varias elecciones activas. No se prohíben postulaciones entre listas sin norma confirmada. Listas históricas conservadas, asignación al creador apoderado, sin reglas/fechas inventadas.
- D10: recuperación asistida ADMIN, contraseña nueva, ayuda en login y `SUPPORT_CONTACT` opcional; no hay correo automático ni dirección inventada.

Los detalles verificables están en [flujos actuales](../ELECTORAL_WORKFLOWS.md).

## Ejecución Tasks 10–15 — 20/09/2026

D08 confirmado explícitamente por el usuario: «Sí, usar ese criterio», referido a
impedir envío por composición, permitir pendientes de afiliación/RENAPER en lista
completa y dejarla en lectura. No se concedieron aprobación manual ni reapertura.
D05: paridad global de prueba y alternancia global solo cuando está configurada;
registros X se guardan, pero falta política para resolver su composición institucional.
D09: selector muestra todas las elecciones autorizadas o una elegida; últimas listas
por ID de creación descendente; estados excluyentes y tasa aprobadas/total filtrado.
D10: Ayuda por rol, contacto configurable y recuperación asistida implementados;
el valor institucional del contacto permanece pendiente de provisión.
D11: formatos técnicos adoptados para prueba: padrón XLSX/CSV de sus 18 campos.
No se obtuvo muestra institucional ni se amplió soporte a XLS.

Estas decisiones operativas no cierran D01–D07 como normativa o integración real.
