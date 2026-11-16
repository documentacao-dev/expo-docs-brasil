import { ThemeProvider } from '@expo/styleguide';
import { MDXProvider } from '@mdx-js/react';
import { MotionConfig } from 'framer-motion';
import { AppProps } from 'next/app';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { useRouter } from 'next/router';
import { IntlProvider } from 'react-intl';

import { getLocaleFromPath, messages } from '~/common/i18n';
import { useNProgress } from '~/common/useNProgress';
import { DocumentationPageWrapper } from '~/components/DocumentationPageWrapper';
import { buildWebsiteSchema } from '~/constants/structured-data';
import { CodeBlockSettingsProvider } from '~/providers/CodeBlockSettingsProvider';
import { TutorialChapterCompletionProvider } from '~/providers/TutorialChapterCompletionProvider';
import { ApiDataProvider } from '~/providers/api-data';
import { HreflangAlternates } from '~/ui/components/HreflangAlternates';
import { markdownComponents } from '~/ui/components/Markdown';
import { CodeSelectionCopy } from '~/ui/components/Snippet/CodeSelectionCopy';
import { StructuredData } from '~/ui/components/StructuredData';
import * as Tooltip from '~/ui/components/Tooltip';
import '@expo/styleguide/dist/expo-theme.css';
import '@expo/styleguide-search-ui/dist/expo-search-ui.css';

import '~/styles/global.css';

export const regularFont = Inter({
  display: 'swap',
  subsets: ['latin'],
});
export const monospaceFont = JetBrains_Mono({
  display: 'swap',
  subsets: ['latin'],
});

const rootMarkdownComponents = {
  ...markdownComponents,
  wrapper: DocumentationPageWrapper,
};

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const locale = getLocaleFromPath(router.asPath);
  useNProgress();
  return (
    <>
      <StructuredData id="website" data={buildWebsiteSchema(locale)} />
      <HreflangAlternates />
      {/* oxlint-disable-next-line react/no-unknown-property */}
      <style jsx global>{`
        html,
        body,
        kbd,
        button,
        input,
        select,
        tspan,
        text {
          font-family: ${regularFont.style.fontFamily}, sans-serif;
        }
        code,
        pre,
        table.diff {
          font-family: ${monospaceFont.style.fontFamily}, monospace;
        }
      `}</style>
      <IntlProvider locale={locale} messages={messages[locale]} defaultLocale="en">
        <MotionConfig reducedMotion="user">
          <ThemeProvider>
            <TutorialChapterCompletionProvider>
              <CodeBlockSettingsProvider>
                <MDXProvider components={rootMarkdownComponents}>
                  <Tooltip.Provider>
                    <ApiDataProvider data={pageProps.apiSectionData}>
                      <Component {...pageProps} />
                    </ApiDataProvider>
                    <CodeSelectionCopy />
                  </Tooltip.Provider>
                </MDXProvider>
              </CodeBlockSettingsProvider>
            </TutorialChapterCompletionProvider>
          </ThemeProvider>
        </MotionConfig>
      </IntlProvider>
    </>
  );
}
