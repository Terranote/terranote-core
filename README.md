# terranote-core

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

## Observabilidad

- El endpoint `GET /api/v1/status` expone métricas agregadas de publicación de notas (intentos, éxitos y fallos).
- Las publicaciones en OSM registran logs informativos y de advertencia/errores con detalles de latitud y longitud para facilitar el diagnóstico.
- El endpoint `GET /metrics` expone métricas en formato Prometheus con los contadores anteriores.

### Ejecutar con Prometheus (Docker)

```bash
docker compose -f docker/compose.prometheus.yml up --build
```

Esto levantará el servicio `terranote-core` (puerto `8000`) y Prometheus (puerto `9090`) con un scrape cada 10 segundos apuntando a `/metrics`.

## Docker

```bash
docker build -t terranote-core:dev .
docker run -p 8000:8000 terranote-core:dev
```
