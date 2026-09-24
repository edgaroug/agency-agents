# 🇪🇸 Localización a Español (es)

Este módulo localiza los agentes y las skills de **The Agency** a español sin romper la compatibilidad de código, scripts de conversión, linters ni herramientas (como Antigravity).

## Archivos

| Archivo | Descripción |
|---|---|
| `agent-names-es.json` | Mapeo de los 279 agentes con su nombre en español, descripción traducida y vibe |
| `localize-agents-es.py` | Script en Python que aplica la localización tanto a los archivos fuente como a las skills de Antigravity |
| `generate_es_map.py` | Script que extrajo y tradujo las descripciones y metadatos de los 279 agentes |

## Cómo funciona la compatibilidad

Para no afectar la funcionalidad del repositorio:
1. **Identificadores y Slugs**: El campo `name` en el frontmatter YAML y los nombres de las carpetas/archivos conservan sus identificadores en inglés (ej. `Frontend Developer` -> `agency-frontend-developer`). Esto evita romper los comandos de instalación, scripts de detección y referencias cruzadas.
2. **Descripciones traducidas**: El campo `description` en el frontmatter YAML se traduce al español para que los modelos LLM (incluido Antigravity) reconozcan y activen la skill adecuada cuando el usuario solicite tareas en español.
3. **Encabezados bilingües**: Las secciones clave utilizan encabezados bilingües (ej. `## 🧠 Identidad y Memoria (Your Identity & Memory)`), permitiendo que scripts de validación como `lint-agents.sh` y generadores como `convert.sh` pasen todas las pruebas con 0 errores.
4. **Directiva de lenguaje de interacción**: Se inyecta una directiva para que el agente piense y responda prioritariamente en español, conservando la terminología técnica estándar en inglés.

## Uso

Para re-aplicar o actualizar la localización en cualquier momento:

```bash
python3 scripts/i18n/localize-agents-es.py
```

Luego regenerar e instalar las skills:

```bash
./scripts/convert.sh --tool antigravity
./scripts/install.sh --tool antigravity
```
