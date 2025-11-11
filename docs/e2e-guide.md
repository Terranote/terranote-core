# Guía de pruebas end-to-end (fase 1)

0. Prerrequisitos:
   - Clonar `terranote-infra` y `terranote-tests` en el mismo directorio que `terranote-core`.
   - Desde `terranote-infra`, copiar el archivo `.env.example` a `.env` si deseas personalizar puertos o credenciales.
   - Desde `terranote-tests`, instala dependencias con `poetry install`.

1. Ejecutar el entorno base (desde `terranote-infra`):
   ```bash
   export COMPOSE_PROFILES=core,fakes,observability
   docker compose up --build
   ```
   Servicios expuestos:
   - `terranote-core`: `http://localhost:8000`
   - `fake-osm`: `http://localhost:8080`
   - `prometheus`: `http://localhost:9090`

2. Configurar el fake OSM según el escenario:
   ```bash
   curl -X POST http://localhost:8080/__control__/scenario \
     -H 'Content-Type: application/json' \
     -d '{"mode":"success"}'
   ```

3. Adaptador WhatsApp:
   - Enviar interacciones a `POST http://localhost:8000/api/v1/interactions`.
   - O para lotes offline: `POST http://localhost:8000/api/v1/interactions/batch`.
   - Exponer callback `POST http://localhost:<puerto-adaptador>/callbacks/note-created` y configurar `NOTIFIER_WHATSAPP_ENDPOINT` o usar `.env`.

4. Ejecutar pruebas automatizadas (desde `terranote-tests`):
   ```bash
   poetry run pytest -m e2e
   ```
   Marcadores disponibles:
   - `e2e`: flujos completos contra la infraestructura dockerizada.
   - `smoke`: validaciones ligeras para CI/CD.
   - `load`: escenarios de carga; requiere exportar variables adicionales descritas en el README de `terranote-tests`.

5. Verificar métricas/notificaciones:
   - `/api/v1/status` para estado y métricas.
   - `/metrics` para Prometheus.

6. Finalizar:
   ```bash
   docker compose down
   ```

