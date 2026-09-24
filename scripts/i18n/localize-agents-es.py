#!/usr/bin/env python3
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAP_FILE = os.path.join(REPO_ROOT, "scripts", "i18n", "agent-names-es.json")
ANTIGRAVITY_SKILLS_DIR = os.path.expanduser("~/.gemini/config/skills")

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def localize_content(content, name, name_es, desc_es, vibe_es, is_antigravity_skill=False):
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Localize frontmatter description and vibe
    # Preserve name: exactly to not break slugs and tool discovery
    new_fm_lines = []
    has_desc = False
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            # Escape quotes in description
            escaped_desc = desc_es.replace('"', '\\"')
            new_fm_lines.append(f'description: "{escaped_desc}"')
            has_desc = True
        elif line.startswith("vibe:") and vibe_es:
            escaped_vibe = vibe_es.replace('"', '\\"')
            new_fm_lines.append(f'vibe: "{escaped_vibe}"')
        else:
            new_fm_lines.append(line)
            
    if not has_desc and desc_es:
        escaped_desc = desc_es.replace('"', '\\"')
        new_fm_lines.append(f'description: "{escaped_desc}"')
        
    new_frontmatter = "\n".join(new_fm_lines)
    
    # Body localization
    # Check if already localized with language directive
    if "Idioma de Interacción" not in body:
        lang_directive = (
            "\n> **Idioma de Interacción / Language**:\n"
            "> Este agente interactúa, razona y responde preferentemente en **español** por defecto.\n"
            "> Conserva términos técnicos, código, comandos y nombres de API en su forma estándar en inglés.\n"
        )
        # Place language directive after the first heading or intro
        first_h1 = re.search(r"^# .+", body, flags=re.MULTILINE)
        if first_h1:
            h1_pos = first_h1.end()
            body = body[:h1_pos] + "\n" + lang_directive + body[h1_pos:]
        else:
            body = lang_directive + "\n" + body

    # Header replacements preserving English keywords for linting and tool mapping
    header_replacements = [
        (r"^# (.+) Agent Personality", f"# Personalidad del Agente {name_es} (\\1 Agent Personality)"),
        (r"^## 🧠 Your Identity & Memory", "## 🧠 Identidad y Memoria (Your Identity & Memory)"),
        (r"^## 🎯 Your Core Mission", "## 🎯 Misión Principal (Your Core Mission)"),
        (r"^## 🚨 Critical Rules You Must Follow", "## 🚨 Reglas Críticas (Critical Rules You Must Follow)"),
        (r"^## 📋 Your Technical Deliverables", "## 📋 Entregables Técnicos (Your Technical Deliverables)"),
        (r"^## 🔄 Your Workflow Process", "## 🔄 Proceso y Flujo de Trabajo (Your Workflow Process)"),
        (r"^## 💭 Your Communication Style", "## 💭 Estilo de Comunicación (Your Communication Style)"),
        (r"^## 🔄 Learning & Memory", "## 🔄 Aprendizaje y Memoria (Learning & Memory)"),
        (r"^## 🎯 Your Success Metrics", "## 🎯 Métricas de Éxito (Your Success Metrics)"),
        (r"^## 🚀 Advanced Capabilities", "## 🚀 Capacidades Avanzadas (Advanced Capabilities)"),
    ]
    
    for pattern, repl in header_replacements:
        body = re.sub(pattern, repl, body, flags=re.MULTILINE)

    # Standard intro replacement
    body = re.sub(
        r"^You are \*\*" + re.escape(name) + r"\*\*",
        f"Eres **{name}** ({name_es})",
        body,
        flags=re.MULTILINE
    )

    # Standard bullet points
    body = re.sub(r"^- \*\*Role\*\*:", "- **Rol (Role)**:", body, flags=re.MULTILINE)
    body = re.sub(r"^- \*\*Personality\*\*:", "- **Personalidad (Personality)**:", body, flags=re.MULTILINE)
    body = re.sub(r"^- \*\*Memory\*\*:", "- **Memoria (Memory)**:", body, flags=re.MULTILINE)
    body = re.sub(r"^- \*\*Experience\*\*:", "- **Experiencia (Experience)**:", body, flags=re.MULTILINE)
    
    return f"---{new_frontmatter}\n---{body}"

def main():
    if not os.path.exists(MAP_FILE):
        print(f"Error: {MAP_FILE} not found. Run generate_es_map.py first.")
        sys.exit(1)

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        es_map = json.load(f)

    print(f"Loaded {len(es_map)} agent translations from {MAP_FILE}")

    # 1. Update repo source files
    updated_sources = 0
    for name, item in es_map.items():
        rel_file = item.get("file")
        if not rel_file:
            continue
        full_path = os.path.join(REPO_ROOT, rel_file)
        if not os.path.exists(full_path):
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        localized = localize_content(
            content,
            name=name,
            name_es=item.get("name_es", name),
            desc_es=item.get("description_es", item.get("description", "")),
            vibe_es=item.get("vibe_es", item.get("vibe", ""))
        )

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(localized)
        updated_sources += 1

    print(f"[OK] Localized {updated_sources} source agent files in {REPO_ROOT}")

    # 2. Update Antigravity installed skills
    updated_skills = 0
    if os.path.exists(ANTIGRAVITY_SKILLS_DIR):
        for name, item in es_map.items():
            slug = "agency-" + slugify(name)
            skill_file = os.path.join(ANTIGRAVITY_SKILLS_DIR, slug, "SKILL.md")
            if not os.path.exists(skill_file):
                continue

            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()

            localized = localize_content(
                content,
                name=name,
                name_es=item.get("name_es", name),
                desc_es=item.get("description_es", item.get("description", "")),
                vibe_es=item.get("vibe_es", item.get("vibe", "")),
                is_antigravity_skill=True
            )

            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(localized)
            updated_skills += 1

        print(f"[OK] Localized {updated_skills} installed skills in {ANTIGRAVITY_SKILLS_DIR}")

if __name__ == "__main__":
    main()
