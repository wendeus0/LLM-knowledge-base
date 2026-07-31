# Medir a qualidade real dos artigos existentes

Type: research
Status: claimed c703a376-ae52-4e74-b6bf-e4c363c1b195 (fable-gpt / GPT 5.6 Terra)

## Question

Quão rasos são os 1.037 artigos, de fato?

A afirmação "o vault foi compilado sobre fundamentos ruins e precisa ser refeito" é hoje uma hipótese sem um número por trás. O ticket 006 vai decidir entre manter, arquivar e recompilar — e as três opções são fé enquanto ninguém mediu o que existe. Recompilar 1.037 artigos com o documento inteiro no prompt custa de 1.037 a 2.074 chamadas de LLM; a decisão merece evidência.

Medir, sobre amostra estratificada por topic:

- **Razão de compressão fonte→artigo.** Quantas palavras entraram, quantas saíram. O compile não faz chunking: um capítulo inteiro entra em uma chamada e sai como 7 seções. Ninguém registrou o quanto se perde.
- **Densidade estrutural.** Seções do template efetivamente preenchidas vs. omitidas (o prompt manda omitir seção sem material — quanto isso morde na prática), wikilinks por artigo, referências por artigo. A definição de artigo robusto de `011/DOMAIN.md:11` propunha gate em 5 referências reais: quantos artigos passariam hoje?
- **Distribuição de tamanho.** `_validate_output` (`kb/compile.py:64-74`) aceita três frases. Quantos artigos estão perto desse piso? A cauda curta é o que importa.
- **Taxa de near-duplicate.** O V5 do backlog anterior classificou dedup como "valor alto, condicionado a medição" e pediu explicitamente para medir antes de agir. O `embeddings.json` já tem 8.685 chunks vetorizados — o material para medir está pronto, é cosseno sobre o que já existe.
- **Cobertura por topic.** Onde o corpus é denso e onde é decorativo. `wiki/cybersecurity/` tem 11 artigos; `cybersecurity` é topic default com `topic_bonus` de 0,05 (`kb/claims.py:64`). Quantos outros topics estão nessa situação?

**Restrição:** medição só, zero conserto. Nenhum artigo é reescrito, nenhum arquivo do vault é modificado. O script de análise vive no scratchpad ou em `scripts/`, não no vault.

**Saída:** documento `MEDICAO-CORPUS.md` neste diretório, com os números e o método, linkado deste ticket. Números com o comando que os produziu — a regra de casa vale: sem evidência, `UNVERIFIED`.

Ticket AFK: resolve sem o usuário, em paralelo com 001 e 002.

## Answer

<!-- preencher na resolução -->
