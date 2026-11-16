import { DiscordIcon } from '@expo/styleguide-icons/custom/DiscordIcon';
import { GithubIcon } from '@expo/styleguide-icons/custom/GithubIcon';
import { Edit05Icon } from '@expo/styleguide-icons/outline/Edit05Icon';
import { File02Icon } from '@expo/styleguide-icons/outline/File02Icon';
import { MessageTextSquare02Icon } from '@expo/styleguide-icons/outline/MessageTextSquare02Icon';
import type { ReactNode } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { A, CALLOUT, LI } from '../Text';
import { githubUrl } from './utils';

const LINK_CLASSES = 'inline-flex items-center mb-1 focus-visible:outline-offset-4';
const ICON_CLASSES = 'flex items-center mr-2.5 text-icon-secondary shrink-0';

export const IssuesLink = ({ title, repositoryUrl }: { title: string; repositoryUrl?: string }) => (
  <LI>
    <A
      isStyled
      openInNewTab
      href={
        repositoryUrl ? `${repositoryUrl}/issues` : `https://github.com/expo/expo/labels/${title}`
      }
      className={LINK_CLASSES}>
      <GithubIcon aria-hidden="true" className={ICON_CLASSES} />
      <CALLOUT theme="secondary">View open bug reports for {title}</CALLOUT>
    </A>
  </LI>
);

export const ForumsLink = ({ isAPIPage, title }: { isAPIPage: boolean; title: string }) => {
  const intl = useIntl();
  return isAPIPage ? (
    <LI>
      <A isStyled openInNewTab href="https://chat.expo.dev/" className={LINK_CLASSES}>
        <DiscordIcon aria-hidden="true" className={ICON_CLASSES} />
        <CALLOUT theme="secondary">Ask a question on the forums about {title}</CALLOUT>
      </A>
    </LI>
  ) : (
    <LI>
      <A
        isStyled
        openInNewTab
        href="https://chat.expo.dev/"
        className={LINK_CLASSES}
        shouldLeakReferrer>
        <DiscordIcon aria-hidden="true" className={ICON_CLASSES} />
        <CALLOUT theme="secondary">{intl.formatMessage({ id: 'footerAskOnForums' })}</CALLOUT>
      </A>
    </LI>
  );
};

export const EditPageLink = ({ pathname }: { pathname: string }) => {
  const intl = useIntl();
  return (
    <LI>
      <A isStyled openInNewTab href={githubUrl(pathname)} className={LINK_CLASSES}>
        <Edit05Icon aria-hidden="true" className={ICON_CLASSES} />
        <CALLOUT theme="secondary">{intl.formatMessage({ id: 'footerEditPage' })}</CALLOUT>
      </A>
    </LI>
  );
};

export const LlmsTxtLink = () => (
  <LI className="flex items-center">
    <File02Icon aria-hidden="true" className={ICON_CLASSES} />
    <CALLOUT theme="secondary" tag="span">
      <FormattedMessage
        id="footerLlmsView"
        values={{
          llmsLink: (chunks: ReactNode) => (
            <A openInNewTab href="/llms.txt" className="focus-visible:outline-offset-4">
              {chunks}
            </A>
          ),
        }}
      />
    </CALLOUT>
  </LI>
);

// O formulário de feedback original envia dados para a API da Expo; na tradução, o feedback vai
// para as issues do repositório da tradução.
export const ShareFeedbackLink = ({ pathname }: { pathname?: string }) => {
  const intl = useIntl();
  const issueUrl = new URL('https://github.com/documentacao-dev/expo-docs-brasil/issues/new');
  if (pathname) {
    issueUrl.searchParams.set('title', `Feedback sobre ${pathname}`);
  }
  return (
    <LI>
      <A isStyled openInNewTab href={issueUrl.toString()} className={LINK_CLASSES}>
        <MessageTextSquare02Icon aria-hidden="true" className={ICON_CLASSES} />
        <CALLOUT theme="secondary">{intl.formatMessage({ id: 'footerShareFeedback' })}</CALLOUT>
      </A>
    </LI>
  );
};
