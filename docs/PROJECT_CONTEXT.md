# Proyecto: Junta Electoral / Plataforma de Validación de Candidatos

## 1. Problema de negocio

La plataforma busca apoyar a la Junta Electoral del Partido Justicialista, Distrito Chaco, en la administración de listas electorales y candidatos, con foco en la validación automática y asistida antes de la revisión administrativa.

La solución debe facilitar:

- la gestión del padrón de afiliados PJ;
- la carga de candidatos por parte de apoderados;
- la validación de afiliación y requisitos de lista;
- la identificación de observaciones;
- la revisión final por parte del administrador.

## 2. Actores

### ADMIN

- administra usuarios y apoderados;
- importan y actualizan el padrón;
- revisa candidatos, listas y observaciones;
- gestiona información electoral.

### APODERADO

- trabaja sobre los módulos/listas asignados;
- carga candidatos;
- completa listas;
- consulta validaciones;
- remite listas para revisión.

## 3. Flujo general

1. El administrador importa el padrón de afiliados desde Excel.
2. El apoderado trabaja sobre una lista asignada y carga candidatos.
3. El sistema valida la composición, requisitos y afiliación.
4. Se registran observaciones o alertas si algo no coincide con el padrón o con los requisitos del cargo.
5. La lista se envía para revisión administrativa.
6. El administrador confirma, corrige o rechaza la propuesta según la validación.

## 4. Estado actual del repositorio

### Backend

El backend tiene una base funcional y estructural clara:

- modelos principales definidos;
- Alembic con migraciones reales;
- endpoints para auth, usuarios, listas, candidatos, validaciones, dashboard y padrón;
- servicios para importación de padrón y validación de lista/afiliación;
- configuración de JWT, usuarios y seguridad básica.

### Frontend

El frontend cuenta con scaffold de React + Vite + Tailwind y estructura de módulos, pero todavía no está completamente integrado funcionalmente. Hay una base visual y algunas carpetas preparadas, pero aún debe completarse:

- autenticación funcional;
- routing real por roles;
- integración con endpoints del backend;
- gestión completa de formularios;
- permisos por módulo y acceso real a funcionalidades.

## 5. Módulos existentes

### Backend

Los módulos y entidades visibles en el código reflejan estas áreas:

- usuarios
- elecciones
- municipios
- oficinas
- listas electorales
- candidatos
- validaciones
- dashboard
- padrón
- plantillas de cargos/listas

### Frontend

La estructura de `src/modules` sugiere intención de separar:

- admin
- auth
- candidatos
- listas
- reportes
- shared

Sin embargo, estos módulos no aparecen implementados en la estructura actual de forma funcional completa.

## 6. Módulos o funciones aún incompletas o pendientes

El repositorio deja claro que existen varios puntos aún no productivos o en desarrollo:

- integración RENAPER real: no hay funcionamiento productivo real.
- frontend funcional completo: no está integrado con la lógica de negocio del backend.
- permisos/routing de usuario y módulos por asignación: requieren consolidación funcional.
- importación de padrón: funciona como flujo interno con Excel, pero se debe confirmar la estructura real de datos del archivo del padrón.
- validaciones administrativas y alertas: existen bases y servicios, pero la experiencia completa aún requiere integración y refinamiento.

## 7. Integraciones

### Padrón PJ

- Integración interna mediante Excel.
- Persistencia en base de datos.
- Se registra lote de importación y miembros del padrón.
- No existe API externa de padrón.

### RENAPER

- Existe una estructura base/mock.
- No debe considerarse una integración real productiva.

## 8. Roadmap inmediato sugerido

1. consolidar la validación de afiliación y la advertencia por ausencia en padrón;
2. completar integración frontend con backend real;
3. cerrar la definición de campos y flujo de importación del padrón;
4. completar permisos y asignación de listas por apoderado;
5. definir y documentar la revisión administrativa final;
6. cerrar la lógica de validación de listas con plantillas y cargos;
7. consolidar migraciones y pruebas del backend.

## 9. Consideraciones clave para agentes

- No documentar como implementado lo que está mockeado o incompleto.
- Mantener la regla crítica del padrón: ausencia en padrón = observación/alerta, no bloqueo automático.
- Respetar la separación de capas.
- Documentar cambios reales y no asumir que existen integraciones productivas no verificadas.

## 10. Referencias

- [AGENTS.md](../AGENTS.md)
- [backend/AGENTS.md](../backend/AGENTS.md)
- [frontend/AGENTS.md](../frontend/AGENTS.md)
- [backend/README.md](../backend/README.md)
- [frontend/README.md](../frontend/README.md)
