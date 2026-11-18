"""Sync the local Antigravity model catalog into OpenCode 2.x (stdlib only)."""

import argparse
import copy
import datetime
import json
import os
from pathlib import Path
import urllib.error
import urllib.request


PROVIDER = "antigravity-tools"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_config(original, proxy, catalog):
    config = copy.deepcopy(original)
    models = {}
    for item in catalog["data"]:
        model_id = item["id"]
        # Image generators and internal aliases are not coding chat models.
        if "image" in model_id or model_id.startswith("internal-"):
            continue
        capabilities = {
            "tools": True,
            "input": ["text", "image"] if item.get("supports_images") else ["text"],
            "output": ["text"],
            "reasoning": {"supported": bool(item.get("supports_thinking"))},
        }
        model = {"name": item.get("display_name", model_id), "capabilities": capabilities}
        limits = {key: item[source] for key, source in (
            ("context", "context_length"), ("output", "max_output_tokens")
        ) if isinstance(item.get(source), int) and item[source] > 0}
        if limits:
            model["limit"] = limits
        models[model_id] = model
    if not models:
        raise ValueError("Proxy returned no chat models; configuration was not changed.")
    legacy = config.get("provider", {})
    legacy.pop(PROVIDER, None)
    if "provider" in config and not legacy:
        del config["provider"]
    config.setdefault("providers", {})[PROVIDER] = {
        "name": "Antigravity Tools Proxy",
        "package": "@opencode/ai/providers/openai-compatible",
        "settings": {
            "baseURL": "http://127.0.0.1:{}/v1".format(proxy["port"]),
            "apiKey": proxy["api_key"],
        },
        "models": models,
    }
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Back up and update the global config")
    args = parser.parse_args()
    user_dir = Path.home()
    config_root = Path(os.environ.get("XDG_CONFIG_HOME", str(user_dir / ".config")))
    target = config_root / "opencode" / "opencode.json"
    if target.with_suffix(".jsonc").exists():
        raise ValueError("An opencode.jsonc also exists; review precedence before applying.")
    source = target.read_bytes()
    original = json.loads(source.decode("utf-8-sig"))
    proxy = read_json(user_dir / ".antigravity_tools" / "gui_config.json")["proxy"]
    request = urllib.request.Request(
        "http://127.0.0.1:{}/v1/models".format(proxy["port"]),
        headers={"Authorization": "Bearer " + proxy["api_key"]},
    )
    # Local credentials must never pass through an environment-configured proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=20) as response:
        catalog = json.load(response)
    updated = build_config(original, proxy, catalog)
    models = updated["providers"][PROVIDER]["models"]
    print("Target:", target)
    print("Chat models:", len(models))
    for model_id in models:
        print("  " + PROVIDER + "/" + model_id)
    print("Default model preserved:", updated.get("model", "(automatic)"))
    if not args.apply:
        print("Preview only. Run with --apply to back up and write the configuration.")
        return
    if target.read_bytes() != source:
        raise ValueError("Configuration changed during discovery; rerun to preserve the latest edits.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = target.with_name(target.name + ".antigravity-" + stamp + ".bak")
    with backup.open("xb") as file:
        file.write(source)
    payload = (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    target.write_bytes(payload)
    if read_json(target) != updated:
        raise RuntimeError("Read-back verification failed. Original config is in " + str(backup))
    print("Updated and read-back verified. Backup:", backup)
    print("Restart OpenCode, then select an antigravity-tools model using /models.")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        raise SystemExit("Proxy HTTP error {}. Configuration was not updated.".format(error.code))
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit("Update failed ({}): {}".format(type(error).__name__, error))
