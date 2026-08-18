from __future__ import annotations

from pathlib import Path
import sys

from scripts.utils import normalize_repo_path

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def detect_transcricoes(repo_root: str | Path, explicit_file: str | Path | None = None, require_single: bool = False) -> list[str]:
    root = Path(repo_root)
    if explicit_file is not None:
        normalized = normalize_repo_path(explicit_file, root)
        if normalized.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Extensão inválida para transcrição: {normalized}")
        return [str(normalized)]

    candidate_dir = root / "clientes"
    if not candidate_dir.exists():
        return []

    matches = sorted(
        path for path in candidate_dir.glob("**/transcricoes/*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    relative_paths = [str(path.relative_to(root)) for path in matches]
    if require_single and len(relative_paths) > 1:
        raise ValueError("Múltiplos arquivos de transcrição encontrados; forneça um arquivo explícito.")
    return relative_paths


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    if len(sys.argv) > 1:
        result = detect_transcricoes(repo_root, sys.argv[1], require_single=True)
    else:
        result = detect_transcricoes(repo_root)
    for item in result:
        print(item)
