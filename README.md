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

## Pruebas

```bash
.venv/bin/pytest
```

## Docker

```bash
docker build -t terranote-core:dev .
docker run -p 8000:8000 terranote-core:dev
```
