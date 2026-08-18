from __future__ import annotations

from pathlib import Path

from scripts.gerar_ata import generate_ata, main


def processar_reuniao(transcript_path: str | Path, repo_root: str | Path) -> dict:
    return generate_ata(transcript_path, repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
