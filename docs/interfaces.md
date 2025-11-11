# Contratos de Interacción y Notificaciones

## Interacción entrante (`POST /api/v1/interactions`)

- **Resumen**: Los adaptadores envían mensajes del usuario para agruparlos y crear notas.
- **Payload**:

```json
{
  "channel": "whatsapp",
  "user_id": "string",
  "sent_at": "2025-11-11T10:00:00Z",
  "payload": {
    "type": "text",
    "text": "Hay una vía cerrada por obras."
  }
}
```

```json
{
  "channel": "telegram",
  "user_id": "string",
  "sent_at": "2025-11-11T10:00:10Z",
  "payload": {
    "type": "location",
    "latitude": 4.611,
    "longitude": -74.082
  }
}
```

- **Respuestas**:
  - `accepted`: se requiere más información (`awaiting_text`, `awaiting_location`).
  - `note_created`: se creó la nota, incluye `note` con datos.
  - `discarded`: expiración o error (`missing_location_timeout`, `osm_api_error`, etc.).

## Notificación de nota creada (propuesta)

- **Uso**: Cuando el módulo central crea una nota, notifica al adaptador para que envíe el resultado al usuario.
- **Endpoint sugerido**: `POST /callbacks/note-created` (propio de cada adaptador).
- **URL configurable**: cada canal (WhatsApp, Telegram) puede tener su propio endpoint; se recomienda exponerlo mediante variables de entorno (`NOTIFIER_ENDPOINT_WHATSAPP`, etc.).
- **Payload**:

```json
{
  "channel": "whatsapp",
  "user_id": "string",
  "note_url": "https://www.openstreetmap.org/note/123456",
  "note_id": "123456",
  "latitude": 4.611,
  "longitude": -74.082,
  "text": "Hay una vía cerrada por obras.\n-- Terranote Core v1.0",
  "created_at": "2025-11-11T10:00:12Z"
}
```

- **Respuesta esperada**: `200 OK` o `202 Accepted`.
- **Reintentos**: el módulo central puede reintentar en caso de errores `5xx` o fallos de red; el adaptador debe tratar la operación como idempotente.
- **Reintentos**: El adaptador debería manejar idempotencia; el módulo central puede reintentar en caso de error temporal (en fases posteriores).

## Lote de interacciones (`POST /api/v1/interactions/batch`)

- **Uso**: enviar mensajes acumulados (offline) en una sola llamada.
- **Payload**: lista ordenada o desordenada de `InteractionRequest`; el módulo central los ordena por `sent_at`.
- **Respuesta**: lista de `InteractionResponse` correspondientes a cada interacción procesada.

