'use client';

import { useEffect, useState } from 'react';
import { Menu } from 'lucide-react';
import { useTranslations } from 'next-intl';

import { Link, usePathname } from '@/core/i18n/navigation';
import {
  BrandLogo,
  LocaleSelector,
  SignUser,
  SmartIcon,
  ThemeToggler,
} from '@/shared/blocks/common';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/shared/components/ui/accordion';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from '@/shared/components/ui/navigation-menu';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/components/ui/sheet';
import { useMedia } from '@/shared/hooks/use-media';
import { cn } from '@/shared/lib/utils';
import { NavItem } from '@/shared/types/blocks/common';
import { Header as HeaderType } from '@/shared/types/blocks/landing';

function isCurrentItem(item: NavItem, pathname: string): boolean {
  if (item.is_active) return true;
  if (!item.url || !item.url.startsWith('/')) return false;
  return item.url === '/'
    ? pathname === '/'
    : pathname === item.url || pathname.startsWith(`${item.url}/`);
}

function DesktopNavigation({
  items,
  pathname,
  label,
}: {
  items: NavItem[];
  pathname: string;
  label: string;
}) {
  return (
    <NavigationMenu
      viewport={false}
      aria-label={label}
      className="hidden lg:flex"
    >
      <NavigationMenuList className="gap-1">
        {items.map((item, index) => {
          const active = isCurrentItem(item, pathname);
          return (
            <NavigationMenuItem key={item.url || index}>
              {item.children?.length ? (
                <>
                  <NavigationMenuTrigger className="h-10 gap-2 px-4">
                    {item.icon && <SmartIcon name={item.icon as string} />}
                    {item.title}
                  </NavigationMenuTrigger>
                  <NavigationMenuContent className="min-w-64 p-2">
                    {item.children.map((child, childIndex) => (
                      <NavigationMenuLink key={child.url || childIndex} asChild>
                        <Link
                          href={child.url || ''}
                          target={child.target || '_self'}
                          rel={
                            child.target === '_blank'
                              ? 'noopener noreferrer'
                              : undefined
                          }
                          aria-current={
                            isCurrentItem(child, pathname) ? 'page' : undefined
                          }
                          className="flex-row items-start gap-3 p-3"
                        >
                          {child.icon && (
                            <SmartIcon name={child.icon as string} />
                          )}
                          <span>
                            <span className="block font-medium">
                              {child.title}
                            </span>
                            {child.description && (
                              <span className="text-muted-foreground mt-1 block text-xs leading-relaxed">
                                {child.description}
                              </span>
                            )}
                          </span>
                        </Link>
                      </NavigationMenuLink>
                    ))}
                  </NavigationMenuContent>
                </>
              ) : (
                <NavigationMenuLink asChild>
                  <Link
                    href={item.url || ''}
                    target={item.target || '_self'}
                    rel={
                      item.target === '_blank'
                        ? 'noopener noreferrer'
                        : undefined
                    }
                    aria-current={active ? 'page' : undefined}
                    className={cn(
                      'h-10 flex-row items-center gap-2 rounded-lg px-4 font-medium',
                      active
                        ? 'bg-brand text-brand-foreground hover:bg-brand/90 hover:text-brand-foreground'
                        : 'text-muted-foreground hover:bg-muted/70 hover:text-foreground'
                    )}
                  >
                    {item.icon && <SmartIcon name={item.icon as string} />}
                    {item.title}
                  </Link>
                </NavigationMenuLink>
              )}
            </NavigationMenuItem>
          );
        })}
      </NavigationMenuList>
    </NavigationMenu>
  );
}

function HeaderActions({ header }: { header: HeaderType }) {
  return (
    <div className="flex flex-wrap items-center gap-5">
      {header.buttons?.map((button, index) => (
        <Link
          key={button.url || index}
          href={button.url || ''}
          target={button.target || '_self'}
          rel={button.target === '_blank' ? 'noopener noreferrer' : undefined}
          className={cn(
            'focus-visible:ring-ring inline-flex min-h-9 items-center justify-center gap-2 rounded-lg px-4 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none',
            button.variant === 'outline'
              ? 'bg-background hover:bg-muted border'
              : 'bg-brand text-brand-foreground hover:bg-brand/90'
          )}
        >
          {button.icon && (
            <SmartIcon name={button.icon as string} className="size-4" />
          )}
          {button.title}
        </Link>
      ))}
      {header.show_theme && <ThemeToggler />}
      {header.show_locale && <LocaleSelector />}
      {header.show_sign && <SignUser userNav={header.user_nav} />}
    </div>
  );
}

