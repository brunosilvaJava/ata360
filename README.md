# Ata360

Ata360 é uma proposta de sistema GitHub-native para transformar transcrições de reuniões em atas profissionais, tarefas, decisões e pendências rastreáveis.

## Visão geral

O sistema funciona sem frontend, banco de dados ou API pública. O GitHub é utilizado como repositório, executor de automações, mecanismo de revisão via Pull Requests e gestão de tarefas via Issues.

## Estrutura

- `clientes/`: registro de clientes e projetos em YAML
- `scripts/`: utilitários e validações em Python
- `templates/`: templates de ata, manifesto e issues
- `tests/`: testes unitários e fixtures
- `.github/workflows/`: fluxos de processamento, CI e pós-merge
- `.github/agents/`: instruções do agente Secretário Executivo

## Fluxo principal

1. Adicionar transcrição em `clientes/<cliente>/projetos/<projeto>/transcricoes/`
2. Validar estrutura e metadados
3. Executar o agente Secretário Executivo
4. Gerar ata, manifesto e arquivo de Issues propostas
5. Abrir Pull Request para revisão humana
6. Validar e fazer merge
7. Criar Issues apenas após merge

## Validação local

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Opcionalmente, você pode instalar as dependências diretamente (equivalente a `requirements.txt`):

    python -m pip install PyYAML pytest
