# Frontend AGENTS.md

## Objetivo

Documentar la base arquitectónica y de trabajo del frontend de la plataforma de validación de candidatos, con foco en la realidad actual del repositorio.

## Stack actual

- React
- TypeScript
- Vite
- Tailwind CSS
- React Query
- React Hook Form
- Zod
- Zustand
- React Router
- shadcn/ui permitido

## Estructura actual

```text
frontend/
  src/
    app/
    components/
    hooks/
    lib/
    modules/
    pages/
    services/
    types/
    assets/
    App.tsx
    main.tsx
```

## Estado real del frontend

La base visual existe y hay un scaffold inicial, pero la aplicación aún está en etapas tempranas de integración funcional. Los módulos definidos en `src/modules/` no muestran una implementación funcional completa y la app todavía debe completar:

- routing real;
- autenticación real;
- consumo de endpoints reales;
- integración de formularios y estado de servidor;
- permisos por rol y flujo de usuario.

Si se implementa una funcionalidad no documentada en el código base, debe tratarse como trabajo pendiente o incompleto, no como hecho.

## Arquitectura recomendada

### Servicios API

Mantener una capa de servicios separados de los componentes para encapsular llamadas HTTP. Esto permite:

- reutilización;
- menor acoplamiento;
- mejores pruebas y mantenimiento;
- mejor separación entre UI y contratos backend.

### Formularios

- usar React Hook Form para manejo de formularios;
- usar Zod para validaciones declarativas;
- mantener validaciones complejas fuera del propio JSX cuando sea necesario.

### Estado

- React Query para estado del servidor;
- Zustand solo cuando exista un estado global real que justifique un store;
- evitar introducir Redux sin necesidad explícita.

### Diseño y reutilización

- preferir componentes reutilizables;
- mantener consistencia visual con Tailwind;
- usar shadcn/ui donde aporte claridad sin introducir patrones innecesarios.

## Routing y permisos

El frontend debe respetar el modelo de usuario y permisos del backend:

- `admin`
- `apoderado`

Cada módulo y flujo debe diseñarse para que los permisos se validen en backend y la UI responda según el rol disponible.

## Manejo de errores

- No ocultar errores del backend;
- mostrar mensajes claros y accionables;
- distinguir estados de carga, éxito y validación;
- manejar errores de red y errores de negocio sin romper la experiencia del usuario.

## Reglas para trabajo con esta base

- mantener TypeScript estricto;
- separar servicios del UI;
- evitar duplicación de lógica;
- no introducir stacks o patrones no previstos si no hay necesidad real;
- no asumir integraciones productivas que no estén implementadas.

## Integración API y reglas críticas

La lógica del padrón y la afiliación parte del backend; el frontend no debe asumir que un candidato ausente del padrón implica rechazo automático. Debe representar la advertencia/observación y permitir continuar con el flujo.

No implementar reglas frontend que bloqueen la carga o el registro únicamente por ausencia en el padrón. Esa es una regla de negocio del backend y debe respetarse en la capa de presentación.

## Calidad

Antes de cerrar una task:

- `npm run build`
- `npm run lint` cuando corresponda

No declarar una task terminada si existen errores conocidos relacionados con los cambios realizados.

## Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [docs/PROJECT_CONTEXT.md](../docs/PROJECT_CONTEXT.md)
- [docs/BUSINESS_RULES.md](../docs/BUSINESS_RULES.md)
- [frontend/README.md](README.md)
