# ⚠️ TODO: Implementar Endpoint de Ayuda en Terranote Core

## 📋 Resumen

El adaptador de WhatsApp **ya está implementado** y espera que el core proporcione información de ayuda dinámica a través de un endpoint específico.

**Estado actual:** El adaptador tiene un fallback local, pero funcionará mejor cuando el core implemente este endpoint.

## 🎯 Endpoint Requerido

```
GET /api/v1/channels/{channel}/help?lang={lang}
```

### Ejemplo
```
GET /api/v1/channels/whatsapp/help?lang=es
GET /api/v1/channels/whatsapp/help?lang=en
```

## 📄 Especificación Completa

Ver: [`docs/core-help-endpoint.md`](./core-help-endpoint.md)

## 🔗 Referencias

- **Repositorio del adaptador:** https://github.com/Terranote/terranote-adapter-whatsapp
- **Archivo de especificación:** `docs/core-help-endpoint.md` en este repositorio
- **Código del adaptador que usa este endpoint:** `src/terranote_adapter_whatsapp/clients/core.py` (método `get_help`)
- **Lógica de uso:** `src/terranote_adapter_whatsapp/routes/webhook.py` (línea ~90)

## ✅ Qué Hacer

1. **Implementar el endpoint** en `terranote-core`:
   - Ruta: `GET /api/v1/channels/{channel}/help`
   - Parámetro query: `lang` (es, en, etc.)
   - Respuesta: JSON con `body` y `quick_replies` opcional

2. **Incluir información dinámica** sobre:
   - Funcionalidades disponibles (texto, ubicación, fotos, videos, etc.)
   - Comandos específicos del canal
   - Ejemplos de uso

3. **Soporte multiidioma**:
   - Al menos español (`es`) e inglés (`en`)
   - Extensible a otros idiomas

## 🧪 Testing

Una vez implementado, probar con:

```bash
# Español
curl "http://localhost:3002/api/v1/channels/whatsapp/help?lang=es"

# Inglés
curl "http://localhost:3002/api/v1/channels/whatsapp/help?lang=en"
```

## 📝 Notas

- El adaptador tiene un **fallback local** si el endpoint no está disponible
- El adaptador consulta el core **cada vez** que se solicita ayuda, así que los cambios se reflejan inmediatamente
- Ver la especificación completa en `docs/core-help-endpoint.md` para detalles de formato, códigos de estado, etc.

