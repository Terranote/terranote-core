# Guía de pruebas end-to-end (fase 1)

Esta guía cubre la ejecución local de los flujos end-to-end utilizando los repositorios `terranote-infra` y `terranote-tests`. Para la visión global de Terranote, consulta el índice maestro propuesto en `terranote-docs` (ver `docs/terranote-docs-structure.md`).

## 0. Prerrequisitos

- Clonar `terranote-infra` y `terranote-tests` en el mismo directorio que `terranote-core`.
- Desde `terranote-infra`, copiar `.env.example` a `.env` si se requieren ajustes de puertos o credenciales.
- Desde `terranote-tests`, instalar dependencias:
  ```bash
  poetry install
  ```
- Verificar que Docker Desktop/Engine esté activo y con al menos 4 GB de RAM disponibles.

## 1. Levantar la infraestructura base

Ejecuta desde `terranote-infra`:

```bash
export COMPOSE_PROFILES=core,fakes,observability
docker compose up --build
```

Servicios publicados:

| Servicio          | URL                        | Descripción                                  |
|-------------------|----------------------------|----------------------------------------------|
| `terranote-core`  | `http://localhost:8000`    | API REST principal                           |
| `fake-osm`        | `http://localhost:8080`    | Emulador de OpenStreetMap                    |
| `prometheus`      | `http://localhost:9090`    | Métricas para observabilidad                 |

> Tip: puedes añadir `logs` al perfil para incluir Loki/Grafana si tu `.env` lo habilita.

## 2. Configurar escenarios del fake OSM

Ejemplo de escenario exitoso:

```bash
curl -X POST http://localhost:8080/__control__/scenario \
  -H 'Content-Type: application/json' \
  -d '{"mode":"success"}'
```

Escenarios disponibles: `success`, `http_error`, `network_error`, `invalid_response`. Usa `__control__/reset` para volver al valor por defecto.

## 3. Preparar adaptadores o simulaciones

- Para pruebas manuales, puedes usar `httpie` o `curl` contra `POST http://localhost:8000/api/v1/interactions`.
- Para cargas offline, usa `POST http://localhost:8000/api/v1/interactions/batch`.
- Si ejecutas un adaptador real (p. ej., WhatsApp), expón el callback `POST http://localhost:<puerto-adaptador>/callbacks/note-created` y configura la variable `NOTIFIER_WHATSAPP_ENDPOINT` (o el canal correspondiente) en el `.env` de `terranote-infra`.

## 4. Ejecutar las suites automatizadas

Desde `terranote-tests`:

```bash
poetry run pytest -m e2e
```

Marcadores útiles:

- `e2e`: flujos completos contra la infraestructura dockerizada (por defecto).
- `smoke`: subconjunto rápido para validaciones de pipeline.
- `load`: escenarios de carga; revisa el README de `terranote-tests` para variables como `LOAD_USERS` o `LOAD_DURATION`.

Puedes combinar marcadores, por ejemplo: `poetry run pytest -m "smoke or e2e"`.

## 5. Inspeccionar métricas y logs

- `http://localhost:8000/api/v1/status`: métricas agregadas de publicación.
- `http://localhost:8000/metrics`: exportación Prometheus.
- `docker compose logs -f terranote-core`: seguimiento en tiempo real de eventos y reintentos.
- `http://localhost:9090`: Prometheus UI para construir consultas (`terranote_note_publication_*`).

## 6. Finalizar y limpiar

Desde `terranote-infra`:

```bash
docker compose down
```

Si necesitas liberar volúmenes/caches, agrega `--volumes --remove-orphans`.

