import { useRouter } from 'next/compat/router';

import translationStatus from '~/public/static/constants/translation-status.json';
import { InlineHelp } from '~/ui/components/InlineHelp';
import { A } from '~/ui/components/Text';

const REPOSITORY_BLOB_URL =
  'https://github.com/documentacao-dev/expo-docs-brasil/blob/main/docs/pages';

const untranslatedPages: Record<string, string> = translationStatus.pages;

export function getUntranslatedSourceUrl(pathname: string): string | undefined {
  const file = untranslatedPages[pathname.replace(/\/$/, '') || '/'];
  return file ? `${REPOSITORY_BLOB_URL}/${file}` : undefined;
}

/**
 * Faixa no topo das páginas que ainda estão em inglês. A lista vem de
 * `scripts/translation-status.js`, gerada antes do build (páginas sem o marcador
 * o marcador `ia-translate: true` (comentário MDX) na última linha).
 */
export function TranslationNotice() {
  const router = useRouter();
  const sourceUrl = router?.pathname ? getUntranslatedSourceUrl(router.pathname) : undefined;

  if (!sourceUrl) {
    return null;
  }

  return (
    <InlineHelp type="default" size="sm" className="mb-5! inline-flex! w-full">
      Esta página ainda não foi traduzida e está em inglês. A tradução para português do Brasil está
      em andamento.{' '}
      <A openInNewTab href={sourceUrl}>
        ver no GitHub
      </A>
    </InlineHelp>
  );
}
