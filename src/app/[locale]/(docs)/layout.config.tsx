import Image from 'next/image';
import { DynamicAppName } from '@/components/docs/dynamic-app-name';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

import { i18n } from '@/core/docs/source';
import { envConfigs } from '@/config';
import { defaultLocale } from '@/config/locale';

export function baseOptions(locale: string): BaseLayoutProps {
  const prefix = locale === defaultLocale ? '' : `/${locale}`;

  return {
    links: [
      {
        text: locale === 'zh' ? '首页' : 'Home',
        url: prefix || '/',
      },
      {
        text: locale === 'zh' ? '博客' : 'Blog',
        url: `${prefix}/blog`,
      },
    ],
    nav: {
      url: prefix || '/',
      title: (
        <>
          <Image
            src={envConfigs.app_logo}
            alt=""
            width={32}
            height={32}
            className="docs-brand-logo"
          />
          <span className="docs-brand-title">
            <DynamicAppName fallback={envConfigs.app_name} />
          </span>
        </>
      ),
    },
    i18n,
  };
}
