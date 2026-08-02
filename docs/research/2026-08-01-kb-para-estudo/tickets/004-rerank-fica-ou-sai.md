# O rerank fica, sai ou troca de modelo?

Type: decision
Status: open

## Question

Depois da troca da geração para o Codex, o `bonsai-27b-1bit` em `:8081` ficou como **único gargalo**: é o motivo de todo comando desta sessão ter precisado de `--no-rerank`.

### O que a medição já diz

| Configuração | recall@5 | MRR |
|---|---|---|
| Lexical puro | 0,230 | — |
| + canal semântico | 0,414 | — |
| + rerank dos 20 primeiros | 0,467 | 0,343 |
| + correções de slug/snippet | **0,526** | **0,352** |

O rerank vale **+0,059 de recall@5 e +0,11 de MRR** — ganho real. A pergunta não é se ele serve, é a que custo.

### Pontos a fechar

- **Trocar o rerank para o Codex também?** O shim já existe; seria uma variável de ambiente. Custo: cada `qa` passa a fazer 1 chamada de rerank + 1 de geração na assinatura.
- **Rerank menor e local?** Um cross-encoder dedicado (ms-marco MiniLM) roda em CPU em milissegundos — mas é outro modelo para manter, e o `:1235` já mostrou que isso tem custo operacional.
- **Ou desligar por padrão** e ligar só quando a pergunta for difícil?
- O `--rerank N` restrito (pedir top-N em vez de ordenar 20) está no backlog como P2 e mudaria a conta.

## Answer

<!-- preencher no grilling -->
