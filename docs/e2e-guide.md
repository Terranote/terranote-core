# Guía de pruebas end-to-end (fase 1)

1. Ejecutar el entorno base:
   ```bash
   docker compose -f docker/compose.prometheus.yml up --build
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

4. Verificar métricas/notificaciones:
   - `/api/v1/status` para estado y métricas.
   - `/metrics` para Prometheus.

5. Finalizar:
   ```bash
   docker compose -f docker/compose.prometheus.yml down
   ```

