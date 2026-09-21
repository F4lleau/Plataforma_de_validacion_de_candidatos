# Task 03 — Estado

> Actualización de organización (2026-09-20): `docs/task/` dejó de estar excluida
> de Git por pedido del usuario. Las menciones a carpeta ignorada y snapshots Git
> del cierre original se conservan como evidencia histórica. El estado actual es
> versionable; `task-original.txt` preserva la consigna recibida y `task.md` agrega
> un checklist de cierre por mini task.


- Estado: completada.
- Rama: `develop`.
- Consigna leída y auditoría inicial realizada el 2026-09-20.
- Se conservan los cambios locales previos de Docker/setup y los datos del seed.
- Sin commit ni push.

## Auditoría inicial

Ya existen login, `/auth/me`, JWT, hashing, roles, bootstrap ADMIN, store Zustand,
router, layout, importación de padrón, carga de candidatos y 21 tests backend.

Faltantes detectados:

- Los 401 no invalidan el estado de Zustand ni redirigen de manera consistente.
- Login no distingue error de credenciales de fallo de conexión/servidor.
- Restauración de sesión puede completar después del logout.
- JWT no exige explícitamente expiración; faltan pruebas de usuario inactivo,
  refresh usado como access y rol actualizado en BD.
- Validación de listas expuesta sin autenticación ni comprobación de asignación.
- Candidatos permite consultar todos y crear fuera de módulos asignados.
- Routers administrativos/placeholder sin protección.
- Navegación ausente en móvil y pantalla 403 sin salida.
- Listas/revisión no presentan correctamente errores de carga.
- Documentación de contexto y AGENTS desactualizada respecto del código real.

## Alcance acordado

Completar autenticación, sesión y controles de acceso usando UserModule y los
servicios/repositorios existentes. Mantener las plantillas de listas; no crear
un CRUD completo de listas ni un editor de asignaciones. Refresh/rotación y
revocación del JWT quedan documentados como trabajo posterior.


## Cierre

Todos los puntos de la consigna fueron auditados. Se completaron los faltantes de
JWT/RBAC/sesión y navegación, preservando Task 02B y el bootstrap existente.
Refresh y CRUD de listas se mantienen como pendientes explícitos, según el alcance
permitido por la consigna. No hubo cambios de modelo ni migraciones.

- Backend: 40 tests aprobados; current y heads coinciden.
- Frontend: 10 tests aprobados, build y lint correctos.
- Navegador: ADMIN, APODERADO, logout, restauración, 403, 401 en sesión y móvil comprobados.
- [Informe completo](report.md) con archivos, endpoints, estrategias, pendientes y estado Git.
- Sin commit ni push. Lista para recibir la siguiente task.
