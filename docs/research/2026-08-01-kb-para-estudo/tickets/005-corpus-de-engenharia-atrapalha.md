# Os 1.037 artigos de engenharia atrapalham o estudo de segurança?

Type: grilling
Status: open

## Question

O vault tem ~1.040 artigos, dos quais **15 são de cibersegurança**. O resto são capítulos de ~40 livros de engenharia de software (DDD, PropEr, Observability, Release It!, CLRS, Fluent Python).

Quando o usuário pergunta sobre Google Dorking, o retrieval procura em 1.040 artigos para achar 3 relevantes. A pergunta é se isso é problema real ou preocupação teórica.

### Pontos a fechar

- **É medível?** Rodar a mesma pergunta com o vault inteiro e com um subconjunto só de segurança, comparar a resposta. Se não muda, o problema não existe.
- **Se atrapalha**, a saída é filtro por `topic` no retrieval, vault separado, ou reagrupamento (ticket 006 do map anterior — hoje bloqueado)?
- **Vault separado tem custo**: `KB_DATA_DIR` é global; alternar exigiria perfis. A feature 010-multi-vault existe em draft e foi arquivada.
- **O corpus de engenharia tem valor para o estudo?** Segurança de API, autenticação, menor privilégio aparecem nos livros de engenharia — pode ser que o corpus ajude em vez de atrapalhar.

## Answer

<!-- preencher no grilling -->
