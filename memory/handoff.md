---
name: Handoff
description: Estado para a próxima sessão
type: project
---

## Handoff — 2026-07-31 (sprint da política de corpus)

### Onde parou

`main` @ `6cd8d88`, tudo pushado, PR #46 mergeado, CI verde em 3.11/3.12/3.13. Working tree limpo. `608 passed` / 91%.

O sprint respondeu a pergunta que o abriu — *"posso usar o KB para estudar, ou preciso refazer o vault?"* — e a resposta é **nenhum dos dois**. O retrieval já estava consertado (ADR-0017, sprint anterior). O corpus **não é raso**: mediana de 10 headings por artigo, 93% com ≥5. O gargalo é a **camada de compilação**, e o primeiro conserto dela foi entregue.

### O que entrou

- **Wayfinder da política de corpus** — `docs/research/2026-07-30-politica-de-corpus/`, 8 tickets. Destination: ADR que trava origem do conhecimento novo, destino dos 1.037 artigos, wiki como produto ou insumo, e superfície de leitura.
- **Gate de saída do compile** — `_validate_output` barra seção declarada e vazia e placeholder do template não substituído. Reconhece placeholder comparando com os marcadores reais do template, então `<T extends Base>` e `<div>` passam; cobre o markdown inteiro, frontmatter incluído. 7 testes. Calibrado contra o corpus: 1 reprovado em 1.039 (0,10%).
- **Infra local medida** — `-ctk q8_0 -ctv q8_0` e `--ctx-size 65536` em `start-bonsai-server.sh`. Footprint 9.609 → 3.178 MB **com 4× o contexto**; o compile de documento de 11k tokens deixou de falhar.

### Tickets resolvidos

**002 — travessia do caso Google Dorking.** Seis atritos registrados. Os que mais importam: `kb ingest` de página JS-dinâmica traz **zero conteúdo e reporta sucesso** (o GHDB veio só com `"This site requires JavaScript"`); o `qa --deep` é melhor que o `fast` mas custa 2,7× o tempo; e **erro de compile se propaga ao QA** — `"filetype: Concorda apenas um tipo de arquivo"` chegou íntegro às duas respostas medidas. A duplicação prevista aconteceu: o mesmo documento OWASP virou dois artigos, e `wiki/cybersecurity/` foi de 11 para 13.

**003 — medição do corpus.** A conclusão original do subagente estava errada e foi corrigida no próprio documento: "1.022 artigos com uma seção" media aderência ao template, não rasura. Seguem válidos: **1.035 de 1.037 sem nenhuma referência**, **59 pares** com cosseno ≥0,95, e proveniência perdida (compressão fonte→artigo não é mensurável).

### Próximo passo

**Ticket 001** (frontier, P0): proteger o golden de 152 casos e as **869 fontes de `library/` (185 MB, fora do git)**. O ticket 006 discute recompilar o corpus; sem o material bruto, essa opção não existe.

Depois, **ticket 004** — destravou com 002 e 003 entregues, e é a decisão da qual as outras derivam.

### Armadilhas a não repetir

Três novas em `pitfalls.md`, todas do tipo "o número não media o que parecia":

1. **Medir aderência a template e chamar de rasura** — teria justificado recompilar 1.037 artigos e destruir estrutura existente.
2. **Compatibilidade de shader não implica offload** — o `Q1_0` tem shader Vulkan e ainda assim rodou 96% em CPU na VM, a 4,71 tok/s contra 17,6 no Metal local.
3. **Footprint de processo longo mistura vazamento com configuração** — a queda de 8 GB ao quantizar o KV veio do reinício, não da mudança; a conta previa menos de 1 GB.

### Estado da infra

- `:8081` (`llama-server`, bonsai) roda **fora do launchd** apesar de `KeepAlive`, último exit 1. Se morrer, não volta.
- A VM `g0dw1n` é **Vulkan**, não ROCm — RX 6600, 8 GB de VRAM, 6,4 GB livres. Baixou o `Bonsai-27B-Q1_0` (4,4 GB) no canário; pode ser removido. O `ornith-1.0:35b` foi deletado a pedido (re-baixável do HF).
- `~/dev/personal/local-ai-lab` tem mudanças não commitadas, incluindo o `start-bonsai-server.sh` editado (untracked naquele repo) e um relatório de infra escrito por um agente.

### Prompt de retomada

> Retomando o kb em `main` @ `6cd8d88`. O map da política de corpus está em `docs/research/2026-07-30-politica-de-corpus/` com 8 tickets; 002 e 003 resolvidos, frontier em 001. Comece pelo ticket 001 — proteger o golden set e as 869 fontes de `library/`, que estão fora do git — e depois trabalhe o 004, que destravou e é a decisão central do map.
