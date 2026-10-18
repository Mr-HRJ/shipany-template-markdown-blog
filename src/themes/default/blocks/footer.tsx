import { Link } from '@/core/i18n/navigation';
import {
  BrandLogo,
  BuiltWith,
  Copyright,
  LocaleSelector,
  ThemeToggler,
} from '@/shared/blocks/common';
import { SmartIcon } from '@/shared/blocks/common/smart-icon';
import { cn } from '@/shared/lib/utils';
import { Footer as FooterType } from '@/shared/types/blocks/landing';

const footerLinkClass =
  'text-muted-foreground hover:text-primary focus-visible:ring-ring w-fit rounded-sm text-sm leading-relaxed transition-colors focus-visible:ring-2 focus-visible:ring-offset-4 focus-visible:outline-none';

export function Footer({ footer }: { footer: FooterType }) {
  return (
    <footer
      id={footer.id}
      className={cn(
        'border-border/70 bg-card/50 border-t pt-12 pb-6 sm:pt-16',
        footer.className
      )}
    >
      <div className="container">
        <div className="grid min-w-0 gap-10 lg:grid-cols-12 lg:gap-16">
          <div className="min-w-0 space-y-4 lg:col-span-5">
            {footer.brand && <BrandLogo brand={footer.brand} />}
            {footer.brand?.description && (
              <p
                className="text-muted-foreground max-w-sm text-sm leading-7"
                dangerouslySetInnerHTML={{ __html: footer.brand.description }}
              />
            )}
            {footer.social && footer.social.items.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 pt-1">
                {footer.social.items.map((item, index) => (
                  <Link
                    key={item.url || index}
                    href={item.url || ''}
                    target={item.target || '_self'}
                    rel={
                      item.target === '_blank'
                        ? 'noopener noreferrer'
                        : undefined
                    }
                    className={cn(footerLinkClass, 'p-2')}
                    aria-label={item.title || 'Social media'}
                  >
                    {item.icon && (
                      <SmartIcon name={item.icon as string} size={18} />
                    )}
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div className="grid min-w-0 grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-7">
            {footer.nav?.items.map((item, index) => (
              <div key={item.title || index} className="min-w-0">
                <h2 className="mb-4 text-sm font-semibold">{item.title}</h2>
                <ul className="space-y-3">
                  {item.children?.map((child, childIndex) => (
                    <li key={child.url || childIndex}>
                      <Link
                        href={child.url || ''}
                        target={child.target || '_self'}
                        rel={
                          child.target === '_blank'
                            ? 'noopener noreferrer'
                            : undefined
                        }
                        className={footerLinkClass}
                      >
                        {child.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
        <div className="border-border/70 mt-10 flex flex-wrap items-center justify-between gap-5 border-t pt-6 sm:mt-12">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            {footer.copyright ? (
              <p
                className="text-muted-foreground text-xs leading-relaxed"
                dangerouslySetInnerHTML={{ __html: footer.copyright }}
              />
            ) : footer.brand ? (
              <Copyright brand={footer.brand} />
            ) : null}
            {footer.agreement?.items.map((item, index) => (
              <Link
                key={item.url || index}
                href={item.url || ''}
                target={item.target || '_self'}
                rel={
                  item.target === '_blank' ? 'noopener noreferrer' : undefined
                }
                className={cn(footerLinkClass, 'text-xs')}
              >
                {item.title}
              </Link>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {footer.show_built_with !== false && <BuiltWith />}
            {footer.show_theme !== false && <ThemeToggler type="toggle" />}
            {footer.show_locale !== false && <LocaleSelector type="button" />}
          </div>
        </div>
      </div>
    </footer>
  );
}
