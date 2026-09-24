#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.parse
import urllib.request

MAP_FILE = "scripts/i18n/agent-names-es.json"
EXTRACTED_FILE = "scripts/i18n/extracted_agents.json"

def translate_text(text, retries=3):
    if not text or not text.strip():
        return ""
    text = text.strip()
    # Cache lookup / direct translation
    url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(text) + "&langpair=en|es&de=agencylocalize@gmail.com"
    req = urllib.request.Request(url, headers={"User-Agent": "AgencyLocalizer/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                res = data.get("responseData", {}).get("translatedText", "")
                if res and "MYMEMORY WARNING" not in res.upper():
                    return res
                if "MYMEMORY WARNING" in res.upper():
                    time.sleep(2)
        except Exception as e:
            time.sleep(1 + attempt)
    return text  # fallback to original if failed

def main():
    if not os.path.exists(EXTRACTED_FILE):
        print(f"Error: {EXTRACTED_FILE} not found.")
        sys.exit(1)

    with open(EXTRACTED_FILE, "r", encoding="utf-8") as f:
        extracted = json.load(f)

    es_map = {}
    if os.path.exists(MAP_FILE):
        try:
            with open(MAP_FILE, "r", encoding="utf-8") as f:
                es_map = json.load(f)
        except Exception:
            es_map = {}

    total = len(extracted)
    print(f"Total agents to translate: {total}. Already cached: {len(es_map)}")

    count = 0
    for name, item in extracted.items():
        count += 1
        if name in es_map and es_map[name].get("description_es"):
            continue

        desc = item.get("description", "")
        vibe = item.get("vibe", "")

        print(f"[{count}/{total}] Translating {name}...")
        name_es = translate_text(name)
        desc_es = translate_text(desc)
        vibe_es = translate_text(vibe) if vibe else ""

        es_map[name] = {
            "name": name,
            "name_es": name_es,
            "description": desc,
            "description_es": desc_es,
            "vibe": vibe,
            "vibe_es": vibe_es,
            "file": item.get("file", ""),
            "division": item.get("division", "")
        }

        # Save progress every 5 agents
        if count % 5 == 0:
            with open(MAP_FILE, "w", encoding="utf-8") as f:
                json.dump(es_map, f, indent=2, ensure_ascii=False)
        time.sleep(0.3)

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(es_map, f, indent=2, ensure_ascii=False)

    print(f"Finished! {len(es_map)} agents saved to {MAP_FILE}")

if __name__ == "__main__":
    main()
