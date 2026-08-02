# O artigo compilado presta para estudar? Qual o gate de qualidade que falta?

Type: grilling
Status: open
Blocked by: 001 (o que é "bom" depende de como é lido)

## Question

O map anterior mediu que o compile produz artigo com estrutura, mas o defeito que o ticket 002 daquele map achou — **seção "Exemplos" sem exemplos, tradução errada no título** — não é pego por gate nenhum, e as três heurísticas testadas para detectá-lo foram descartadas com medição.

Amostra desta sessão, compilada com o Codex Luna:

- `google-hacking-database-ghdb.md` (475 palavras): frontmatter correto, resumo, conceitos centrais, wikilinks para `[[OSINT]]`, `[[Bing]]`, `[[GitHub]]`. Utilizável.
- `ataque-xss-explicado.md` (**69 palavras**): curto demais para um tema que dá livro inteiro. Sinal de fonte pobre ou de compile que desistiu.
- `reconhecimento-de-motor-de-busca-para-vazamento-de-informaca.md` (850 palavras): bom conteúdo, mas o **título foi truncado no slug** e o corpo tem "contenido" (espanhol) e "operators" sem traduzir.

### Pontos a fechar

- **O que é "artigo bom" para estudar?** Profundidade, exemplos concretos, comandos executáveis, referência à fonte? O critério muda o gate.
- **69 palavras deveria falhar o gate?** Existe piso de tamanho por tipo de tema?
- **Truncamento de slug** (`...informaca.md`) é cosmético ou quebra wikilink?
- **Qualidade da tradução**: vale um passe de revisão, ou compilar em inglês e traduzir só o que for ler?
- **O grounding ajuda aqui?** A verificação de ancoragem já roda no `qa`; roda no `compile`?

## Answer

<!-- preencher no grilling -->
