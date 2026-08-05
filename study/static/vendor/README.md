# Ativos de terceiros servidos localmente

O leitor é local e precisa funcionar sem rede. Estes arquivos vinham de CDN e passaram a ser servidos por `study/static/`.

| Arquivo | Versão | Origem | Licença |
|---|---|---|---|
| `htmx-2.0.4.min.js` | 2.0.4 | `unpkg.com/htmx.org@2.0.4/dist/htmx.min.js` | [BSD 2-Clause](https://github.com/bigskysoftware/htmx/blob/master/LICENSE) |
| `alpine-3.15.12.min.js` | 3.15.12 | `unpkg.com/alpinejs@3.15.12/dist/cdn.min.js` | [MIT](https://github.com/alpinejs/alpine/blob/main/LICENSE.md) |
| `press-start-2p-latin.woff2` | v16, subset latino | Google Fonts (`fonts.gstatic.com`) | [SIL Open Font License 1.1](https://openfontlicense.org/) |

`alpinejs@3.x.x` estava sem pin de versão: a mesma página podia carregar uma minor diferente a cada dia. Trocar de versão agora é substituir o arquivo e o `src` em `study/templates/base.html`.
