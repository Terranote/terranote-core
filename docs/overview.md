# Terranote Core – Fase 1

## Resumen

Servicio FastAPI que orquesta la creación de notas anónimas en OpenStreetMap a partir de interacciones recibidas desde adaptadores de mensajería. Esta fase implementa:

- Agrupación de interacciones (texto/ubicación) por usuario con restricciones de tiempo.
- Construcción de notas con identificador del sistema y publicación en la API OSM v0.6.
- Reintentos, métricas y logging para la publicación.
- Exposición de métricas Prometheus y estado resumido.

## Componentes principales

### `app/core/sessions.py`
- Gestiona sesiones en memoria (`SessionStore`, `SessionManager`).
- Aplica reglas de 20s/2min para agrupar interacciones.
- Produce `NoteCandidate` cuando se obtiene texto + ubicación válida.

### `app/services/note_builder.py`
- Convierte `NoteCandidate` en `NoteDraft` (texto + metadata).

### `app/services/osm_client.py`
- Cliente HTTP asíncrono (`httpx.AsyncClient`) hacia `/api/0.6/notes.json`.
- Parsea la respuesta JSON de OSM en `OSMNoteResponse`.

### `app/services/note_publisher.py`
- Orquesta construcción y publicación, con:
  - Reintentos configurables (`OSM_MAX_RETRIES`, `OSM_RETRY_BACKOFF_SECONDS`).
  - Métricas/telemetría (`metrics.increment(...)`).
  - Logging contextual (éxitos/reintentos/errores).

### `app/api/routes`
- `/api/v1/status`: Estado + métricas agregadas.
- `/api/v1/interactions`: Recibe interacciones desde adaptadores.
- `/api/v1/notes/anonymous`: Publicación directa de notas anónimas.
- `/metrics`: Exporta métricas Prometheus.

### `fakes/osm_api`
- Servicio FastAPI que simula la API de OSM con escenarios configurables:
  - `success` (respuesta válida)
  - `http_error` (HTTP status controlado)
  - `network_error` (simula fallo de conexión)
  - `invalid_response` (payload inválido)
- Se complementa con dos fakes:
  - **`FakeOSMClient`**: fixture en `tests/conftest.py`, trabaja en memoria y es ideal para pruebas unitarias rápidas.
  - **`fakes/osm_api`**: servidor HTTP emulado, útil para pruebas end-to-end/Docker.

## Métricas
- `terranote_note_publication_attempts_total`
- `terranote_note_publication_successes_total`
- `terranote_note_publication_http_errors_total`
- `terranote_note_publication_network_errors_total`
- `terranote_note_publication_invalid_responses_total`
- `terranote_note_publication_retries_total`

Se pueden visualizar con Prometheus (`docker/compose.prometheus.yml`).

## Pruebas
- Ejecutar `pytest` (véase README). Incluye pruebas unitarias, integración con fake in-memory y test de fake HTTP.

## Próximos pasos sugeridos
- Añadir documentación por carpeta (README locales).
- Incluir ejemplos de uso para adaptadores reales (WhatsApp/Telegram) en fases posteriores.

