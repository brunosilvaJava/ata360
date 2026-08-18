from pathlib import Path

from scripts.utils import read_front_matter, read_yaml, stable_issue_id


def test_read_yaml_success():
    data = read_yaml(Path('clientes/exemplo/cliente.yml'))
    assert data['id'] == 'exemplo'


def test_read_front_matter_success():
    metadata, body = read_front_matter(Path('clientes/exemplo/projetos/projeto-exemplo/transcricoes/2026-08-18-status.md'))
    assert metadata['reuniao_id'] == '2026-08-18-status'
    assert 'cronograma' in body


def test_stable_issue_id_is_deterministic():
    issue_id = stable_issue_id('acme', 'projeto-alpha', '2026-08-18-status', 'action-001')
    assert issue_id == 'ata360:acme:projeto-alpha:2026-08-18-status:action-001'
