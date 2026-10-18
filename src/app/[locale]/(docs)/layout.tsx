import type { ReactNode } from 'react';
import type { Translations } from 'fumadocs-ui/i18n';
import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import { RootProvider } from 'fumadocs-ui/provider';

import { source } from '@/core/docs/source';

import { baseOptions } from './layout.config';

import '@/config/style/docs.css';

const zh: Partial<Translations> = {
  search: '搜索手册',
  searchNoResult: '没有找到相关内容',
  toc: '本页目录',
  tocNoHeadings: '本页暂无章节标题',
  lastUpdate: '更新于',
  chooseLanguage: '选择语言',
  nextPage: '下一篇',
  previousPage: '上一篇',
  chooseTheme: '切换主题',
  editOnGithub: '在 GitHub 上编辑',
};
// available languages that will be displayed on UI
// make sure `locale` is consistent with your i18n config
const locales = [
  {
    name: 'English',
    locale: 'en',
  },
  {
    name: '简体中文',
    locale: 'zh',
  },
];

export default async function DocsRootLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale?: string }>;
}) {
  const { locale } = await params;
  const lang = locale || 'en';
  const options = baseOptions(lang);

  return (
    <RootProvider
      i18n={{
        locale: lang,
        locales,
        translations: { zh }[lang],
      }}
      search={{
        options: {
          api: '/api/docs/search',
        },
      }}
    >
      <DocsLayout
        {...options}
        tree={source.pageTree[lang]}
        nav={{ ...options.nav, mode: 'top' }}
        tabMode="sidebar"
        containerProps={{ className: 'docs-shell' }}
      >
        {children}
      </DocsLayout>
    </RootProvider>
  );
}
