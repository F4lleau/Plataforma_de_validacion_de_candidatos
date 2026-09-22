# Backend - Junta Electoral

## Descripción del Sistema

La aplicación backend de Junta Electoral gestiona la administración de elecciones, listas, candidatos y validaciones asociadas. Provee una API RESTful para la gestión de usuarios, listas electorales, candidatos, validaciones y auditoría.

### Requisitos Funcionales

- Gestión de usuarios y autenticación.
- Administración de listas electorales y candidatos.
- Validación de afiliaciones y candidaturas.
- Registro de logs de auditoría.
- Validaciones locales contra el padrón y las reglas electorales configuradas.

### Requisitos No Funcionales

- Seguridad basada en JWT y roles.
- Rendimiento optimizado para grandes volúmenes de datos.
- Escalabilidad y modularidad.

## Arquitectura

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Base de datos:** PostgreSQL (Docker local o Neon, configurado por entorno)
- **Migraciones:** Alembic
- **Autenticación:** JWT
- **Integraciones:** padrón importado desde Excel; sin consulta externa de identidad

### Estructura de Carpetas

- `app/`: Código principal del backend
- `alembic/`: Migraciones de base de datos
- `requirements.txt`: Dependencias

Las migraciones se encuentran en `backend/alembic/versions/`.

## Documentación de APIs

Ver [autenticación, permisos y prueba manual](../docs/AUTHENTICATION.md) para el
estado real de los endpoints y los módulos pendientes.

- **Swagger UI:** Disponible en `/docs` al ejecutar el backend.
- **Redoc:** Disponible en `/redoc`.

## Guía de Configuración

Para levantar PostgreSQL en Docker junto con el backend y el frontend locales,
seguir la [guía de desarrollo local](../README.md).

### Clonar el Repositorio

```bash
git clone <url-del-repo>
cd junta_electoral/backend
```

### Crear y Activar Entorno Virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Variables de Entorno

Configura `DATABASE_URL` y `SECRET_KEY` en `backend/.env`. El archivo se resuelve
desde el directorio de ejecución; ejecutar los comandos desde `backend/`.

### Ejecutar el Backend

```bash
uvicorn app.main:app --reload
```

### Bootstrap de administrador de desarrollo

Definí `INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` en el entorno y ejecutá:

```bash
python -m scripts.bootstrap_admin
```

El script crea un usuario ADMIN solo si no existe. Nunca guarda la contraseña en el código ni la imprime.

Autenticación con JWT access de 15 minutos, refresh opaco rotativo en cookie HttpOnly,
sesiones revocables en BD, protección CSRF, bloqueo temporal, recuperación/cambio de clave
y correo SMTP por outbox/worker. Ver [contratos](../docs/AUTHENTICATION.md) y
[operación, variables y Mailpit](../docs/AUTH_OPERATIONS.md).
Aplicar Alembic hasta `6cb192ebc9fe` y configurar `MAIL_OUTBOX_KEY` antes de iniciar.

### Migraciones de Base de Datos

```bash
alembic upgrade head
```

## Documentación de Usuario

### Guías de Uso

- Accede a la API vía Swagger UI (`/docs`).
- Consulta los endpoints disponibles y prueba operaciones.

### FAQ

- **¿Por qué falla la conexión a la base de datos?**
  - Verifica las variables de entorno y la configuración en `config.py`.
- **¿Cómo crear un usuario admin?**
  - Usa el bootstrap de administrador documentado arriba.

### Solución de Problemas

- **Error de migraciones:** Revisa el estado de Alembic y sincroniza con `alembic upgrade head`.
- **Problemas de dependencias:** Ejecuta `pip install -r requirements.txt`.

## Documentación del Proyecto

### Objetivo del Negocio

Facilitar la gestión y validación de procesos electorales, optimizando la transparencia y eficiencia.

---

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

## Tasks 20–21: invitaciones y aceptación local

Alta por invitación de un uso (48 h), reenvío/cancelación ADMIN, primer acceso con
perfil/contraseña, email verificado y permisos mínimos. Las cuentas existentes se
conservan sin afirmar verificación histórica. Migración `a72e903d418f`; Mailpit para
pruebas, SMTP externo aún pendiente. Variables en `backend/.env.example` desde raíz.
Ver [contratos](../docs/AUTHENTICATION.md), [operación](../docs/AUTH_OPERATIONS.md)
y [informe consolidado](../docs/task/INFORME_16_21.md).
