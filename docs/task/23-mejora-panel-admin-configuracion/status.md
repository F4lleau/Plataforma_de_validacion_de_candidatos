# Task 23 — Estado

- Estado: **Implementación parcial avanzada**.
- Fecha: 22/09/2026. Rama: `develop`. Sin commit/push.
- [Consigna con checklist](task.md) · [Informe parcial](report.md).

## Implementado

- Subrutas ADMIN para Configuración:
  - `/configuracion/proceso-electoral`
  - `/configuracion/cargos`
  - `/configuracion/localidades`
- Menú lateral con subitems para Proceso electoral, Cargos y Localidades habilitadas.
- Componentes globales `ActionButton`, `BadgeLink` y `Modal` con patrón visual tipo login.
- Botones del login ajustados a tipografía mono.
- Vista de procesos electorales en tabla con crear/editar en modal y eliminación como desactivación.
- Vista de cargos en tabla con crear/editar en modal; el código estable ya no se pide en UI.
- Tipos de cargo desde BD: `electivo` y `partidario`.
- Asociación cargo-proceso electoral mediante tabla de relación.
- Vista de localidades habilitadas por proceso electoral, con selección de todas, una o algunas.
- Migración Alembic `f2b7a61d9c30` aplicada en Neon y verificada en `head`.

## Verificación

- Backend importa correctamente con `from app.main import app`.
- `npm run build` finalizado correctamente.
- `git diff --check` finalizado correctamente.
- Alembic en Neon: `f2b7a61d9c30 (head)`.
- Tipos de cargo verificados en Neon: `electivo`, `partidario`.
- `python -m pytest -q` no se completó por bloqueo de red hacia Neon durante la colección; no se reintentó contra la base remota para evitar mutaciones de datos.

## Pendiente

- Ejecutar suite completa backend/frontend y lint.
- Verificación visual manual en navegador de escritorio/móvil.
- Confirmar si la BD contiene el listado completo oficial de localidades del Chaco.
- Agregar tests específicos de los nuevos endpoints y flujos.
- Completar limpieza visual en otras vistas ADMIN no tocadas por esta primera pasada.
- Evaluar si la edición/eliminación debe bloquearse por dependencias concretas en vez de desactivar siempre.
