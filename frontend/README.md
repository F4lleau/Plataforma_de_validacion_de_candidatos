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

### Variables de Entorno

Configura el archivo `.env` en `frontend/` según corresponda (ejemplo: URL del backend).

## Documentación de Usuario

### Guías de Uso

- Inicia sesión con tus credenciales.
- Navega por los módulos de listas, candidatos y validaciones.

### FAQ

- **No carga la app:** Verifica que el backend esté corriendo y la URL en `.env` sea correcta.
- **Problemas de login:** Revisa usuario y contraseña, y que el backend esté accesible.

### Solución de Problemas

- **Error de dependencias:** Ejecuta `npm install`.
- **Pantalla en blanco:** Revisa la consola del navegador para errores.

## Documentación del Proyecto

### Objetivo del Negocio

Brindar una interfaz amigable para la gestión y validación de procesos electorales.

---

> **Automatización:** Se recomienda documentar componentes y hooks con comentarios y herramientas como Storybook o Docz.
