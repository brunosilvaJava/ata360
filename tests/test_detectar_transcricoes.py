from pathlib import Path

import pytest

from scripts.detectar_transcricoes import detect_transcricoes


def test_detect_transcricoes_finds_examples():
    paths = detect_transcricoes(Path('.'))
    assert any(path.endswith('2026-08-18-status.md') for path in paths)


def test_detect_transcricoes_accepts_explicit_file():
    paths = detect_transcricoes(Path('.'), explicit_file='clientes/exemplo/projetos/projeto-exemplo/transcricoes/2026-08-18-status.md')
    assert len(paths) == 1
    assert paths[0].endswith('2026-08-18-status.md')


def test_detect_transcricoes_requires_single_when_requested():
    with pytest.raises(ValueError):
        detect_transcricoes(Path('.'), require_single=True)
