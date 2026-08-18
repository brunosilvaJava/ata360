from pathlib import Path

from scripts.criar_issues import reconcile_issues


def test_reconcile_issues_only_creates_new_ones():
    issues_file = Path('tests/fixtures/issues-propostas.yml')
    if not issues_file.exists():
        issues_file.write_text(
            '''issues:
  - id: action-001
    tipo: action-item
    titulo: "[EXM][PE-01] Enviar versão revisada"
    labels:
      - generated-by-agent
      - action-item
    descricao: Enviar a versão revisada do documento.
    responsavel: Maria Souza
    prazo: sexta-feira
    confianca: alta
''',
            encoding='utf-8',
        )

    created = reconcile_issues(
        issues_file,
        client_id='exemplo',
        project_id='projeto-exemplo',
        reunion_id='2026-08-18-status',
        existing_issue_lookup=lambda identifier: identifier.endswith('action-001'),
    )
    assert len(created) == 0

    created_full = reconcile_issues(
        issues_file,
        client_id='exemplo',
        project_id='projeto-exemplo',
        reunion_id='2026-08-18-status',
        existing_issue_lookup=lambda identifier: False,
    )
    assert len(created_full) == 1
    assert created_full[0]['stable_id'].startswith('ata360:exemplo:projeto-exemplo:2026-08-18-status:action-001')
