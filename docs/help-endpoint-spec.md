# Especificación del Endpoint de Ayuda para Terranote Core

Este documento describe el endpoint que el adaptador de WhatsApp espera que `terranote-core` implemente para proporcionar información de ayuda dinámica.

## Endpoint

```
GET /api/v1/channels/{channel}/help
```

### Parámetros

- **Path parameter:**
  - `channel`: Canal del adaptador (ej: `"whatsapp"`, `"telegram"`)

- **Query parameter:**
  - `lang`: Idioma solicitado (ej: `"es"`, `"en"`) - opcional, por defecto `"es"`

### Ejemplo de Request

```bash
GET /api/v1/channels/whatsapp/help?lang=es
GET /api/v1/channels/whatsapp/help?lang=en
```

## Respuesta Esperada

### Formato JSON

```json
{
  "body": "📝 *Terranote - Comandos disponibles:*\n\n...",
  "quick_replies": [
    {"id": "cmd_crear", "title": "Crear nota"},
    {"id": "cmd_info", "title": "Más info"}
  ]
}
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `body` | `string` | ✅ Sí | Texto del mensaje de ayuda. Puede incluir Markdown de WhatsApp (negrita con `*texto*`, cursiva con `_texto_`, etc.) |
| `quick_replies` | `array` | ❌ No | Array de botones de respuesta rápida. Máximo 3 botones. Cada botón tiene `id` y `title` |

### Estructura de Quick Replies

Cada elemento en `quick_replies` debe tener:

```json
{
  "id": "cmd_crear",      // Identificador único del comando (sin espacios, sin caracteres especiales)
  "title": "Crear nota"   // Texto visible del botón (máximo 20 caracteres)
}
```

## Ejemplos de Respuesta

### Ejemplo 1: Ayuda básica sin botones

```json
{
  "body": "📝 *Terranote - Comandos disponibles:*\n\n• Envía un *mensaje de texto* seguido de tu *ubicación* para crear una nota\n• `/ayuda` - Mostrar esta ayuda\n• `/info` - Información sobre Terranote"
}
```

### Ejemplo 2: Ayuda con botones

```json
{
  "body": "📝 *Terranote - Comandos disponibles:*\n\n• Envía un *mensaje de texto* seguido de tu *ubicación* para crear una nota\n• También puedes enviar *fotos* o *videos* con tu ubicación\n• `/ayuda` - Mostrar esta ayuda\n• `/info` - Información sobre Terranote",
  "quick_replies": [
    {"id": "cmd_crear", "title": "Crear nota"},
    {"id": "cmd_info", "title": "Más info"}
  ]
}
```

### Ejemplo 3: Ayuda en inglés

```json
{
  "body": "📝 *Terranote - Available commands:*\n\n• Send a *text message* followed by your *location* to create a note\n• You can also send *photos* or *videos* with your location\n• `/help` - Show this help\n• `/info` - Information about Terranote",
  "quick_replies": [
    {"id": "cmd_create", "title": "Create note"},
    {"id": "cmd_info", "title": "More info"}
  ]
}
```

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200 OK` | Respuesta exitosa con información de ayuda |
| `404 Not Found` | Canal no encontrado o no soportado |
| `500 Internal Server Error` | Error del servidor |

## Comportamiento del Adaptador

1. **Si el endpoint responde `200 OK`:**
   - El adaptador usa el `body` y `quick_replies` del core
   - Envía el mensaje al usuario con los botones si están disponibles

2. **Si el endpoint falla o no está disponible:**
   - El adaptador usa un mensaje de ayuda local como fallback
   - Registra el error en los logs pero continúa funcionando

3. **Si `quick_replies` está vacío o no está presente:**
   - El adaptador envía solo el texto sin botones

## Consideraciones para la Implementación

### Idiomas Soportados

El core debe soportar al menos:
- `es` (Español) - por defecto
- `en` (Inglés)

Puede extenderse a otros idiomas según necesidad.

### Contenido Dinámico

El core puede incluir en el mensaje de ayuda información sobre:
- Funcionalidades disponibles (texto, ubicación, fotos, videos, etc.)
- Comandos específicos del canal
- Ejemplos de uso
- Información sobre límites o restricciones

### Actualización en Tiempo Real

Como el adaptador consulta el core cada vez que se solicita ayuda, cualquier cambio en el core se reflejará inmediatamente sin necesidad de reiniciar el adaptador.

## Ejemplo de Implementación (Pseudocódigo)

```python
@router.get("/api/v1/channels/{channel}/help")
async def get_channel_help(channel: str, lang: str = "es"):
    # Validar que el canal sea soportado
    if channel not in ["whatsapp", "telegram"]:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Obtener información de ayuda según el idioma
    help_info = get_help_for_channel(channel, lang)
    
    # Construir respuesta
    return {
        "body": help_info["message"],
        "quick_replies": help_info.get("buttons", [])
    }
```

## Testing

Para probar el endpoint:

```bash
# Español
curl "http://localhost:3002/api/v1/channels/whatsapp/help?lang=es"

# Inglés
curl "http://localhost:3002/api/v1/channels/whatsapp/help?lang=en"
```

## Notas Adicionales

- El adaptador detecta automáticamente el idioma del mensaje del usuario, pero siempre puedes forzar un idioma específico
- Los `id` de los `quick_replies` deben ser únicos y seguir el formato `cmd_{nombre}`
- Los `title` de los botones tienen un límite de 20 caracteres en WhatsApp
- El `body` puede tener hasta 4096 caracteres en WhatsApp

