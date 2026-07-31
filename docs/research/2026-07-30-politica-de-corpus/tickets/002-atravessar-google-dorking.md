# Atravessar Google Dorking à mão

Type: task
Status: claimed c703a376-ae52-4e74-b6bf-e4c363c1b195

## Question

O que quebra de fato ao levar um tema novo do zero até o artigo lido?

Este é o caso que abriu o esforço: estudar reconhecimento em cibersegurança e querer um artigo robusto sobre Google Dorking. O vault não tem uma linha sobre o assunto. Em vez de decidir a política no abstrato, atravessar o caminho inteiro uma vez, à mão, registrando cada atrito: escolher fonte → `kb ingest` → `kb compile` → `kb qa` → ler o que saiu.

Sai daqui a evidência que desbloqueia 004 e alimenta 005 e 006. Sai também o artigo que motivou o esforço.

**Hipóteses a confirmar ou derrubar** — todas com endereço no código, nenhuma medida:

1. **O guardrail barra o próprio conteúdo.** `guardrails.py` aborta com `SensitiveContentError` em padrões `api_key`/`token`/`password`/`secret`. Um artigo de dorking cheio de `intext:"api_key"` e `filetype:env` é o falso positivo perfeito — é o pitfall P9, e `--allow-sensitive` é o escape hatch. A pergunta real: um corpus de segurança ofensiva torna o guardrail inútil por saturação de opt-in?
2. **O perfil errado está ligado no `qa`.** O default é `fast`: `top_k=3`, artigos capados em 4.000 chars (`kb/config.py:85`), e o cap de 4k corta a cauda de 40% dos artigos (`013/REPORT.md:31`). Enquanto isso o perfil `article` — `top_k=5`, 8.000 chars, travessia com budget 4.000 (`kb/config.py:88`) — existe e **não tem consumidor nenhum**. Se o produto é o output do `qa`, ligar `article` pode ser a mudança de maior efeito por menor custo do projeto inteiro. Comparar as duas saídas na mesma pergunta.
3. **O artigo compilado sai raso.** Prompt sem instrução de profundidade, validação que aceita três frases, `max_tokens` nunca enviado. Ver o tamanho real do que sai de uma fonte densa.
4. **O modelo local dá conta.** `bonsai-27b-1bit` a 3,79 GB de quantização 1-bit, `n_ctx` 16384. Redigir um artigo técnico longo é tarefa diferente de reordenar 20 candidatos. Se não der, a política de corpus herda uma restrição de modelo.

**Restrição de método:** uma fonte, um tema, um caminho. Não otimizar nada no meio — o valor deste ticket é o registro fiel do atrito, não o conserto. Cada atrito vira linha na resposta; o que merecer conserto vira ticket ou entra no ADR.

## Answer

**Parcial — travessia pela via web concluída em 2026-07-31; falta a via livro.**

Fontes ingeridas em `~/vault/raw/`: OWASP WSTG (HTML e markdown puro), Wikipedia "Google hacking", GHDB do Exploit-DB. Artigo compilado: `wiki/cybersecurity/reconhecimento-de-motor-de-busca-para-vazamento-de-informaca.md`.

### Atritos registrados

| # | Atrito | Evidência |
|---|---|---|
| 1 | `web_ingest` não remove boilerplate — banner de cookies, menu, aviso de JS entram no `raw/` e seguem inteiros para o prompt do compile | `wstg-latest-owasp-foundation.md`: 2.457 palavras, parte relevante < 1/3 |
| 2 | **Página JS-dinâmica vem vazia e o ingest reporta sucesso.** O GHDB — base canônica de dorks — foi ingerido com **zero dorks**, só `"This site requires JavaScript"`. Falha silenciosa: 1.358 palavras de chrome parecem conteúdo legítimo | `google-hacking-database-ghdb-google-dorks-osint-recon.md:55` |
| 3 | `html2text` sobre markdown puro **colapsa o documento numa única linha** — os `##` viram texto inline, matando o chunking por seção de `kb/chunking.py` | `raw-githubusercontent-com-owasp-wstg-mas.md` |
| 4 | `kb compile <path relativo>` interpreta o caminho como nome de livro e falha com `"Nenhum livro encontrado"`. Exige caminho absoluto; a mensagem não indica isso | — |
| 5 | **Compile morreu após 6m49** com `CompileOutputError: output sem frontmatter YAML` e traceback Python bruto. Não há retry para esse caso — o retry existente só cobre resource-limit do provider | `kb/compile.py:67`, `:346` |
| 6 | Nomes de arquivo derivados de `title`/URL não descrevem o assunto, e o slug trunca em 60 chars no meio da palavra: `...vazamento-de-informaca.md` | `kb/compile.py:217` |

### Hipóteses do ticket

**H1 — o guardrail barra conteúdo de segurança ofensiva: DERRUBADA.** Texto com "passwords", "usernames", "private keys" e operadores de dork passou sem `--allow-sensitive`. A preocupação se inverte: o guardrail pode ser frouxo demais para este tipo de corpus.

**H2 — o perfil `fast` dá contexto insuficiente: CONFIRMADA, com teto.** Medido na mesma pergunta:

| Perfil | Tempo | Resultado |
|---|---|---|
| `fast` (default, `top_k=3`, cap 4k) | 2m50 | 3 seções; trata encadeamento em uma frase abstrata |
| `--deep` (`top_k=5`, 8k) | 7m48 | 5 seções numeradas + conclusão; ganha seção própria de "Encadeamento de Operadores" citando a combinação `site:` + `inurl:` + `filetype:` |

