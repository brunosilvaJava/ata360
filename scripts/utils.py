from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml

SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def read_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo YAML não encontrado: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Arquivo YAML inválido: {config_path}")
    return payload


def read_front_matter(path: str | Path) -> tuple[dict[str, Any], str]:
    transcript_path = Path(path)
    text = transcript_path.read_text(encoding="utf-8")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}, text

    delimiter = "\n---\n"
    if "\r\n" in text[:200]:
        delimiter = "\r\n---\r\n"

    parts = text.split(delimiter, 1)
    if len(parts) != 2:
        return {}, text

    front_matter = parts[0][4:]
    body = parts[1]
    metadata = yaml.safe_load(front_matter) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"Front matter inválido em {transcript_path}")
    return metadata, body.strip()


def normalize_repo_path(path: str | Path, repo_root: str | Path | None = None) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        raise ValueError(f"Caminho absoluto não é permitido: {path}")
    if ".." in candidate.parts:
        raise ValueError(f"Uso de '..' não é permitido em: {path}")
    if not candidate.name or candidate.name in {".", ".."}:
        raise ValueError(f"Nome de arquivo inválido: {path}")
    if any(char in candidate.name for char in ["\x00", "\n", "\r"]):
        raise ValueError(f"Nome de arquivo contém caracteres inválidos: {path}")
    if repo_root is not None:
        root = Path(repo_root).resolve()
        resolved = (root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Caminho fora do repositório: {path}") from exc
    return candidate


def make_slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text or "item"


def validate_identifier(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.match(value):
        raise ValueError(f"Campo '{field_name}' inválido: {value!r}")
    return value


def is_safe_filename(value: str) -> bool:
    return bool(value) and SAFE_NAME_RE.match(value) is not None


def stable_issue_id(client_id: str, project_id: str, reunion_id: str, issue_id: str) -> str:
    return f"ata360:{client_id}:{project_id}:{reunion_id}:{issue_id}"


def ensure_required_fields(payload: dict[str, Any], required: list[str], context: str) -> None:
    missing = [field for field in required if field not in payload or payload[field] in (None, "")]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes em {context}: {', '.join(missing)}")
