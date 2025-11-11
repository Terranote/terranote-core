# Proposed Structure for `terranote-docs`

## Purpose

> Source of truth for documentation shared across the Terranote ecosystem. This outline defines where global content should live and how it references per-repository guides (including `terranote-core`).

## Table of Contents (target)

1. **Introducción**
   - Misión y alcance de Terranote.
   - Glosario común.
   - Enlaces rápidos a repositorios principales.
2. **Arquitectura de Plataforma**
   - Diagrama general del ecosistema.
   - Descripción de módulos (`core`, adaptadores, infraestructura, observabilidad).
   - Enlace a `docs/overview.md` de `terranote-core` para detalles internos.
3. **Guía de Onboarding**
   - Requisitos de entorno y herramientas globales.
   - Checklist de primeros pasos (clonado de repos, setup de cuentas externas).
   - Enlaces a guías operativas locales:
     - `terranote-core/docs/e2e-guide.md`
     - `terranote-infra/README.md`
     - `terranote-tests/README.md`
4. **Operación y Runbooks**
   - Procedimientos para despliegue (desarrollo, staging, producción).
   - Runbooks de incidentes comunes.
   - Matriz de responsables (SRE, equipo de adaptadores, core).
5. **Estándares y Buenas Prácticas**
   - Guías de estilo de código, revisión y testing compartidas.
   - Políticas de seguridad y manejo de secretos.
   - Definición de ramas y versionado.
6. **Referencias por Componente**
   - Sub-sección por repositorio con resumen y links:
     - `terranote-core` → enlazar `README.md`, `docs/interfaces.md`, `docs/e2e-guide.md`.
     - `terranote-infra` → perfiles `docker-compose`, configuración `.env`.
     - `terranote-tests` → marcadores pytest, escenarios de carga.
     - Adaptadores oficiales (WhatsApp, Telegram, etc.).
7. **Anexos**
   - Plantillas (ej. PR, incident reports).
   - Historial de arquitectura, decisiones (ADR) globales.
   - Preguntas frecuentes.

## Ownership & Maintenance

- **Product Owner**: Responsable de validar la vigencia del contenido y priorizar cambios.
- **Equipo Core**: Mantiene secciones relacionadas con `terranote-core`, provee enlaces actualizados.
- **Equipo Infra/SRE**: Actualiza runbooks, despliegues, observabilidad.
- **Equipo QA/Tests**: Custodia referencias a `terranote-tests` y guías de validación.

Se propone un ciclo de revisión trimestral coordinado por el Product Owner, con checklists para cada equipo.

## Cross-Linking Conventions

- Los documentos globales en `terranote-docs` deben enlazar a las guías locales usando rutas absolutas de GitHub (e.g., `https://github.com/Terranote/terranote-core/blob/main/docs/e2e-guide.md`).
- En los repositorios locales, incluir una nota “Para contexto global, ver…” apuntando a la sección correspondiente en `terranote-docs`.
- Evitar duplicidad: cualquier contenido que aplique a más de un repositorio debe residir en `terranote-docs`; los repos locales solo ofrecen resúmenes y enlaces.


