# Plano de Implementação do Ata360

## Visão geral

Este repositório foi organizado como estrutura inicial para o Ata360, um sistema GitHub-native para transformar transcrições em atas e tarefas rastreáveis.

## Objetivo

Processar uma transcrição isolada por cliente e projeto e gerar:

- ata em Markdown;
- manifesto YAML;
- arquivo de Issues propostas;
- branch e Pull Request para revisão;
- criação de Issues após merge.

## Principais regras

- revisão humana obrigatória antes da ata oficial;
- rastreabilidade por trecho da transcrição;
- fidelidade à fonte e impossibilidade de invenção;
- processamento por cliente/projeto/arquivo individual;
- idempotência para PRs, Issues e manifestos.

## Estrutura esperada

- `clientes/<cliente>/cliente.yml`
- `clientes/<cliente>/projetos/<projeto>/projeto.yml`
- `clientes/<cliente>/projetos/<projeto>/transcricoes/<reuniao>.md`
- `clientes/<cliente>/projetos/<projeto>/atas/<reuniao>.md`
- `clientes/<cliente>/projetos/<projeto>/processamento/<reuniao>.issues.yml`

## Regras de validação

- rejeitar caminhos fora do padrão `clientes/**`;
- impedir `..`, caminhos absolutos e nomes inseguros;
- verificar cliente e projeto existentes;
- comparar `cliente_id` e `projeto_id` do arquivo com o caminho;
- validar front matter e conteúdo não vazio.

## Entregáveis deste MVP

- estrutura de diretórios e exemplos;
- scripts Python para detecção e validação;
- geração de issues propostas com identificadores estáveis;
- testes automatizados;
- workflows de CI e processamento;
- documentação operacional e de governança.
