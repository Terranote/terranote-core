# terranote-core

> Versión recomendada para adaptadores (fase 1): `v1.0.0-fase1`

Módulo central (fase 1) de Terranote para orquestar la creación de notas en OpenStreetMap desde aplicaciones de mensajería.

## Objetivo

Este servicio expone una API REST (FastAPI) que:
- Recibe interacciones de adaptadores (WhatsApp/Telegram) y agrupa los mensajes por usuario.
- Construye notas anónimas cuando recibe texto y ubicación en las ventanas de tiempo definidas (20 s entre mensajes, 2 min por sesión).
- Genera notas stub en OSM (fase 1) y devuelve la URL al adaptador.
- Ofrece endpoints básicos de estado y creación manual de notas.

## Requisitos

- Python 3.11+
- [Poetry](https://python-poetry.org/) 1.8+

## Instalación

Se recomienda usar un entorno virtual local:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Ejecución

```bash
.venv/bin/uvicorn app.main:app --reload
```

Variables de entorno relevantes:

- `OSM_API_BASE_URL`: URL base del API de OpenStreetMap (por defecto `https://api.openstreetmap.org`).
- `OSM_API_TIMEOUT_SECONDS`: timeout de peticiones en segundos (por defecto `10.0`).
- `OSM_MAX_RETRIES`: número máximo de reintentos para fallas temporales (por defecto `2`).
- `OSM_RETRY_BACKOFF_SECONDS`: factor base de backoff exponencial para reintentos (por defecto `0.2`).
- Los logs usan el logger estándar de Python; configura `LOGLEVEL` antes de ejecutar uvicorn para ajustar la verbosidad (por ejemplo, `LOGLEVEL=info`).

## Pruebas

```bash
.venv/bin/pytest
```

Para generar reporte de cobertura:

```bash
.venv/bin/pytest --cov --cov-report=term-missing
```

El workflow de GitHub Actions (`.github/workflows/ci.yml`) ejecuta lint (ruff, black, mypy) y pruebas con cobertura en cada push/PR.

Consulta `docs/interfaces.md` para los contratos de entrada/salida de los adaptadores.

### Repositorios auxiliares

- **Infraestructura compartida**: utiliza el repositorio [`terranote-infra`](https://github.com/Terranote/terranote-infra) para levantar el núcleo junto con adaptadores y servicios auxiliares (fake OSM, túneles, observabilidad). Los escenarios `docker-compose` de ese proyecto están alineados con la estructura de este repositorio: basta con clonar ambos en la misma carpeta y exportar `COMPOSE_PROFILES=core,fakes` para ejecutar `docker compose up` desde `terranote-infra`.
- **Pruebas de extremo a extremo**: el repositorio [`terranote-tests`](https://github.com/Terranote/terranote-tests) contiene suites de integración y carga que consumen la API expuesta por `terranote-core`. Después de levantar la infraestructura con `terranote-infra`, posiciona tu terminal en `terranote-tests` y ejecuta `poetry run pytest -m "e2e or smoke"` para validar los flujos principales. Consulta su README para ver los perfiles disponibles (`smoke`, `regression`, `load`).

## Observabilidad

### Health Check (`GET /api/v1/status`)

Endpoint de salud mejorado que incluye:
- **Estado general**: `ok`, `degraded`, o `down` basado en dependencias
- **Información del sistema**: uptime, versión, ambiente
- **Verificación de dependencias**: estado de la API de OSM
- **Métricas de notas**: intentos, éxitos, errores HTTP, errores de red, respuestas inválidas, reintentos

Ejemplo de respuesta:
```json
{
  "status": "ok",
  "uptime": 3600,
  "version": "1.0.0",
  "environment": "production",
  "dependencies": {
    "osm": {
      "status": "ok",
      "message": null
    }
  },
  "metrics": {
    "attempts": 150,
    "successes": 145,
    "http_errors": 3,
    "network_errors": 2,
    "invalid_responses": 0,
    "retries": 5
  }
}
```

### Métricas Prometheus (`GET /metrics`)

Endpoint que expone métricas en formato Prometheus:

**Métricas de publicación de notas:**
- `terranote_note_publication_attempts_total`: Total de intentos de publicación
- `terranote_note_publication_successes_total`: Publicaciones exitosas
- `terranote_note_publication_http_errors_total`: Errores HTTP
- `terranote_note_publication_network_errors_total`: Errores de red
- `terranote_note_publication_invalid_responses_total`: Respuestas inválidas
- `terranote_note_publication_retries_total`: Reintentos

**Métricas HTTP (capturadas automáticamente):**
- `terranote_http_requests_total`: Total de peticiones HTTP (labels: method, route, status)
- `terranote_http_request_duration_seconds`: Duración de peticiones HTTP (histograma)

**Métricas de OSM API:**
- `terranote_osm_api_calls_total`: Total de llamadas a OSM API (label: status)
- `terranote_osm_api_call_duration_seconds`: Duración de llamadas a OSM API (histograma)

**Autenticación básica opcional:**
El endpoint `/metrics` puede protegerse con autenticación básica configurando:
- `METRICS_USERNAME`: Usuario para autenticación (opcional)
- `METRICS_PASSWORD`: Contraseña para autenticación (opcional)

Si no se configuran, el endpoint es público.

### Logging

Las publicaciones en OSM registran logs informativos y de advertencia/errores con detalles de latitud y longitud para facilitar el diagnóstico.

### Ejecutar con Prometheus (Docker)

```bash
docker compose -f docker/compose.prometheus.yml up --build
```

Esto levantará el servicio `terranote-core` (puerto `8000`), el fake de OSM (`fake-osm`, puerto `8080`) y Prometheus (`9090`). El fake expone `/api/0.6/notes.json` con un escenario configurable vía:

```bash
curl -X POST http://localhost:8080/__control__/scenario \
  -H 'Content-Type: application/json' \
  -d '{"mode":"http_error","status_code":429}'
```

Para volver al comportamiento por defecto:

```bash
curl -X POST http://localhost:8080/__control__/reset
```

Prometheus (job `terranote-core`) hace scrape cada 10 segundos a `/metrics`.

### Pruebas end-to-end

```bash
docker compose -f docker/compose.prometheus.yml up --build
```

- `terranote-core`: expuesto en `http://localhost:8000`
- `fake-osm`: expuesto en `http://localhost:8080` (configurable vía curl como se indica arriba)
- Prometheus: `http://localhost:9090`

El adaptador de WhatsApp puede apuntar a `http://localhost:8000/api/v1/interactions` y registrar su callback (`NOTIFIER_WHATSAPP_ENDPOINT`) apuntando a su propio servidor local.

## Docker

```bash
docker build -t terranote-core:dev .
docker run -p 8000:8000 terranote-core:dev
```

## Fakes disponibles

- `FakeOSMClient`: fixture en `tests/conftest.py`, ideal para pruebas unitarias en memoria.
- `fakes/osm_api`: servicio HTTP emulado disponible en Docker (ver sección Prometheus) con escenarios configurables vía `/__control__/scenario`.

## Configuración

| Variable                         | Descripción                                                | Valor por defecto                     |
|---------------------------------|------------------------------------------------------------|---------------------------------------|
| `OSM_API_BASE_URL`              | URL del API de OSM (o fake)                                | `https://api.openstreetmap.org`       |
| `OSM_API_TIMEOUT_SECONDS`       | Timeout de peticiones a OSM                                | `10.0`                                |
| `OSM_MAX_RETRIES`               | Reintentos ante fallos temporales al crear nota            | `2`                                   |
| `OSM_RETRY_BACKOFF_SECONDS`     | Factor de backoff para reintentos                          | `0.2`                                 |
| `NOTIFIER_WHATSAPP_ENDPOINT`    | Callback del adaptador WhatsApp para notificaciones        | `null` (deshabilitado)                |
| `NOTIFIER_TELEGRAM_ENDPOINT`    | Callback del adaptador Telegram para notificaciones        | `null` (deshabilitado)                |
| `OFFLINE_GAP_SECONDS`           | Umbral para tratar mensajes como offline y usar `/batch`    | `5`                                   |
| `METRICS_USERNAME`              | Usuario para autenticación básica en `/metrics` (opcional) | `null` (sin autenticación)            |
| `METRICS_PASSWORD`              | Contraseña para autenticación básica en `/metrics` (opcional) | `null` (sin autenticación)            |
