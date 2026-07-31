# Sprint — Política de corpus

**2026-07-31** · `main` @ `5ef1a85` · PRs #46 e #47 mergeados

---

## A pergunta que abriu o ciclo

> *"Podemos usar o KB, ou devemos aprimorá-lo antes? Estou estudando Google Dorking e queria puxar um artigo robusto da minha base. Mas a ferramenta foi feita sobre fundamentos não tão bons — busca genérica. Penso em refazer todo o vault."*

A hipótese tinha três partes. **Duas estavam erradas e a terceira apontava para a camada errada.**

---

## O que a medição mostrou

### 1. O retrieval já estava consertado

O sprint anterior levou `recall@5` de 0,230 para **0,467** e MRR de 0,127 para **0,343**, contra golden de 152 casos. Está no ADR-0017, que supera o ADR-0004. A queixa de "busca genérica" descrevia um estado já superado.

### 2. O corpus não é raso

A medição inicial reportou *"1.022 de 1.037 artigos com uma única seção preenchida"* — e a conclusão estava **errada**. O detector contava os nomes literais do template.

| Métrica | Seções do template | Headings reais |
|---|---:|---:|
| Mediana por artigo | 1 | **10** |
| Média | 1,21 | **11,7** |
| Máximo | 2 | **69** |
| Artigos com ≥5 headings | — | **965 de 1.038 (93%)** |
| Artigos sem heading | — | **0** |

Os artigos são estruturados — só usam headings derivados do conteúdo, não os nomes fixos do template. Exemplo real: `autenticacao-de-requisicoes-por-assinatura-digital.md`, 1.552 palavras e **15 headings** ("Prova de Origem", "Não-Repúdio", "Fingerprint de Requisição HTTP", "Proteção contra Replay").

**Recompilar "para consertar rasura" destruiria estrutura existente.**

### 3. Refazer o vault duplicaria a wiki

`manifest.json` nunca foi materializado, então `find_compiled_entry()` devolve `None` para tudo e o compile escreve em caminho novo derivado do título. Isso não é teoria — aconteceu durante a travessia:

| Artigo | `source` |
|---|---|
| `reconhecimento-de-motor-de-busca-para-vazamento-de-informaca.md` | `raw.githubusercontent.com/.../01-Conduct_Search_Engine...md` |
| `reconhecimento-de-desconhecimento-de-informacao-via-motores-.md` | `wstg-latest-owasp-foundation.md` |

O **mesmo documento OWASP** virou dois artigos. `wiki/cybersecurity/` foi de 11 para 13.

### 4. E o motivo real de o artigo não sair

Não havia **uma linha** sobre dorking, OSINT ou recon no vault. A `library/` cobre `finance`, `llm`, `psychology`, `software-engineering`. Nenhum rebuild produz conhecimento que não entrou.

---

## O gargalo real: a camada de compilação

A travessia levou um tema do zero ao artigo lido e registrou seis atritos. Os que importam:

**O `kb ingest` de página dinâmica traz nada e reporta sucesso.** O GHDB — base canônica de dorks — foi ingerido com **zero dorks**, só `"This site requires JavaScript"`. Com 1.358 palavras de chrome, parece conteúdo legítimo.

**O artigo compilado tem seção "Exemplos" sem um único exemplo.** Duas vezes, com contextos de 16k e 64k. O template *já manda* omitir seção sem material; o modelo ignorou e preencheu com a lista de motores de busca.

**Erro de compile chega ao leitor com cara de fato.** O artigo traduziu *match* como "concorda", e `"filetype: Concorda apenas um tipo de arquivo"` apareceu **íntegro nas duas respostas do `qa`** medidas. Nenhum gate entre o compile e a leitura pega isso.

### Perfis de retrieval, medidos

| Perfil | Tempo | Resultado |
|---|---|---|
| `fast` (default) | 2m50 | encadeamento em uma frase abstrata |
| `--deep` | 7m48 | seção própria de encadeamento, citando `site:` + `inurl:` + `filetype:` |

O `--deep` é melhor e custa 2,7×. Nenhum dos dois produz um dork concreto — o teto é a fonte.

---

## O que foi entregue

### Gate de saída do compile (PR #46)

`_validate_output` aceitava qualquer coisa com frontmatter parseável. Agora barra:

