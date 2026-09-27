# Deploy QA

Objetivo: publicar un entorno provisorio de QA con frontend público y backend
FastAPI usando la misma base Neon de desarrollo.

## Rama

Trabajar desde `develop` y publicar una rama `qa`:

```bash
git checkout develop
git pull origin develop
git checkout -B qa
git push -u origin qa
```

## Backend en Render

El repo incluye `render.yaml` y `backend/Dockerfile`.

Crear un Blueprint o Web Service en Render desde la rama `qa`. El servicio esperado
es `junta-electoral-api-qa`.

Variables obligatorias en Render:

```bash
DATABASE_URL=<misma URL de Neon usada en desarrollo>
SECRET_KEY=<clave aleatoria de al menos 32 bytes>
MAIL_OUTBOX_KEY=<clave Fernet>
CORS_ORIGINS=["https://<frontend-qa>.netlify.app"]
FRONTEND_URL=https://<frontend-qa>.netlify.app
```

Variables ya declaradas en `render.yaml`:

```bash
APP_ENV=development
DEBUG=false
COOKIE_SECURE=true
COOKIE_SAMESITE=none
SUPPORT_CONTACT=juspjchaco@gmail.com
```

Cuando el backend levanta, el contenedor ejecuta:

```bash
python -m alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Healthcheck:

```text
/api/v1/auth/health
```

## Frontend en Netlify

El repo incluye `netlify.toml`.

Crear el sitio desde la rama `qa` con:

```bash
base = frontend
command = npm ci && npm run build
publish = dist
```

Actualizar la variable de build:

```bash
VITE_API_URL=https://<backend-qa>.onrender.com/api/v1
```

Si se usa el nombre default previsto por `render.yaml`, queda:

```bash
VITE_API_URL=https://junta-electoral-api-qa.onrender.com/api/v1
```

## Usuarios de prueba

Usar las cuentas ya creadas en Neon:

```text
ADMIN: verificar el email actual en la tabla users
APODERADO: verificar el email actual en la tabla users
Clave para ambos: Admin123!
```

## Notas

- No commitear `.env`, `DATABASE_URL`, `SECRET_KEY` ni `MAIL_OUTBOX_KEY`.
- Para QA provisorio se usa la misma base Neon de desarrollo por pedido del
  proyecto. Evitar pruebas destructivas de datos reales.
- Si luego se configura SMTP real, cambiar `APP_ENV=qa` o `production`,
  `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` y
  `SMTP_TLS=starttls` o `ssl`.
