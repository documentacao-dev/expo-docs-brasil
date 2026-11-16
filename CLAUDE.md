# CLAUDE.md

Tradução PT-BR da documentação do **Expo**, fork de `expo/expo` (só `docs/`), parte da org [`documentacao-dev`](https://github.com/documentacao-dev). Original: https://docs.expo.dev. Publicado no site Firebase `expo-documentacao` (projeto `transliteradu`).

- Conteúdo traduzível: `docs/pages/**/*.mdx`, traduzido no lugar, **fora** de `docs/pages/ja/` (tradução japonesa do upstream) e `docs/pages/versions/` (referência da SDK, por enquanto em inglês). Interface do site: `docs/messages/en.json` (já em português; o inglês original, só para testes, está em `docs/__mocks__/messages.en.json`).
- Site: Next.js (`output: 'export'`). Build em `docs/`: `pnpm export` gera `docs/out/` (~1 GB, vários minutos). O projeto exige pnpm 12.2.1 e Node 24. O `export-prep` grava `modificationDate` nos .mdx: depois de cada build rode `git checkout -- docs/pages` (nunca commite isso). Typecheck: `pnpm exec tsc --noEmit` em `docs/`. Testes: `pnpm test` em `docs/`.
- Sync: branch `sync/upstream-AAAA-MM` com merge de `upstream/main` (`expo/expo`), retradução só do que mudou, atualização de `tool/traducao/ultimo-sync-upstream.txt`.
- O fork usa sparse checkout (`docs/` e `packages/@expo/sdk-compatibility`). Arquivos fora disso (`tool/`, `.github/`, `.claude/`) entram com `git add --sparse`.

## Modelo da tradução: sempre Haiku

Toda tradução e retradução de página (tradução nova, sync com o upstream, revisão de trecho) roda no **Haiku** (`model: haiku`), local ou na nuvem (Claude Code na web, GitHub App, rotinas agendadas).

- O agente `.claude/agents/traduzir-pt-br.md` já declara `model: haiku`. Não troque.
- Se um orquestrador disparar subagentes para traduzir, passe `model: "haiku"` na ferramenta Agent.
- O modelo principal da sessão fica só com a orquestração: merge do upstream, scripts de conferência, commits e PR. Ele não traduz páginas.
- Revisão de tradução: subagente de contexto limpo que lê 100% do texto lado a lado e declara `COBERTURA`; lote grande num revisor só vira amostragem.

## Convenções das páginas (MDX)

- **Marcador de página traduzida:** a **última linha** do .mdx é `{/* ia-translate: true */}`. Sem ele a página é tratada como inglesa e o site mostra a faixa "ainda não foi traduzida".
- Frontmatter: traduza `title`, `description` e `sidebar_title`; as outras chaves ficam idênticas.
- Blocos de código (inclusive comentários e saídas), linhas `import`, props de componentes JSX (`<Terminal cmd={...} />`), URLs, comentários `{/* */}` e código inline ficam idênticos ao inglês. Dos atributos de texto visível dos componentes (`title`, `description`, `label`, `sidebar_title`, `summary`, `header`, `alt`, `caption`) só o texto entre aspas pode mudar.
- Callouts `> **info**`, `> **warning**`, `> **tip**`: a palavra-chave em inglês fica; traduza o resto.
- Links e âncoras iguais ao original. Cuidado: o slug de um título vem do texto dele (`rehype-slug`), então links internos `#ancora` para um título traduzido quebram; mantenha o link como está e avise o orquestrador quando acontecer (ainda não há `{#id}` explícito nos títulos).
- `python3 tool/traducao/verificar.py` confere cada página com marcador contra o inglês do commit em `tool/traducao/ultimo-sync-upstream.txt` (via `git show`) e falha o deploy se houver erro. Aviso (`AVISO`) não bloqueia.

## Política de termos

Ficam em inglês: Expo, EAS, Expo Go, Expo Router, development build, build, deploy, app config, config plugin, prebuild, native module, bundle, bundler, Metro, hot reload, Fast Refresh, component, hook, props, state, template, workflow, update, OTA, CLI, SDK, store, push notification, splash screen, layout, debug, release, commit, branch, merge, script, token, endpoint, callback, framework, plugin, package.

Traduza: app = app, developer = dev ou desenvolvedor, getting started = Primeiros passos, learn more = Saiba mais, see also = Veja também. Títulos em português com só a primeira palavra maiúscula. Tom direto ("você"), sem travessão onde o português usaria vírgula.

## Sem rastreamento

O site traduzido não manda dados para a Expo: foram removidos Sentry, Google Analytics, banner de consentimento (DataGrail), pixel Cometly, votação da página, newsletter e o formulário de feedback (que posta em `api.expo.dev`; agora o link "Envie seu feedback" abre uma issue neste repositório). Não reintroduza nenhum desses. Pendentes de revisão: widget "Ask AI" (AskPageAI) e a busca, que podem chamar APIs da Expo.

## Aviso de página em inglês e rodapé

- `docs/scripts/translation-status.js` lista as páginas sem marcador; `generate-static-resources` grava `docs/public/static/constants/translation-status.json` (roda no `pnpm export`, no `postinstall` e no `pnpm test`). `docs/ui/components/TranslationNotice` mostra a faixa no topo das páginas em inglês, com link "ver no GitHub". Não aparece em `/ja` nem em `/versions`.
- O rodapé (`docs/ui/components/Footer/Footer.tsx`) traz a atribuição: tradução comunitária, MIT, original em docs.expo.dev, parte do documentacao.dev.

## Export reduzido

O `next build` exporta todas as versões da SDK (~1,1 GB; o `exportPathMap` do upstream não filtra mais nada no Next 16). No deploy, `pnpm prune-export-versions` (`docs/scripts/prune-export-versions.js`) apaga de `docs/out/versions/` o `unversioned` e as versões antigas, e ficam `latest` e a mais nova (~550 MB). Links para versões podadas caem no 404.
