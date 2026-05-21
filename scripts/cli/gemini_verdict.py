from __future__ import annotations

import json
import os
import re
import subprocess
import sys


def extract_json_block(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)

    bare = re.search(r"(\{.*\})", text, re.DOTALL)
    if bare:
        return bare.group(1)

    raise ValueError("no JSON object found in model output")


def main() -> None:
    prompt = sys.stdin.read().strip()
    if not prompt:
        raise SystemExit("empty prompt")

    model = os.environ.get("GEMINI_VERDICT_MODEL", "gemini-2.5-flash")
    command = ["gemini", "-m", model, "-p", prompt]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=int(os.environ.get("CONTROL_TOWER_GEMINI_TIMEOUT_SEC", "120")),
    )
    raw = completed.stdout.strip()
    payload = json.loads(extract_json_block(raw))
    json.dump(payload, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
