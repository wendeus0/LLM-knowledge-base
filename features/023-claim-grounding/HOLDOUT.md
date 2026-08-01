# HOLDOUT — 023-claim-grounding

**Congelado em:** 2026-08-01
**Pares:** 12 · **Domínios:** 6 (cybersecurity ×4, banco-de-dados ×2, algoritmos ×2, python ×2, redes ×1, arquitetura-de-software ×1)

O manifest com caminhos, trechos e afirmações vive em `.holdout/manifest.json` — **privado e gitignored**, para que quem ajusta parâmetros não veja os casos de aceite (protocolo do `EVALS.md`). Este arquivo registra apenas os hashes dos pares e as contagens, provando o congelamento sem expor o conteúdo.

## Regras do congelamento

- Nenhum destes pares pode ser usado para escolher janela, limiar ou exemplo público.
- O split é por par: todas as afirmações e mutações derivadas de um par ficam do mesmo lado.
- Não mover pares depois de ver pontuações. Recalibração posterior exige holdout novo.
- Os 8 casamentos automáticos via frontmatter `source` → `_sources/` estão **excluídos por classe** (contaminados: calibraram os limiares atuais). A curadoria evitou 288 casamentos diretos dessa classe.
- Todos os 12 `trecho_fonte` foram validados por substring match byte a byte contra a fonte.

## Ressalva declarada

Os artigos são compilações em português de fontes em inglês — o vínculo afirmação↔trecho é **cross-língue** (PT→EN). O mDeBERTa é multilíngue e o XNLI cobre o par, mas o efeito não foi medido separadamente: a primeira rodada do holdout deve reportar a taxa cross-língue à parte antes de compará-la com a linha de base monolíngue.

## Pares congelados (hash SHA-256 truncado de `artigo|fonte`)

| Hash | Domínio | Método de confirmação |
|---|---|---|
| `8c8e0b66e3f8eed3` | algoritmos | nome de capitulo identico (Part I Foundations, CLRS 4a ed.)  |
| `654aa0851c8a9efc` | algoritmos | nome de capitulo identico (Part VI Graph Algorithms, CLRS 4a |
| `36ee0825200def10` | banco-de-dados | frontmatter source (05-chapter-2-the-where-clause.md) locali |
| `1835b570ded60e06` | cybersecurity | frontmatter source (44-30-request-authentication.md) localiz |
| `b140af957ec448de` | cybersecurity | titulo do capitulo identico ao frontmatter source (103-the-o |
| `7d8fe4c8dcd96eee` | cybersecurity | titulo identico + leitura integral dos dois arquivos (artigo |
| `6380a35e9ba21637` | cybersecurity | URL: frontmatter source do artigo == source_url do arquivo r |
| `d074adbf6b93ef81` | redes | titulo identico (Network Routing) + leitura do trecho sobre  |
| `4439baa46c46da79` | banco-de-dados | frontmatter source (05-part-i-storage-engines.md) localizado |
| `ee3bf247c3874ae6` | arquitetura-de-software | frontmatter source (10-7-aggregates-and-consistency-boundari |
| `d9b7e15a003c3dac` | python | frontmatter source (26-chapter-17-...) localizado em library |
| `19660008534edea6` | python | frontmatter source (03-chapter-8-boolean-logic.md) localizad |

## Próximo uso

Rodada única conforme `EVALS.md` § "Reajuste sem contaminar a validação": configuração congelada no desenvolvimento → uma execução no holdout → publicar taxas, denominadores e hashes. Resultado pior que o teto contaminado (5/6, 12/12, 72%) é resultado válido, não falha do processo.
