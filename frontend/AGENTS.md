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

La aplicación integra React Router, login, sesión Zustand validada mediante `/auth/me`,
rutas protegidas y navegación por rol en escritorio y móvil. Padrón, carga de candidatos,
revisión administrativa y consulta de listas/plantillas consumen endpoints reales.

Configuración, apoderados/asignaciones y CRUD de listas/candidatos están implementados.
Envío/aprobación condicionada, bandeja y auditoría están implementados. No se habilitó
revisión administrativa resolutiva ni reapertura sin definición institucional. No existe un directorio `src/modules`
implementado; el código actual se organiza en `pages`, `services`, `stores` y `components`.

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

- `npm run test` (Vitest: sesión y cliente API)
- `npm run build`
- `npm run lint` cuando corresponda

No declarar una task terminada si existen errores conocidos relacionados con los cambios realizados.

## Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [docs/PROJECT_CONTEXT.md](../docs/PROJECT_CONTEXT.md)
- [docs/BUSINESS_RULES.md](../docs/BUSINESS_RULES.md)
- [frontend/README.md](README.md)

## Actualización Tasks 04–09 (20/09/2026)

Configuración, catálogos, usuarios/módulos, padrón de 18 campos, listas con asignación
explícita y edición de candidatos tienen API y UI reales. RENAPER permanece pendiente
sin proveedor; no devuelve OK ficticio. Ver [contratos y recorrido](../docs/ELECTORAL_WORKFLOWS.md).
Tasks 10–14 y aceptación local de 15 están implementadas. RENAPER real y aceptación
institucional siguen pendientes. Ver docs/task/INFORME_10_15.md desde la raíz.

## Actualización Tasks 10–15 (20/09/2026)

Envío transaccional, bandeja ADMIN, dashboards, reportes/exportaciones y auditoría
están implementados y verificados localmente. El contenido enviado queda en lectura.
Las reglas demo y RENAPER pendiente impiden afirmar aprobación institucional.
Ver `docs/SUBMISSION_REPORTING_AUDIT.md`, `docs/MANUAL_ADMIN.md`,
`docs/MANUAL_APODERADO.md` y `docs/task/INFORME_10_15.md` desde la raíz.

## Actualización Tasks 16–19 (21/09/2026)

El contrato vigente incorpora access JWT con sid, refresh opaco rotativo HttpOnly,
sesiones revocables, CSRF, Argon2id (bcrypt legacy), bloqueo temporal, desbloqueo ADMIN,
recuperación/cambio de clave y SMTP mediante outbox cifrada/worker. Ver
`docs/AUTHENTICATION.md` y `docs/AUTH_OPERATIONS.md` desde raíz: reemplazan las
limitaciones históricas de login/clave descritas en secciones previas. Invitaciones (Task 20) ya implementadas: reemplazan el alta manual. ADMIN no fija
contraseñas ajenas ni modifica correos sin verificación.

## Tasks 20–21: invitaciones y aceptación local

Alta por invitación de un uso (48 h), reenvío/cancelación ADMIN, primer acceso con
perfil/contraseña, email verificado y permisos mínimos. Las cuentas existentes se
conservan sin afirmar verificación histórica. Migración `a72e903d418f`; Mailpit para
pruebas, SMTP externo aún pendiente. Variables en `backend/.env.example` desde raíz.
Ver [contratos](../docs/AUTHENTICATION.md), [operación](../docs/AUTH_OPERATIONS.md)
y [informe consolidado](../docs/task/INFORME_16_21.md).

## Task 22: aceptación inicial

Una identidad autenticada puede seguir pendiente de términos: `ProtectedRoute`
exige `user.terms_accepted_at`. El login presenta checkbox/confirmación y actualiza
perfil solo tras respuesta del backend. `LegalAccess`/`LegalModal` comparten lectura
pública de documentos entre login/footer; no duplicar contenido en el bundle ni
persistir aceptación en localStorage. Un 403 `TERMS_ACCEPTANCE_REQUIRED` vuelve al
paso pendiente sin bucles de refresh. Ver [contratos](../docs/AUTHENTICATION.md).
