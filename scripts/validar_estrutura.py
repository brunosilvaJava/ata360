from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.utils import ensure_required_fields, normalize_repo_path, read_front_matter, read_yaml
except ModuleNotFoundError:
    from utils import ensure_required_fields, normalize_repo_path, read_front_matter, read_yaml

CLIENT_REQUIRED_FIELDS = ["id", "nome", "sigla", "idioma_padrao", "fuso_horario", "estilo_ata", "ativo"]
PROJECT_REQUIRED_FIELDS = ["id", "cliente_id", "nome", "codigo", "status", "responsavel_interno", "estilo_ata", "labels_padrao"]
TRANSCRIPT_REQUIRED_FIELDS = ["cliente_id", "projeto_id", "reuniao_id", "titulo", "data", "tipo", "idioma", "participantes"]


def validate_client(client_path: str | Path, repo_root: str | Path) -> dict:
    path = normalize_repo_path(client_path, repo_root)
    if path.name != "cliente.yml":
        raise ValueError(f"Arquivo de cliente inválido: {path}")
    client_data = read_yaml(Path(repo_root) / path)
    ensure_required_fields(client_data, CLIENT_REQUIRED_FIELDS, str(path))
    if client_data["id"] != path.parent.name:
        raise ValueError(f"ID do cliente não bate com o caminho: {path}")
    return client_data


def validate_project(project_path: str | Path, repo_root: str | Path) -> dict:
    path = normalize_repo_path(project_path, repo_root)
    if path.name != "projeto.yml":
        raise ValueError(f"Arquivo de projeto inválido: {path}")
    project_data = read_yaml(Path(repo_root) / path)
    ensure_required_fields(project_data, PROJECT_REQUIRED_FIELDS, str(path))
    if project_data["id"] != path.parent.name:
        raise ValueError(f"ID do projeto não bate com o caminho: {path}")
    return project_data


def validate_transcript(transcript_path: str | Path, repo_root: str | Path) -> dict:
    path = normalize_repo_path(transcript_path, repo_root)
    if path.suffix.lower() not in {".md", ".txt"}:
        raise ValueError(f"Extensão de transcrição inválida: {path}")

    parts = path.parts
    if len(parts) < 6 or parts[0] != "clientes" or parts[2] != "projetos" or parts[4] != "transcricoes":
        raise ValueError(f"Caminho de transcrição fora do padrão esperado: {path}")

    client_id = parts[1]
    project_id = parts[3]
    client_file = Path("clientes") / client_id / "cliente.yml"
    project_file = Path("clientes") / client_id / "projetos" / project_id / "projeto.yml"

    if not (Path(repo_root) / client_file).exists():
        raise ValueError(f"Cliente não encontrado: {client_id}")
    if not (Path(repo_root) / project_file).exists():
        raise ValueError(f"Projeto não encontrado: {project_id}")

    client_data = validate_client(client_file, repo_root)
    project_data = validate_project(project_file, repo_root)
    if client_data["id"] != client_id:
        raise ValueError("Inconsistência entre cliente no path e no arquivo.")
    if project_data["cliente_id"] != client_id:
        raise ValueError("Projeto pertence a outro cliente.")
    if project_data["id"] != project_id:
        raise ValueError("Inconsistência entre projeto no path e no arquivo.")

    metadata, body = read_front_matter(Path(repo_root) / path)
    if not body:
        raise ValueError(f"Transcrição vazia: {path}")
    ensure_required_fields(metadata, TRANSCRIPT_REQUIRED_FIELDS, str(path))
    if metadata["cliente_id"] != client_id:
        raise ValueError("cliente_id no front matter não combina com o caminho.")
    if metadata["projeto_id"] != project_id:
        raise ValueError("projeto_id no front matter não combina com o caminho.")

    return {
        "cliente": client_data,
        "projeto": project_data,
        "metadata": metadata,
        "body": body,
        "path": str(path),
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python scripts/validar_estrutura.py <transcricao>")
    transcript_path = sys.argv[1]
    result = validate_transcript(transcript_path, repo_root)
    print(json.dumps({
        "path": result["path"],
        "cliente": result["cliente"]["id"],
        "projeto": result["projeto"]["id"],
        "reuniao": result["metadata"]["reuniao_id"],
        "titulo": result["metadata"]["titulo"],
        "status": "ok",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
