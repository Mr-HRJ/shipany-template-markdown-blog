'use client';

import { useState } from 'react';
import Link from 'next/link';
import { TOCProvider } from 'fumadocs-ui/components/layout/toc';
import {
  CalendarIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ListIcon,
} from 'lucide-react';
import { useTranslations } from 'next-intl';

import { Crumb } from '@/shared/blocks/common/crumb';
import { ImageViewer } from '@/shared/blocks/common/image-viewer';
import { MarkdownPreview } from '@/shared/blocks/common/markdown-preview';
import { TableOfContents } from '@/shared/blocks/common/table-of-contents';
import { Button } from '@/shared/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/components/ui/sheet';
import { type Post as PostType } from '@/shared/types/blocks/blog';
import { NavItem } from '@/shared/types/blocks/common';

import '@/config/style/reading.css';

// 移除Markdown语法的简单函数
function stripMarkdown(text: string): string {
  if (!text) return '';

  return (
    text
      // 移除标题标记
      .replace(/^#{1,6}\s+/gm, '')
      // 移除粗体和斜体
      .replace(/(\*\*|__)(.*?)\1/g, '$2')
      .replace(/(\*|_)(.*?)\1/g, '$2')
      // 移除链接，保留文本
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // 移除图片
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
      // 移除行内代码
      .replace(/`([^`]+)`/g, '$1')
      // 移除代码块
      .replace(/```[\s\S]*?```/g, '')
      // 移除引用
      .replace(/^>\s+/gm, '')
      // 移除列表标记
      .replace(/^[\*\-\+]\s+/gm, '')
      .replace(/^\d+\.\s+/gm, '')
      // 移除水平线
      .replace(/^[\*\-_]{3,}$/gm, '')
      // 移除多余空白
      .replace(/\n{2,}/g, '\n')
      .trim()
  );
}

export function BlogDetail({
  post,
  prevPost,
  nextPost,
}: {
  post: PostType;
  prevPost: { title: string; url: string } | null;
  nextPost: { title: string; url: string } | null;
}) {
  const t = useTranslations('blog.page');
  const [isTocOpen, setIsTocOpen] = useState(false);
  const showToc = Boolean(post.toc?.length);

  const crumbItems: NavItem[] = [
    {
      title: t('crumb'),
      url: '/blog',
      icon: 'Newspaper',
      is_active: false,
    },
    {
      title: post.title || '',
      url: `/blog/${post.slug}`,
      is_active: true,
    },
  ];

  return (
    <TOCProvider toc={post.toc || []}>
      <section
        id={post.id}
        className="reading-page pt-24 pb-24 md:pt-32 md:pb-32"
      >
        <div className="mx-auto w-full max-w-6xl px-5 md:px-8">
          <div className="mb-10 min-w-0 overflow-hidden md:mb-14 [&_nav]:px-0">
            <Crumb items={crumbItems} />
          </div>

          <div
            className={
              showToc
                ? 'grid items-start gap-12 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-16'
                : ''
            }
          >
            {showToc && (
              <aside
                className="sticky top-28 hidden min-w-0 lg:block"
                aria-label={t('toc')}
              >
                <h2 className="text-foreground mb-5 flex items-center gap-2 text-sm font-semibold">
                  <ListIcon
                    className="text-muted-foreground size-4"
                    aria-hidden="true"
                  />
                  {t('toc')}
                </h2>
                <TableOfContents toc={post.toc || []} className="pr-3" />
              </aside>
            )}

            <div className="mx-auto w-full max-w-[70ch] min-w-0">
              <header className="border-border mb-10 border-b pb-10 md:mb-12 md:pb-12">
                <h1 className="text-foreground font-serif text-3xl leading-snug font-semibold tracking-tight text-balance md:text-4xl lg:text-[2.75rem]">
                  {post.title}
                </h1>
                {post.created_at && (
                  <div className="text-muted-foreground mt-5 flex items-center gap-2 text-sm">
                    <CalendarIcon className="size-4" aria-hidden="true" />
                    <span>{post.created_at}</span>
                  </div>
                )}
                {post.description && (
                  <p className="text-muted-foreground mt-6 text-base leading-8 md:text-lg">
                    {stripMarkdown(post.description)}
                  </p>
                )}
              </header>

              <article className="reading-content min-w-0">
                <ImageViewer>
                  {post.body ? (
                    <div id="nice">{post.body}</div>
                  ) : (
                    post.content && <MarkdownPreview content={post.content} />
                  )}
                </ImageViewer>
              </article>

              {(prevPost || nextPost) && (
                <nav
                  className="border-border mt-16 grid grid-cols-1 gap-6 border-t pt-8 sm:grid-cols-2"
                  aria-label={`${t('prev_post')} / ${t('next_post')}`}
                >
                  {prevPost ? (
                    <Link
                      href={prevPost.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group focus-visible:outline-ring rounded-md py-2 focus-visible:outline-2 focus-visible:outline-offset-4"
                    >
                      <span className="text-muted-foreground mb-3 flex items-center gap-2 text-sm">
                        <ChevronLeftIcon
                          className="size-4"
                          aria-hidden="true"
                        />
                        {t('prev_post')}
                      </span>
                      <span className="text-foreground group-hover:text-primary leading-7 font-medium transition-colors">
                        {prevPost.title}
                      </span>
                    </Link>
                  ) : (
                    <div className="hidden sm:block" />
                  )}
                  {nextPost && (
                    <Link
                      href={nextPost.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group focus-visible:outline-ring rounded-md py-2 focus-visible:outline-2 focus-visible:outline-offset-4 sm:text-right"
                    >
                      <span className="text-muted-foreground mb-3 flex items-center gap-2 text-sm sm:justify-end">
                        {t('next_post')}
                        <ChevronRightIcon
                          className="size-4"
                          aria-hidden="true"
                        />
                      </span>
                      <span className="text-foreground group-hover:text-primary leading-7 font-medium transition-colors">
                        {nextPost.title}
                      </span>
                    </Link>
                  )}
                </nav>
              )}
            </div>
          </div>
        </div>

        {showToc && (
          <Sheet open={isTocOpen} onOpenChange={setIsTocOpen}>
            <SheetTrigger asChild>
              <Button
                variant="outline"
                className="bg-card fixed right-5 bottom-5 z-40 h-11 gap-2 rounded-full px-4 shadow-sm lg:hidden"
              >
                <ListIcon className="size-4" aria-hidden="true" />
                {t('toc')}
              </Button>
            </SheetTrigger>
            <SheetContent
              side="right"
              className="w-[min(22rem,90vw)] overflow-y-auto px-6 py-8"
              aria-describedby={undefined}
            >
              <SheetHeader className="px-0 pt-0 pb-3">
                <SheetTitle className="flex items-center gap-2 text-lg">
                  <ListIcon className="size-4" aria-hidden="true" />
                  {t('toc')}
                </SheetTitle>
              </SheetHeader>
              <div
                onClick={(event) => {
                  if (
                    event.target instanceof Element &&
                    event.target.closest('a')
                  ) {
                    setIsTocOpen(false);
                  }
                }}
              >
                <TableOfContents
                  toc={post.toc || []}
                  className="max-h-[calc(100dvh-8rem)]"
                />
              </div>
            </SheetContent>
          </Sheet>
        )}
      </section>
    </TOCProvider>
  );
}