O `--deep` é melhor e custa 2,7× o tempo. Mas **nenhum dos dois produz um dork concreto**, porque o artigo-fonte não tem nenhum. O perfil `article` (`kb/config.py:88`) segue sem consumidor.

**H3 — o artigo compilado sai raso: CONFIRMADA, e pior que raso.** 850 palavras, as 7 seções do template presentes, 5 wikilinks. Mas:
- a seção **"Exemplos" não tem exemplos** — repete a lista de motores de busca da seção anterior. Num artigo sobre dorking, zero dorks;
- erros de tradução: `"os índices contêm **contenido**"` (espanhol), `"filetype: **Concorda** apenas um tipo de arquivo"` (*match* traduzido literalmente), "Outras Serviços";
- "Google Hacking Database" **duplicado** nas referências, e nenhuma referência tem URL;
- os 5 wikilinks (`[[Crawling]]`, `[[OSINT]]`, …) apontam para artigos inexistentes — **nascem quebrados**;
- perdeu conteúdo da fonte: as categorias de dorks do GHDB e a seção de OSINT/Maltego sumiram;
- o link do "Google hacking" foi trocado: a fonte apontava para a Wikipedia, o artigo aponta para o exploit-db.

**H4 — o modelo local dá conta: PARCIAL.** Por conhecimento paramétrico o `bonsai-27b-1bit` responde bem — melhor que o `deephat-v1:7b` da VM, que é especializado em segurança. Nenhum dos dois recusa o tema. Mas o bonsai falhou em aderir ao formato num documento de 11.370 tokens (medido no tokenizer do próprio modelo) contra `n_ctx` de 16.384 — **coube com folga, então não foi falta de contexto**. O `ornith-35b` roda na VM, contrariando `PENDING_LOG.md:145`, mas é modelo de raciocínio e consumiu o orçamento inteiro em `<think>`; o compile não remove esses blocos.

### O achado que atravessa tudo

**Erro de compile se propaga ao QA com aparência de fato.** O `"Concorda apenas um tipo de arquivo"` do artigo aparece íntegro nas duas respostas do `qa`. O QA é fiel à fonte — e é justamente por isso que um artigo raso com erros produz resposta rasa com os mesmos erros. Nenhum gate entre o compile e o leitor detecta isso: `_validate_output` só checa frontmatter, e `kb lint` audita 20 de 1.037 artigos.

Isso é insumo direto do ticket 004: mesmo tratando a wiki como insumo, a qualidade do artigo determina a qualidade da resposta. "Insumo" não isenta o compile de um gate.

### Segunda rodada — com 64k de contexto (2026-07-31)

Depois de quantizar o KV cache (`-ctk q8_0 -ctv q8_0`) e subir `--ctx-size` de 16.384 para 65.536, o compile que falhava **passou**: 7m08, artigo gerado.

| Config | Footprint | 100 tokens | Prompt de 11.381 tokens |
|---|---|---|---|
| 16k, KV `f16` (original) | 9.609 MB | — | 6m49 → **falhou** |
| 16k, KV `q8_0` | 1.540 MB | 17,6 tok/s | 5m17 |
| **64k, KV `q8_0`** | **3.178 MB** | 16,6 tok/s | 4m20 → **passou** |

Quadruplicar o contexto custou 1.638 MB, batendo com a previsão de `PESQUISA-OTIMIZACAO-AMD.md`. A velocidade não mudou. **A falha original não era o prompt não caber — era não sobrar janela para a resposta depois dele.**

**Mas contexto não resolveu a qualidade, e isso é o achado que importa:**

- **A seção "Exemplos" continua sem exemplos.** Com 4× o contexto, o modelo repetiu exatamente o mesmo comportamento: listou os nove motores de busca de novo. Zero dorks. O problema é do **prompt/template**, não do modelo nem da janela.
- **Erro grave no título:** `"Reconhecimento de **Desconhecimento** de Informação"` — *Information Leakage* virou "Desconhecimento" em vez de "Vazamento". `_validate_output` aprova, porque só checa se `title` é não-vazio.
- **Ficou menor**: 678 palavras contra 850 da primeira tentativa, com mais contexto disponível.
- Ganhou uma seção que a primeira perdeu ("Ferramentas de Correlação OSINT", com Maltego).

**A duplicação prevista aconteceu, e está observável no vault:**

| Artigo | `source` |
|---|---|
| `reconhecimento-de-motor-de-busca-para-vazamento-de-informaca.md` | `raw.githubusercontent.com/.../01-Conduct_Search_Engine_Discovery....md` |
| `reconhecimento-de-desconhecimento-de-informacao-via-motores-.md` | `wstg-latest-owasp-foundation.md` |

**São o mesmo documento OWASP** — um ingerido como HTML, outro como markdown puro — e viraram dois artigos com títulos diferentes, ambos em `wiki/cybersecurity/`, que foi de 11 para 13 artigos. Sem `manifest.json` e sem dedup no compile, nada detecta isso. É a prova empírica do que o ticket 006 discute em teoria e do V5 do backlog anterior.

### Pendente

- Via livro (`kb import-book`) — depende de o usuário obter o arquivo.
- Comparação entre um artigo vindo de livro e um vindo da web no mesmo topic, que é o que o ticket 005 precisa saber sobre convivência de origens.
