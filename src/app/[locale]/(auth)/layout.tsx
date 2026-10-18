import { envConfigs } from '@/config';
import {
  BrandLogo,
  LocaleSelector,
  ThemeToggler,
} from '@/shared/blocks/common';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="bg-background flex min-h-dvh w-full flex-col">
      <header className="border-border/70 bg-card/70 border-b">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-5 md:h-[72px] md:px-8">
          <BrandLogo
            brand={{
              title: envConfigs.app_name,
              logo: { src: envConfigs.app_logo, alt: envConfigs.app_name },
              url: '/',
              target: '_self',
              className:
                'min-w-0 [&>span]:truncate [&>span]:text-sm [&>span]:font-semibold md:[&>span]:text-base [&>img]:shrink-0',
            }}
          />
          <div className="flex shrink-0 items-center gap-1 md:gap-2">
            <ThemeToggler />
            <LocaleSelector type="button" />
          </div>
        </div>
      </header>
      <main className="grid flex-1 place-items-center px-5 py-12 md:py-20">
        <div className="[&_[data-slot=card]]:border-border/80 w-full max-w-md [&_[data-slot=card-header]]:gap-3 [&_[data-slot=card-title]]:font-serif [&_[data-slot=card]]:rounded-2xl [&_[data-slot=card]]:py-8 [&_[data-slot=card]]:shadow-none [&_button[type=submit]]:h-11 [&_h1]:text-3xl [&_h1]:font-semibold [&_input]:h-11 [&>div.h-screen]:h-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
