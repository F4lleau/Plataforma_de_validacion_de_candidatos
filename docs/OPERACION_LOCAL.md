# Operación y recuperación local

El [README raíz](../README.md) documenta Docker, entorno Python, instalación frontend,
migraciones y bootstrap. PostgreSQL 17 y Mailpit corren en Docker. API, worker de correo y Vite
corren en el host. Ver [operación SMTP y seguridad](AUTH_OPERATIONS.md). `reportlab>=4,<5` genera PDF sin navegador/LibreOffice en el servidor.

## Verificar

```bash
# Desde backend, con backend/.env local configurado
.venv/bin/python -m pytest -q
.venv/bin/alembic current
.venv/bin/alembic heads
.venv/bin/alembic check
# Desde frontend
npm run test
npm run build
npm run lint
```

Migración actual: `6cb192ebc9fe`, sesiones, bloqueos, recuperación y outbox de Tasks 16–19. Un entorno nuevo debe aplicar la cadena completa con Alembic.
`create_all` se usa solo en fixtures SQLite de tests, no para inicializar la aplicación.

## Copia de seguridad y prueba de restauración

Detené operaciones de escritura durante una prueba que requiera comparar recuentos exactos.
Desde la raíz, la siguiente copia conserva estructura y datos sin mostrar credenciales:

```bash
umask 077
docker compose -f local-deps.yml exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > /tmp/junta-respaldo.dump
```

Restaurá siempre en una **base nueva de prueba**, nunca encima de la base en uso:

```bash
docker compose -f local-deps.yml exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" junta_restore_verificacion'
docker compose -f local-deps.yml exec -T postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d junta_restore_verificacion --no-owner --exit-on-error' < /tmp/junta-respaldo.dump
docker compose -f local-deps.yml exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d junta_restore_verificacion -c "SELECT count(*) FROM electoral_lists;"'
```

Compará migración, usuarios, listas, candidatos, padrón y auditoría; luego conectá una API
separada a la copia si necesitás recorrerla. Mantené fuera de Git el dump y cualquier URL
con credenciales. Tras verificar, se puede eliminar **solo la base temporal creada para
esa prueba** y su dump. No usar `docker compose down -v`: borra los datos locales.
En la aceptación se restauró una copia con nombre aleatorio, se compararon seis tablas,
se ensayó envío concurrente allí y se eliminó únicamente esa copia.

## Fallos y límites

- Un lote de padrón inválido no reemplaza el vigente. Corregir/reimportar; no borrar tablas.
- Un envío repetido retorna el estado ya registrado. No editar estados directamente por SQL.
- Un error de red puede ocurrir después del commit: recargar antes de repetir altas.
- 401 intenta una renovación y luego pide login; 403 requiere revisar permisos; 409 indica conflicto de estado/plazo.
- Exportación 413: acotar filtros; máximo 50.000 registros, PDF 5.000 listas.
- `SUPPORT_CONTACT` en `backend/.env` permite mostrar el canal real en correos/Ayuda; reiniciar
  la API tras cambiarlo. Sin valor, se remite al administrador sin inventar email/teléfono.
- RENAPER fue retirado. No reemplazar requisitos institucionales pendientes por OK ni usar mocks para aprobar.
- Las fechas de auditoría se filtran por días Argentina y se almacenan UTC. PDF indica UTC.

Ver [guía ADMIN](MANUAL_ADMIN.md), [guía APODERADO](MANUAL_APODERADO.md) y
[contratos/estados](SUBMISSION_REPORTING_AUDIT.md).

Invitaciones y aceptación Tasks 20–21 usan la misma API/worker/Mailpit. Aplicar
`alembic upgrade head` (`a72e903d418f`) antes de reiniciar todos los procesos. Ver
[backup, rollback y colisiones de correo](AUTH_OPERATIONS.md#invitaciones-migración-y-despliegue-coordinado).
