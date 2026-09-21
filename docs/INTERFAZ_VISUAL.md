# Interfaz visual

La actualización visual toma como referencia [Inerxia — Sistema operativo](https://www.inerxia.ai/sistema-operativo), adaptada a la gestión electoral. No utiliza sus logos ni reproduce sus contenidos comerciales.

## Componentes y criterios

- Inter para títulos y contenido; JetBrains Mono para indicadores y etiquetas de sección, con fuentes de respaldo locales. Las fuentes web se solicitan a Google Fonts, como en la interfaz anterior.
- Fondos claros, texto azul oscuro, acciones azules, bordes finos y superficies blancas. Los estilos compartidos viven en `frontend/src/index.css` y `frontend/tailwind.config.js`.
- `Brand`, `PageHeading`, `Panel`, `Field`, `Feedback` y `StatusBadge` mantienen la identidad y los patrones reutilizables.
- Navegación agrupada por función y filtrada por rol. En escritorio permanece visible; debajo de 1024 px se abre con un botón que informa su estado. Se cierra al navegar o con Escape desde la navegación, devolviendo el foco al botón.
- Enlace para saltar al contenido, foco visible, áreas de acción de al menos 40 px y respeto a la preferencia de movimiento reducido.
- Los estados siempre incluyen texto: borrador/pendiente neutro, observaciones ámbar, validación/envío azul y aprobación/verificado verde. El color no determina permisos ni decisiones de negocio.
- Dashboard con métricas existentes, distribución real de estados y accesos por rol. No se generan tendencias o actividad ficticias.
- Formularios, tablas, reportes, auditoría, candidatos y ayuda comparten la base visual. Las tablas extensas conservan desplazamiento horizontal dentro de su región.
- Login con presentación institucional en escritorio y formulario compacto en móvil; ayuda con preguntas desplegables.

## Alcance funcional

Se mantienen los contratos API, los permisos y las reglas de validación. Una observación de afiliación permite guardar; RENAPER permanece pendiente de integración real. Las listas enviadas conservan el modo lectura. En el listado se muestra «Ver lista» para estados no editables y se incluye el estado existente «Composición observada» en el filtro.

## Verificación

Ejecutar `npm run test`, `npm run build` y `npm run lint` desde `frontend/`. Revisar con datos locales ambos roles, navegación, filtros, controles de acceso, detalle de listas y estados. Comprobar escritorio y móvil, incluido el desplazamiento de tablas y la ausencia de desborde horizontal de la página.

Tasks 16–19: las fuentes usan fallback local; se retiró la carga externa de Google Fonts para que recuperación no solicite recursos a terceros.
