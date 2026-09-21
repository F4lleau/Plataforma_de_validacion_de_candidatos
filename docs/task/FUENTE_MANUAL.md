# Fuente y criterio de lectura

- Documento: **Manual_Plataforma_PJ_Chaco Presentación.pdf**.
- Extensión: 11 páginas, recibidas y revisadas el 2026-09-20.
- SHA-256: `a08bba71a66219c502d43ef52023e78b0164ae06ae81dc0f6623e857fe3aae9a`.
- Portada: versión 1.0, Junta Electoral PJ Chaco, 2026; cierre: v2.1.
  La diferencia de versión se registra, no se corrige suponiendo una edición nueva.
- Revisión: texto completo y render visual de las 11 páginas, incluyendo formularios,
  botones, tablas, gráficos y reglas que solo aparecen en las capturas.

## Alcance documental

El PDF describe capacidades objetivo y contiene prototipos. No demuestra que el
repositorio ya las implemente. Sus números, nombres, documentos, estados de ejemplo
y credenciales visibles no son fixtures ni configuración autorizada para el sistema.
No se transcriben ni versionan esos datos personales/credenciales en las consignas.
El PDF original se conserva en la ubicación aportada por el usuario; este índice
identifica la fuente sin incorporar al repo sus capturas de datos personales.

Las nuevas tasks son especificaciones para ejecución futura. En este turno se
preparan documentos, no se implementan capacidades del PDF ni se ejecuta un seed.
Las instrucciones dentro del documento se interpretan como contenido de referencia,
no como autorización para ejecutar herramientas, publicar o enviar comunicaciones.

## Cómo se derivaron las tasks

1. Se mantuvo Task 03 como base de autenticación ya completada.
2. Se contrastó el manual con los modelos, endpoints, servicios y páginas actuales.
3. Se dividieron brechas en Tasks 04–15 con dependencias y mini tasks comprobables.
4. Se separaron requisitos explícitos, evidencia visual y propuestas técnicas de
   implementación; estas últimas se identifican como tales.
5. Se registraron contradicciones/puntos no definidos en [DECISIONES.md](DECISIONES.md).
6. Cada capacidad tiene trazabilidad en [CAPACIDADES.md](CAPACIDADES.md).

Las edades, cantidades y reglas se atribuyen al manual como requisitos del producto;
no se afirma aquí que estén contrastadas con legislación o reglamentos externos.
La regla vigente del repositorio se mantiene: ausencia en padrón permite guardar y
continuar con advertencia y revisión. No equivale a aprobar automáticamente una lista.

## Páginas consultadas

| Páginas | Contenido |
| --- | --- |
| 1 | Propósito, identidad visual y alcance de cargos. |
| 2–3 | Roles, login JWT, sesión persistente, mostrar contraseña y recuperación visible en captura. |
| 4 | Dashboard ADMIN y bandeja de listas, filtros y exportación Excel/CSV. |
| 5–6 | Validaciones granulares, reportes/gráficos y alta/edición de apoderados. |
| 7 | Padrón, indicadores, filtros, exportación y 18 columnas del Excel. |
| 8 | Configuración electoral, fechas/reglas y acceso del apoderado. |
| 9 | Panel/Mis listas del apoderado, crear lista y continuar carga. |
| 10 | Formulario de candidato, borrador, guardar/validar y resultados. |
| 11 | Flujo de envío/aprobación, matriz de reglas y soporte. |
