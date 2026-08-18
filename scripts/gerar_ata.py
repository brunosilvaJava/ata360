from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.validar_estrutura import validate_transcript
except ModuleNotFoundError:  # pragma: no cover
    from validar_estrutura import validate_transcript


SPEAKER_RE = re.compile(r"^\[(?P<time>[^\]]+)\]\s*(?P<speaker>[^:]+):\s*(?P<text>.+?)\s*$")
DECISION_TOKENS = ("decid", "decisão", "definiu", "defin", "concord", "aprov", "será", "ficará", "fica", "confirm", "validar", "revisar")
TASK_TOKENS = ("vai", "irá", "envi", "entreg", "revis", "valid", "confirm", "atualiz", "discut", "agendar", "criar", "desenvolv", "apresent", "analis", "prepar")
PENDENCY_TOKENS = ("pendente", "pendência", "falt", "ainda", "aguard", "resta", "espera", "pendentes")
RISK_TOKENS = ("risco", "problem", "imped", "bloqueio", "dificuld", "dependência", "atras", "incerteza")
CONFIRMATION_TOKENS = ("confirm", "confirma", "concord", "ok", "ciente", "aceito", "aprovado", "validado")


def contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def iterate_speech_lines(body: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw_line in body.splitlines():
        text = raw_line.strip()
        if not text:
            continue
        match = SPEAKER_RE.match(text)
        if match:
            entries.append({
                "speaker": match.group("speaker").strip(),
                "text": match.group("text").strip(),
            })
        else:
            entries.append({"speaker": "", "text": text})
    return entries


def build_executive_summary(entries: list[dict[str, str]], max_sentences: int = 3) -> str:
    sentences: list[str] = []
    for entry in entries:
        text = entry["text"].rstrip(".")
        if not text:
            continue
        if text.lower().startswith("vamos ") or text.lower().startswith("podemos "):
            continue
        sentences.append(text)
        if len(sentences) >= max_sentences:
            break
    summary = " ".join(sentences)
    return summary.rstrip(". ") if summary else "Resumo não disponível na transcrição."


def build_topics(entries: list[dict[str, str]]) -> list[str]:
    topics: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        text = entry["text"].strip()
        if not text:
            continue
        if text.lower() in {"resumo", "objetivo"}:
            continue
        if text not in seen:
            topics.append(f"- {text}")
            seen.add(text)
    return topics or ["- Nenhum tópico explicitamente identificado na transcrição."]


def extract_decisions(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    decisions: list[dict[str, str]] = []
    for index, entry in enumerate(entries, start=1):
        text = entry["text"]
        if not text:
            continue
        if contains_any(text, DECISION_TOKENS) and not contains_any(text, PENDENCY_TOKENS):
            evidence = entry["speaker"] and f"{entry['speaker']}: {text}" or text
            decisions.append({
                "id": f"D{index}",
                "texto": text,
                "confianca": "alta",
                "evidencia": evidence,
            })
    return decisions


def extract_tasks(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    for index, entry in enumerate(entries, start=1):
        text = entry["text"]
        if not text:
            continue
        if contains_any(text, TASK_TOKENS):
            responsible = entry["speaker"] if entry["speaker"] else "não informado"
            prazo = "não informado"
            match = re.search(r"(at[eé]|até|na próxima|próxima|sexta-feira|segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta|amanhã)", text, re.IGNORECASE)
            if match:
                prazo = match.group(0).strip()
            tasks.append({
                "id": f"T{index}",
                "texto": text,
                "responsavel": responsible,
                "prazo": prazo,
                "confianca": "alta",
                "evidencia": f"{responsible}: {text}",
            })
    return tasks


def extract_pendencies(entries: list[dict[str, str]]) -> list[str]:
    pendencies: list[str] = []
    for entry in entries:
        text = entry["text"]
        if contains_any(text, PENDENCY_TOKENS):
            pendencies.append(f"- {text}")
    return pendencies


def extract_risks(entries: list[dict[str, str]]) -> list[str]:
    risks: list[str] = []
    for entry in entries:
        text = entry["text"]
        if contains_any(text, RISK_TOKENS):
            risks.append(f"- {text}")
    return risks


def extract_confirmations(entries: list[dict[str, str]]) -> list[str]:
    confirmations: list[str] = []
    for entry in entries:
        text = entry["text"]
        if contains_any(text, CONFIRMATION_TOKENS):
            confirmations.append(f"- {text}")
    return confirmations


def render_markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    if not rows:
        return "Nenhuma informação explicitamente registrada na transcrição."
    column_map = {
        "ID": "id",
        "Decisão": "texto",
        "Tarefa": "texto",
        "Responsável": "responsavel",
        "Prazo": "prazo",
        "Confiança": "confianca",
        "Evidência": "evidencia",
    }
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"
    body: list[str] = [header, separator]
    for row in rows:
        values = [str(row.get(column_map.get(column, column.lower()), "-")) for column in columns]
        body.append("| " + " | ".join(values) + " |")
    return "\n".join(body)


def render_decisions(decisions: list[dict[str, str]]) -> str:
    if not decisions:
        return "| - | Nenhuma decisão explicitamente registrada na transcrição. | - | - |"
    table = render_markdown_table(decisions, ["ID", "Decisão", "Confiança", "Evidência"])
    return "\n".join(table.splitlines()[2:])


def render_tasks(tasks: list[dict[str, str]]) -> str:
    if not tasks:
        return "| - | Nenhuma tarefa explicitamente registrada na transcrição. | - | - | - | - |"
    table = render_markdown_table(tasks, ["ID", "Tarefa", "Responsável", "Prazo", "Confiança", "Evidência"])
    return "\n".join(table.splitlines()[2:])


def render_custom_list(items: list[str], fallback: str | None = None) -> str:
    if not items:
        return fallback or "- Nenhuma informação explicitamente registrada na transcrição."
    return "\n".join(items)


def stringify_value(value: Any) -> str:
    if value is None:
        return "não informado"
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def extract_meeting_facts(body: str) -> dict[str, Any]:
    entries = iterate_speech_lines(body)
    return {
        "summary": build_executive_summary(entries),
        "topics": build_topics(entries),
        "decisions": extract_decisions(entries),
        "tasks": extract_tasks(entries),
        "pendencies": extract_pendencies(entries),
        "risks": extract_risks(entries),
        "confirmations": extract_confirmations(entries),
    }


def build_ata_content(validation: dict[str, Any], facts: dict[str, Any] | None = None) -> str:
    metadata = validation["metadata"]
    client_data = validation["cliente"]
    project_data = validation["projeto"]
    facts = facts or extract_meeting_facts(validation["body"])

    template = Path(__file__).resolve().parent.parent / "templates" / "ata-padrao.md"
    content = template.read_text(encoding="utf-8")
    replacements = {
        "{{ cliente }}": stringify_value(client_data.get("nome", client_data.get("id", "Cliente"))),
        "{{ projeto }}": stringify_value(project_data.get("nome", project_data.get("id", "Projeto"))),
        "{{ reuniao }}": stringify_value(metadata.get("reuniao_id", "reuniao")),
        "{{ data }}": stringify_value(metadata.get("data", "não informada")),
        "{{ tipo }}": stringify_value(metadata.get("tipo", "não informado")),
        "{{ idioma }}": stringify_value(metadata.get("idioma", "não informado")),
        "{{ participantes }}": ", ".join(metadata.get("participantes", [])) if isinstance(metadata.get("participantes"), list) else stringify_value(metadata.get("participantes", "não informado")),
        "{{ objetivo }}": stringify_value(metadata.get("titulo", "Reunião")),
        "{{ resumo_executivo }}": facts["summary"],
        "{{ topicos_discutidos }}": render_custom_list(facts["topics"]),
        "{{ decisoes }}": render_decisions(facts["decisions"]),
        "{{ tarefas }}": render_tasks(facts["tasks"]),
        "{{ riscos }}": render_custom_list(facts["risks"], "- Nenhum risco explicitamente descrito na transcrição."),
        "{{ confirmacoes }}": render_custom_list(facts["confirmations"], "- Nenhuma confirmação explicitamente registrada na transcrição."),
        "{{ observacoes }}": "Sem observações adicionais explicitamente mencionadas na transcrição.",
    }
    for key, value in replacements.items():
        content = content.replace(key, value)
    return content


def build_manifest(
    validation: dict[str, Any],
    ata_path: Path,
    manifest_path: Path,
    repo_root: str | Path,
    decisions: list[dict[str, str]] | None = None,
    tasks: list[dict[str, str]] | None = None,
    risks: list[str] | None = None,
    confirmations: list[str] | None = None,
) -> dict[str, Any]:
    metadata = validation["metadata"]
    client_data = validation["cliente"]
    project_data = validation["projeto"]
    root = Path(repo_root).resolve()
    issue_path = manifest_path.parent / f"{manifest_path.stem}.issues.yml"
    manifest = {
        "versao_schema": "1.0",
        "cliente": {
            "id": client_data.get("id"),
            "nome": client_data.get("nome"),
        },
        "projeto": {
            "id": project_data.get("id"),
            "nome": project_data.get("nome"),
        },
        "reuniao": {
            "id": metadata.get("reuniao_id"),
            "titulo": metadata.get("titulo"),
            "data": metadata.get("data"),
            "tipo": metadata.get("tipo"),
        },
        "arquivos": {
            "transcricao": validation["path"],
            "ata": str(ata_path.relative_to(root)),
            "issues": str(issue_path.relative_to(root)),
        },
        "status": "aguardando-validacao",
        "agente": {
            "nome": "secretario-executivo",
            "versao": "0.1.0",
        },
        "resultado": {
            "decisoes": len(decisions or []),
            "tarefas": len(tasks or []),
            "riscos": len(risks or []),
            "esclarecimentos": len(confirmations or []),
            "confianca_geral": "alta",
        },
        "pull_request": {
            "numero": None,
            "status": "aguardando-validacao",
        },
        "issues": {
            "criadas": [],
        },
    }
    return manifest


def generate_ata(transcript_path: str | Path, repo_root: str | Path) -> dict[str, Path | str | dict[str, Any]]:
    validation = validate_transcript(transcript_path, repo_root)
    repo = Path(repo_root).resolve()
    transcript_rel = Path(validation["path"])
    project_dir = repo / transcript_rel.parents[1]
    ata_dir = project_dir / "atas"
    processing_dir = project_dir / "processamento"
    ata_dir.mkdir(parents=True, exist_ok=True)
    processing_dir.mkdir(parents=True, exist_ok=True)

    meeting_id = validation["metadata"]["reuniao_id"]
    ata_path = ata_dir / f"{meeting_id}.md"
    manifesto_path = processing_dir / f"{meeting_id}.yml"

    facts = extract_meeting_facts(validation["body"])
    ata_content = build_ata_content(validation, facts)
    ata_path.write_text(ata_content + "\n", encoding="utf-8")

    manifest = build_manifest(
        validation,
        ata_path,
        manifesto_path,
        repo,
        facts["decisions"],
        facts["tasks"],
        facts["risks"],
        facts["confirmations"],
    )
    manifesto_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")

    issues_path = processing_dir / f"{meeting_id}.issues.yml"
    if not issues_path.exists():
        issues_path.write_text(
            yaml.safe_dump({"issues": []}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    return {
        "transcript": validation["path"],
        "ata": str(ata_path.relative_to(repo)),
        "manifesto": str(manifesto_path.relative_to(repo)),
        "metadata": validation["metadata"],
        "result": manifest,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in {1, 2}:
        raise SystemExit("Uso: python scripts/gerar_ata.py <transcricao> [repo_root]")

    transcript_path = args[0]
    repo_root = args[1] if len(args) == 2 else Path(__file__).resolve().parents[1]
    result = generate_ata(transcript_path, repo_root)
    print(f"ATA: {result['ata']}")
    print(f"Manifesto: {result['manifesto']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