- **seção declarada e vazia** — respeitando hierarquia, já que um `##` que agrupa `###` não é vazio;
- **placeholder do template não substituído** — comparando com os marcadores reais do molde, então `<T extends Base>` e `<div>` passam; varre o markdown inteiro, frontmatter incluído.

**Calibrado contra o corpus real: 1 reprovado em 1.039 (0,10%)**, e é legítimo.

O caminho teve três correções, todas achadas por rodar contra dados reais em vez de confiar na suíte:

1. a primeira versão **reprovou o melhor artigo do vault** (H2 agrupador contado como vazio);
2. o detector de placeholder deu **falso positivo em notação matemática** (`< 3 log n para n >`);
3. o review do PR apontou **generics TypeScript** e que o **frontmatter não era varrido**.

### Infra local, medida

| Config | Footprint | 100 tokens | Prompt de 11.381 tokens |
|---|---:|---:|---|
| 16k, KV `f16` | 9.609 MB | — | 6m49 → **falhou** |
| 16k, KV `q8_0` | 1.540 MB | 17,6 tok/s | 5m17 |
| **64k, KV `q8_0`** | **3.178 MB** | 16,6 tok/s | 4m20 → **passou** |

Quadruplicar o contexto custou 1.638 MB, batendo com a previsão da fórmula. **Mais contexto resolveu o crash, não a qualidade** — a seção "Exemplos" continuou vazia de exemplos.

### O que não funcionou, e por quê

**Mover o modelo para a VM.** A `g0dw1n` é **Vulkan**, não ROCm (RX 6600, 8 GB). A pesquisa de código confirmou que existe `dequant_q1_0.comp` no backend Vulkan, mas o canário real deu **96%/4% CPU/GPU** e 4,71 tok/s contra 17,6 no Metal local. Suporte declarado no shader não implica caminho acelerado.

**Detectar "Exemplos que não são exemplos".** Três heurísticas medidas e descartadas:

| Heurística | Resultado |
|---|---|
| Jaccard entre seções | alvos 0,205 e 0,109; p99 do corpus 0,254 — sem limiar que separe |
| Concretude condicional | pega os alvos, reprova **19,4%** dos artigos técnicos legítimos |
| Fração de termos novos | alvos 0,574 e 0,600 — **acima** da mediana (0,571) |

Exige juiz semântico com LLM no gate — decisão de custo própria.

---

## Números do ciclo

| Métrica | Valor |
|---|---|
| Commits | 5 (+ 2 merges) |
| Testes | **608 passam** · cobertura 91% · `kb/compile.py` 92% |
| Testes novos | 7 |
| Tickets do map | 2 resolvidos de 8 · frontier em 001 |
| Features formais | 0 — o ciclo correu por `wayfinder` |
| Cycle time | N/D — ciclo de decisão, não de feature |

---

## Achado de segurança (P1, novo)

`kb ingest <url>` foi usado pela primeira vez, trazendo 4 páginas de terceiro para o vault. O caminho `raw/ → compile → wiki → qa` faz **conteúdo web arbitrário virar contexto do LLM em duas etapas**, e `kb/guardrails.py` verifica apenas `SENSITIVE_PATTERNS` — **nenhuma checagem de prompt injection**.

A regra 8 do AGENTS.md não tem enforcement neste caminho. O conteúdo desta sessão está limpo; não há gate para o próximo. `kb/web_ingest.py` já protege contra SSRF — a fronteira foi pensada para rede, não para conteúdo.

A última auditoria de segurança é de **2026-04-07**. Registrada para o próximo ciclo.

---

## Armadilhas registradas

Três novas, todas do mesmo tipo — *o número não media o que parecia*:

1. **Medir aderência a template e chamar de rasura.** Segunda ocorrência do padrão do golden set por título.
2. **Compatibilidade de shader não implica offload.**
3. **Footprint de processo longo mistura vazamento com configuração** — a queda de 8 GB veio do reinício, não da mudança.

---

## Próximo ciclo

**Ticket 001** (P0, frontier): o golden de 152 casos e as **869 fontes de `library/` (185 MB) estão fora do git**, enquanto o ticket 006 discute recompilar o corpus. Sem o material bruto, essa opção deixa de existir.

Depois, **ticket 004** — *a wiki é produto ou insumo?* — destravado com 002 e 003 entregues, e a decisão da qual as outras derivam.

---

*Relatório do ciclo · kb · 2026-07-31*
