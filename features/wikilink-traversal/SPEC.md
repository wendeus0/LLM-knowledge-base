---
title: Wikilink Traversal — Router segue [[links]] durante QA
epic: qa
status: draft
pr:
---

# Wikilink Traversal — Router Segue [[links]] Durante QA

## Objetivo

Hoje o router seleciona arquivos para contexto de QA via contagem de palavras-chave. Arquivos relacionados referenciados por `[[wikilinks]]` não são carregados — o LLM responde sem o grafo de conhecimento que a wiki representa. O router deve seguir wikilinks nos arquivos carregados para enriquecer progressivamente o contexto, até o limite da janela disponível.

## Contexto arquitetural

O conceito de "skill graph" do Post 1 (arscontexta): cada nó tem YAML description para scan sem leitura completa; wikilinks entre arquivos carregam semântica (o link está numa frase que diz quando e por que seguir); o padrão de progressive disclosure evita explosão de contexto.

Nossa wiki já usa `[[wikilinks]]` em markdown. O que falta é o router entender e explorar esse grafo.

## Requisitos funcionais

- [ ] Após selecionar os arquivos iniciais por palavra-chave (comportamento atual), o router extrai todos os `[[wikilinks]]` presentes nesses arquivos
- [ ] Para cada wikilink extraído, resolve o path do arquivo correspondente em `wiki/`
- [ ] Carrega o frontmatter YAML do arquivo linkado (apenas frontmatter, sem conteúdo completo) para avaliar relevância
- [ ] Se o frontmatter indicar relevância com a pergunta original (via match de `tags` ou `title`), carrega o conteúdo completo
- [ ] Profundidade default: **1** (links dos arquivos iniciais, não links dos links)
- [ ] Profundidade configurável: `--depth 2` para segundo nível
- [ ] Limite de contexto: o traversal para automaticamente quando o contexto acumulado atingir 80% do limite configurado em `config.py` (`MAX_CONTEXT_TOKENS`)
- [ ] Arquivos já carregados não são visitados duas vezes (evitar ciclos)
- [ ] `kb qa` sem flags usa traversal por padrão (opt-out: `--no-traverse`)

## Requisitos técnicos

- Novo módulo `kb/graph.py` com:
  - `extract_wikilinks(content: str) -> list[str]` — regex `\[\[([^\]]+)\]\]`
  - `resolve_wikilink(link: str, wiki_dir: Path) -> Path | None` — busca `wiki/**/<link>.md`
  - `load_frontmatter(path: Path) -> dict` — lê apenas o bloco YAML sem o corpo
  - `traverse(seed_files, question, depth, token_budget) -> list[Path]` — BFS com budget
- `router.py`: após seleção inicial por keyword, chamar `graph.traverse()` para expandir contexto
- `config.py`: adicionar `WIKILINK_TRAVERSAL_DEPTH = 1` e `MAX_CONTEXT_TOKENS = 8000`
- Token estimation simples: `len(content) // 4` (aproximação suficiente para controle de budget)
- Relevância de frontmatter: match de qualquer tag da pergunta com `tags` do arquivo linkado, ou substring do `title`

## Algoritmo de traversal (BFS com budget)

```
1. seed_files = keyword_search(question)          # comportamento atual
2. queue = extract_wikilinks(seed_files)
3. visited = set(seed_files)
4. context = seed_files content
5. while queue and tokens(context) < budget:
   a. path = resolve(queue.pop())
   b. if path in visited: skip
   c. fm = load_frontmatter(path)
   d. if relevant(fm, question):
      - content = load_full(path)
      - context += content
      - if depth > 1: queue += extract_wikilinks(content)
   e. visited.add(path)
6. return context
```

## Mudanças de API

```bash
# Comportamento padrão (com traversal, depth=1):
kb qa "O que é XSS e como se relaciona com CSP?"

# Desativar traversal:
kb qa "O que é XSS?" --no-traverse

# Profundidade 2:
kb qa "O que é XSS?" --depth 2
```

## Testes

- **Unit:** `test_graph.py`
  - `extract_wikilinks()`: detecta `[[link]]`, `[[Link com espaço]]`, ignora `[link normal](url)`
  - `resolve_wikilink()`: encontra arquivo, retorna None se não existir
  - `traverse()`: para no budget, não visita dois vezes, respeita depth
- **Integration:** QA numa wiki com artigos interligados — confirmar que contexto inclui arquivos linkados relevantes
- **Manual:** comparar qualidade de resposta com e sem `--no-traverse` em pergunta que cruza dois tópicos

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 5h |
| Bloqueador | não |
| Risk | média |

## Dependências

- Wiki existente com `[[wikilinks]]` (já gerados pelo compile atual)
- `outputs-store` não é pré-requisito

## Notas

- Risk médio porque altera o pipeline crítico de QA — requer validação manual de qualidade antes de marcar como done
- O módulo `graph.py` é isolado e testável independentemente do router
- `--no-traverse` garante escape hatch sem risco de regressão
- Depth 2 pode dobrar o número de arquivos carregados — documentar no `--help` com aviso de custo de tokens
- Progressive disclosure (carregar só frontmatter antes de decidir) é o que mantém o custo controlado