export function Header({ header }: { header: HeaderType }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const isLarge = useMedia('(min-width: 64rem)');
  const t = useTranslations('landing.header');

  useEffect(() => {
    const media = window.matchMedia('(min-width: 64rem)');
    const closeOnDesktop = () => {
      if (media.matches) setIsMobileMenuOpen(false);
    };
    media.addEventListener('change', closeOnDesktop);
    return () => media.removeEventListener('change', closeOnDesktop);
  }, []);

  return (
    <header
      id={header.id}
      className={cn(
        'border-border/70 bg-background/95 fixed inset-x-0 top-0 z-50 border-b backdrop-blur-md',
        header.className
      )}
    >
      <a
        href="#main-content"
        className="bg-primary text-primary-foreground sr-only rounded-lg px-4 py-3 font-medium focus:not-sr-only focus:absolute focus:top-2 focus:left-4 focus:z-[60]"
      >
        {t('skip_content')}
      </a>
      <div className="container flex h-16 items-center justify-between gap-6 lg:h-18">
        <div className="flex min-w-0 items-center gap-10">
          {header.brand && <BrandLogo brand={header.brand} />}
          <DesktopNavigation
            items={header.nav?.items || []}
            pathname={pathname}
            label={t('menu_title')}
          />
        </div>
        <div className="hidden lg:block">
          {isLarge && <HeaderActions header={header} />}
        </div>
        <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
          <SheetTrigger asChild>
            <button
              type="button"
              className="focus-visible:ring-ring bg-card flex size-10 shrink-0 items-center justify-center rounded-lg border focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none lg:hidden"
              aria-label={t('open_menu')}
            >
              <Menu className="size-5" aria-hidden="true" />
            </button>
          </SheetTrigger>
          <SheetContent
            className="w-[min(88vw,360px)] overflow-y-auto px-6 pb-8 motion-reduce:animate-none"
            onClick={(event) => {
              if (
                event.target instanceof Element &&
                event.target.closest('a[href]')
              ) {
                setIsMobileMenuOpen(false);
              }
            }}
          >
            <SheetHeader className="px-0 pt-8 pb-5">
              <SheetTitle>{t('menu_title')}</SheetTitle>
              <SheetDescription>{t('menu_description')}</SheetDescription>
            </SheetHeader>
            <nav aria-label={t('menu_title')}>
              <Accordion type="single" collapsible className="space-y-2">
                {header.nav?.items?.map((item, index) => {
                  const active = isCurrentItem(item, pathname);
                  return item.children?.length ? (
                    <AccordionItem
                      key={item.url || index}
                      value={`${index}`}
                      className="border-none"
                    >
                      <AccordionTrigger className="px-4 py-3 text-base hover:no-underline">
                        {item.title}
                      </AccordionTrigger>
                      <AccordionContent className="space-y-1 pb-2">
                        {item.children.map((child, childIndex) => (
                          <Link
                            key={child.url || childIndex}
                            href={child.url || ''}
                            target={child.target || '_self'}
                            rel={
                              child.target === '_blank'
                                ? 'noopener noreferrer'
                                : undefined
                            }
                            aria-current={
                              isCurrentItem(child, pathname)
                                ? 'page'
                                : undefined
                            }
                            className="focus-visible:ring-ring hover:bg-muted block rounded-lg px-6 py-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
                          >
                            {child.title}
                          </Link>
                        ))}
                      </AccordionContent>
                    </AccordionItem>
                  ) : (
                    <Link
                      key={item.url || index}
                      href={item.url || ''}
                      target={item.target || '_self'}
                      rel={
                        item.target === '_blank'
                          ? 'noopener noreferrer'
                          : undefined
                      }
                      aria-current={active ? 'page' : undefined}
                      className={cn(
                        'focus-visible:ring-ring flex items-center gap-3 rounded-lg px-4 py-3 text-base font-medium focus-visible:ring-2 focus-visible:outline-none',
                        active
                          ? 'bg-brand text-brand-foreground'
                          : 'hover:bg-muted'
                      )}
                    >
                      {item.icon && (
                        <SmartIcon
                          name={item.icon as string}
                          className="size-5"
                        />
                      )}
                      {item.title}
                    </Link>
                  );
                })}
              </Accordion>
            </nav>
            <div className="mt-6 border-t pt-6">
              {!isLarge && <HeaderActions header={header} />}
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
