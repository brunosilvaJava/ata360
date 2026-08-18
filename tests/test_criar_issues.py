from pathlib import Path

from scripts.criar_issues import reconcile_issues


def test_reconcile_issues_only_creates_new_ones():
    issues_file = Path('tests/fixtures/issues-propostas.yml')

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
