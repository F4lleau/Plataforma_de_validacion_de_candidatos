# Organización del backlog desde el manual

Fecha: 2026-09-20. Rama de trabajo: `develop`.

## Resultado

- Se quitó la exclusión de `docs/task/` del `.gitignore`.
- Se conservó Task 03 completada, su estado, informe y evidencia visual histórica.
- Su consigna original se preservó en `task-original.txt`; `task.md` incorpora un
  checklist de cierre en cada una de sus 22 mini tasks, sin cambiar los requisitos.
- Se crearon Tasks 04–15 con objetivo, auditoría, mini tasks/checklists, tests,
  verificación, prueba manual, informe final y definición de done.
- Se agregaron índice por orden/dependencias, matriz de 26 capacidades, referencia
  de fuente y registro de 11 decisiones/ambigüedades.

## Alcance de este turno

Trabajo documental y organización de Git. No se implementaron las nuevas tasks,
no se cambiaron reglas de negocio activas ni modelos, no se ejecutaron migraciones
ni seeds y no se hicieron commit ni push. Los cambios de código/setup de los turnos
anteriores se conservan sin incorporarlos al staging de este trabajo documental.

El PDF se leyó como fuente de capacidades objetivo, incluyendo todas sus capturas.
No se incorporaron al repo sus datos personales/credenciales de demostración ni se
asumió que una pantalla de prototipo equivale a funcionalidad implementada.

## Validación documental

- Consigna original de Task 03 comparada con el archivo recibido.
- Tasks numeradas consecutivamente 04–15 y dependencias previas existentes.
- Todas las secciones numeradas tienen al menos una casilla de checklist.
- Checklists nuevos sin marcar; Task 03 conserva cierre verificado históricamente.
- 26 capacidades de la matriz referenciadas por las consignas correspondientes.
- Enlaces Markdown locales comprobados, excepto links históricos externos al
  backlog que reflejen snapshots anteriores.
- Exclusión de Git retirada; archivos de tareas agregados al índice de Git.
- `git diff --check` y `git diff --cached --check` sin errores.

No corresponde repetir pytest/build para estos cambios documentales; sus resultados
anteriores se conservan como históricos en el informe de Task 03.

## Siguiente paso

Ejecutar Task 04 cuando el usuario lo indique, comenzando por la auditoría y las
decisiones de configuración. Las tasks siguientes quedan preparadas y ordenadas;
RENAPER y ciertas reglas electorales requieren las definiciones registradas en
DECISIONES.md antes de cerrar sus mini tasks dependientes.
