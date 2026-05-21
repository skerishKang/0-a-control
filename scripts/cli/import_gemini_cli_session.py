from __future__ import annotations

try:
    from scripts.cli.import_agent_transcript import main
except ModuleNotFoundError:
    from import_agent_transcript import main


if __name__ == "__main__":
    main(default_source_name="gemini-cli")
