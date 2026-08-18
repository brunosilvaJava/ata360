from pathlib import Path

import pytest
import yaml

from scripts.gerar_ata import generate_ata


def make_valid_repo(tmp_path: Path) -> tuple[Path, Path]:
    client_dir = tmp_path / 'clientes' / 'acme'
    project_dir = client_dir / 'projetos' / 'projeto-alpha'
    trans_dir = project_dir / 'transcricoes'
    trans_dir.mkdir(parents=True)

    (client_dir / 'cliente.yml').write_text(
        'id: acme\nnome: ACME\nsigla: ACME\nidioma_padrao: pt-BR\nfuso_horario: America/Sao_Paulo\nestilo_ata: executivo-formal\nativo: true\n',
        encoding='utf-8',
    )
    (project_dir / 'projeto.yml').write_text(
        'id: projeto-alpha\ncliente_id: acme\nnome: Projeto Alpha\ncodigo: ALPHA\nstatus: ativo\nresponsavel_interno: Bruno Silva\nestilo_ata: executivo-tecnico\nlabels_padrao:\n  - cliente:acme\n  - projeto:alpha\n',
        encoding='utf-8',
    )
    transcript = trans_dir / 'reuniao-001.md'
    transcript.write_text(
        '---\ncliente_id: acme\nprojeto_id: projeto-alpha\nreuniao_id: reuniao-001\ntitulo: Reunião de planejamento\ndata: 2026-08-18\ntipo: acompanhamento\nidioma: pt-BR\nparticipantes:\n  - Ana Souza\n  - Bruno Silva\n---\n\n[00:00:10] Ana Souza: Vamos revisar o cronograma.\n\n[00:02:15] Bruno Silva: Enviarei a versão revisada até sexta-feira.\n\n[00:05:20] Ana Souza: A validação será feita na próxima reunião.\n',
        encoding='utf-8',
    )
    return tmp_path, transcript


def test_generate_ata_creates_markdown_and_manifest(tmp_path):
    repo_root, transcript = make_valid_repo(tmp_path)

    result = generate_ata(transcript.relative_to(repo_root), repo_root)

    ata_path = repo_root / result['ata']
    manifesto_path = repo_root / result['manifesto']
    assert ata_path.exists()
    assert manifesto_path.exists()
    content = ata_path.read_text(encoding='utf-8')
    assert 'Reunião de planejamento' in content
    assert 'Enviarei a versão revisada' in content
    manifest = yaml.safe_load(manifesto_path.read_text(encoding='utf-8'))
    assert manifest['status'] == 'aguardando-validacao'
    assert manifest['resultado']['tarefas'] >= 1

    issues_path = repo_root / manifest['arquivos']['issues']
    assert issues_path.exists()
    issues_payload = yaml.safe_load(issues_path.read_text(encoding='utf-8'))
    assert isinstance(issues_payload.get('issues'), list)

def test_generate_ata_rejects_traversal(tmp_path):
    repo_root, _ = make_valid_repo(tmp_path)

    with pytest.raises(ValueError):
        generate_ata('../secret.txt', repo_root)
