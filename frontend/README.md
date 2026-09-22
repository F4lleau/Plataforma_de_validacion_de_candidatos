# Frontend - Junta Electoral

## Descripción del Sistema

La aplicación frontend de Junta Electoral es una SPA desarrollada en React + TypeScript, que permite la gestión visual de listas, candidatos y validaciones electorales.

### Requisitos Funcionales

- Login y autenticación de usuarios.
- Visualización y gestión de listas y candidatos.
- Validaciones y reportes.

### Requisitos No Funcionales

- Responsive Design (adaptable a dispositivos móviles).
- Seguridad en el manejo de sesiones.
- Buenas prácticas de accesibilidad.

## Arquitectura

- **Framework:** React
- **Lenguaje:** TypeScript
- **Gestor de paquetes:** npm
- **Estilos:** TailwindCSS
- **Empaquetador:** Vite

### Estructura de Carpetas

- `src/`: Código fuente principal
- `public/`: Recursos estáticos
- `App.tsx`: Componente raíz

### Diagrama de Componentes

> **Consejo:** Agregar un diagrama visual con herramientas como [Mermaid](https://mermaid-js.github.io/mermaid/) o [draw.io].

```
flowchart TD
    UI[Usuario] --> App[React App]
    App --> API[API Backend]
```

## Guía de Configuración

Para levantar la aplicación con API y PostgreSQL en Docker, seguir la
[guía de desarrollo local](../README.md).

### Clonar el Repositorio

```bash
git clone <url-del-repo>
cd junta_electoral/frontend
```

### Instalar Dependencias

```bash
npm install
```

### Ejecutar la App

```bash
npm run dev
```

La aplicación inicia en `/login`, restaura la sesión mediante `/api/v1/auth/me` y protege las rutas por rol. ADMIN accede al padrón y a la revisión administrativa; APODERADO accede a sus listas y a la carga de candidatos.

Ver [autenticación y prueba manual](../docs/AUTHENTICATION.md). `npm run test`
ejecuta las pruebas de sesión y cliente API con Vitest. Completar la verificación
con `npm run build` y `npm run lint`.

### Variables de Entorno

El cliente actual usa `http://localhost:8000/api/v1` en `src/services/api.ts`.
No necesita un `.env` de frontend para el entorno local documentado.

## Documentación de Usuario

### Guías de Uso

- Inicia sesión con tus credenciales.
- Navega por los módulos de listas, candidatos y validaciones.

### FAQ

- **No carga la app:** Verifica que el backend esté corriendo y la URL de `src/services/api.ts` sea correcta.
- **Problemas de login:** Revisa usuario y contraseña, y que el backend esté accesible.

### Solución de Problemas

- **Error de dependencias:** Ejecuta `npm install`.
- **Pantalla en blanco:** Revisa la consola del navegador para errores.

## Documentación del Proyecto

### Objetivo del Negocio

Brindar una interfaz amigable para la gestión y validación de procesos electorales.

---

> **Automatización:** Se recomienda documentar componentes y hooks con comentarios y herramientas como Storybook o Docz.

## Actualización Tasks 04–09 (20/09/2026)

Configuración, catálogos, usuarios/módulos, padrón de 18 campos, listas con asignación
explícita y edición de candidatos tienen API y UI reales. RENAPER fue retirado
del alcance el 22/09/2026 por pedido del usuario. Ver [contratos y recorrido](../docs/ELECTORAL_WORKFLOWS.md).
Las menciones anteriores a estos CRUD como pendientes quedan reemplazadas por este estado.
Tasks 10–14 y aceptación local de 15 están implementadas. La aceptación
institucional sigue pendiente. Ver docs/task/INFORME_10_15.md desde la raíz.

## Actualización Tasks 10–15 (20/09/2026)

Envío transaccional, bandeja ADMIN, dashboards, reportes/exportaciones y auditoría
están implementados y verificados localmente. El contenido enviado queda en lectura.
Las reglas demo impiden afirmar aprobación institucional.
Ver `docs/SUBMISSION_REPORTING_AUDIT.md`, `docs/MANUAL_ADMIN.md`,
`docs/MANUAL_APODERADO.md` y `docs/task/INFORME_10_15.md` desde la raíz.

## Diseño de la interfaz

La interfaz comparte tipografía, colores, formularios, paneles y etiquetas de estado.
La navegación agrupa los módulos por rol y se despliega con un menú en móvil.
El dashboard presenta métricas y distribución de estados de la API, junto con accesos rápidos.
Ver [criterios y componentes visuales](../docs/INTERFAZ_VISUAL.md).

## Seguridad de acceso (Tasks 16–19)

Access solo en memoria; refresh HttpOnly con rotación, restore tras recarga y coordinación
entre pestañas. Rutas `/recuperar-clave`, `/restablecer-clave`, `/seguridad`.
ADMIN consulta/desbloquea cuentas y envía recuperación tras reautenticación.
Task 20 agrega `/invitacion` y administración de invitaciones en `/usuarios`. Configurar `VITE_API_URL` desde `.env.example`
si se requiere; API/frontend deben compartir sitio. Ver `docs/AUTHENTICATION.md`
y `docs/AUTH_OPERATIONS.md` desde raíz. Fuentes con fallback local, sin requests a
Google Fonts en páginas que manejan enlaces de recuperación.

Ver [aceptación 16–21](../docs/task/INFORME_16_21.md) y [contrato de invitaciones](../docs/AUTHENTICATION.md).
