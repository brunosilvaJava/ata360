from pathlib import Path

import pytest

from scripts.validar_estrutura import validate_transcript


def test_validate_transcript_accepts_valid_file():
    payload = validate_transcript('clientes/exemplo/projetos/projeto-exemplo/transcricoes/2026-08-18-status.md', Path('.'))
    assert payload['metadata']['cliente_id'] == 'exemplo'
    assert payload['metadata']['projeto_id'] == 'projeto-exemplo'


def test_validate_transcript_rejects_absolute_path():
    with pytest.raises(ValueError):
        validate_transcript('/tmp/arquivo.md', Path('.'))


def test_validate_transcript_rejects_path_traversal():
    with pytest.raises(ValueError):
        validate_transcript('clientes/../secret.txt', Path('.'))


def test_validate_transcript_rejects_empty_body(tmp_path):
    repo_root = tmp_path
    client_dir = repo_root / 'clientes' / 'acme'
    project_dir = client_dir / 'projetos' / 'projeto-alpha' / 'transcricoes'
    project_dir.mkdir(parents=True)
    (client_dir / 'cliente.yml').write_text('id: acme\nnome: ACME\nsigla: ACME\nidioma_padrao: pt-BR\nfuso_horario: America/Sao_Paulo\nestilo_ata: executivo-formal\nativo: true\n', encoding='utf-8')
    (client_dir / 'projetos' / 'projeto-alpha' / 'projeto.yml').write_text('id: projeto-alpha\ncliente_id: acme\nnome: Projeto Alpha\ncodigo: ALPHA\nstatus: ativo\nresponsavel_interno: Bruno Silva\nestilo_ata: executivo-tecnico\nlabels_padrao:\n  - cliente:acme\n  - projeto:alpha\n', encoding='utf-8')
    empty_file = project_dir / 'reuniao-vazia.md'
    empty_file.write_text('---\ncliente_id: acme\nprojeto_id: projeto-alpha\nreuniao_id: reuniao-vazia\ntitulo: Reunião vazia\ndata: 2026-08-18\ntipo: acompanhamento\nidioma: pt-BR\nparticipantes:\n  - Bruno\n---\n\n', encoding='utf-8')

    with pytest.raises(ValueError):
        validate_transcript('clientes/acme/projetos/projeto-alpha/transcricoes/reuniao-vazia.md', repo_root)
