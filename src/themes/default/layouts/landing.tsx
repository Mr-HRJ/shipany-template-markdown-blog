import { ReactNode } from 'react';

import { getThemeBlock } from '@/core/theme';
import {
  Footer as FooterType,
  Header as HeaderType,
} from '@/shared/types/blocks/landing';

export default async function LandingLayout({
  children,
  header,
  footer,
}: {
  children: ReactNode;
  header: HeaderType;
  footer: FooterType;
}) {
  const Header = await getThemeBlock('header');
  const Footer = await getThemeBlock('footer');

  return (
    <div className="flex min-h-screen min-w-0 flex-col">
      <Header header={header} />
      <main id="main-content" className="min-w-0 flex-1">
        {children}
      </main>
      <Footer footer={footer} />
    </div>
  );
}
