import DocumentationPage from '~/components/DocumentationPage';
import { AppJSBanner } from '~/ui/components/AppJSBanner';
import { DevicesImageMasks } from '~/ui/components/Home/resources';
import {
  QuickStart,
  CommandLineTools,
  DiscoverMore,
  ExploreAPIs,
  Talks,
  JoinTheCommunity,
} from '~/ui/components/Home/sections';
import { ExploreExamples } from '~/ui/components/Home/sections/ExploreExamples';

function Home() {
  return (
    <DocumentationPage
      hideTOC
      hideFromSearch
      description="Build one JavaScript/TypeScript project that runs natively on all your users' devices.">
      <div className="h-0">
        <DevicesImageMasks />
      </div>
      <AppJSBanner />
      <section data-home-section="quick-start">
        <QuickStart />
      </section>
      <section data-home-section="command-line-tools">
        <CommandLineTools />
      </section>
      <section data-home-section="discover-more">
        <DiscoverMore />
      </section>
      <section data-home-section="explore-apis">
        <ExploreAPIs />
      </section>
      <section data-home-section="explore-examples">
        <ExploreExamples />
      </section>
      <section data-home-section="talks">
        <Talks />
      </section>
      <section data-home-section="join-the-community">
        <JoinTheCommunity />
      </section>
    </DocumentationPage>
  );
}

export default Home;
