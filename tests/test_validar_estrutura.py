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


def test_validate_transcript_rejects_empty_body():
    empty_file = Path('tests/tmp-empty.md')
    empty_file.write_text('---\ncliente_id: exemplo\nprojeto_id: projeto-exemplo\nreuniao_id: x\ntitulo: Teste\ndata: 2026-08-18\ntipo: acompanhamento\nidioma: pt-BR\nparticipantes:\n  - Bruno\n---\n\n', encoding='utf-8')
    try:
        with pytest.raises(ValueError):
            validate_transcript(str(empty_file), Path('.'))
    finally:
        empty_file.unlink(missing_ok=True)
