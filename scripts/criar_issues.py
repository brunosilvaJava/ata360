from __future__ import annotations

from pathlib import Path
from typing import Callable

from scripts.utils import read_yaml, stable_issue_id


def load_issues_file(path: str | Path) -> list[dict]:
    payload = read_yaml(path)
    issues = payload.get("issues", [])
    if not isinstance(issues, list):
        raise ValueError(f"Arquivo de issues inválido: {path}")
    return issues


def reconcile_issues(
    issues_file: str | Path,
    client_id: str,
    project_id: str,
    reunion_id: str,
    existing_issue_lookup: Callable[[str], bool] | None = None,
) -> list[dict]:
    issues = load_issues_file(issues_file)
    lookup = existing_issue_lookup or (lambda _identifier: False)
    created: list[dict] = []
    for issue in issues:
        payload = dict(issue)
        stable_id = stable_issue_id(client_id, project_id, reunion_id, str(payload.get("id", "unknown")))
        payload["stable_id"] = stable_id
        if lookup(stable_id):
            continue
        created.append(payload)
    return created


def update_manifesto_status(manifesto_path: str | Path, created_issues: list[dict]) -> dict:
    manifest = read_yaml(manifesto_path)
    issues_section = manifest.get("issues")
    if issues_section is None:
        issues_section = {}
        manifest["issues"] = issues_section
    if not isinstance(issues_section, dict):
        raise ValueError(f"Campo 'issues' inválido em {manifesto_path}")

    issues_section["criadas"] = [item["stable_id"] for item in created_issues]
    if created_issues:
        manifest["status"] = "issues-criadas"
    return manifest
