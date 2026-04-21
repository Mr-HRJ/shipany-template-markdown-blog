'use client';

import { TOCProvider } from 'fumadocs-ui/components/layout/toc';
import { CalendarIcon, ListIcon, ChevronLeftIcon, ChevronRightIcon, Menu, X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useState } from 'react';

import { ImageViewer, MarkdownPreview, TableOfContents } from '@/shared/blocks/common';
import { Crumb } from '@/shared/blocks/common/crumb';
import { type Post as PostType } from '@/shared/types/blocks/blog';
import { NavItem } from '@/shared/types/blocks/common';

import '@/config/style/mdnice.css';

// 移除Markdown语法的简单函数
function stripMarkdown(text: string): string {
  if (!text) return '';
  
  return text
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
    .trim();
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

  // Check if TOC should be shown
  const showToc = post.toc && post.toc.length > 0;

  // Check if Author info should be shown
  // const showAuthor = post.author_name || post.author_image || post.author_role;
  const showAuthor = false;
  
  // Calculate main content column span based on what sidebars are shown
  const getMainColSpan = () => {
    if (showToc && showAuthor) return 'lg:col-span-6';
    if (showToc || showAuthor) return 'lg:col-span-9';
    return 'lg:col-span-12';
  };

  return (
    <TOCProvider toc={post.toc || []}>
      <section id={post.id}>
        <div className="py-24 md:py-32">
          <div className="mx-auto w-full max-w-7xl px-6 md:px-8">
            <Crumb items={crumbItems} />

            {/* Header Section */}
            <div className="mt-16 text-center relative">
              {/* Mobile TOC Toggle Button */}
              {showToc && (
                <button
                  onClick={() => setIsTocOpen(!isTocOpen)}
                  className="md:hidden fixed bottom-4 right-4 z-50 p-2 rounded-lg bg-background border border-border shadow-lg"
                  aria-label="Toggle table of contents"
                >
                  {isTocOpen ? <X className="size-5" /> : <Menu className="size-5" />}
                </button>
              )}

              <h1 className="text-foreground mx-auto mb-4 w-full text-3xl font-bold md:max-w-4xl md:text-4xl">
                {post.title}
              </h1>
              <div className="text-muted-foreground text-md flex items-center justify-center gap-4">
                {post.created_at && (
                  <div className="text-muted-foreground text-md flex items-center justify-center gap-2">
                    <CalendarIcon className="size-4" /> {post.created_at}
                  </div>
                )}
              </div>
              
              {/* Description/Summary Section */}
              {post.description && (
                <div className="mx-auto mb-6 mt-2">
                  <div className="bg-muted/50 border-l-4 border-primary rounded-r-lg px-6 py-4 text-left">
                    <div className="flex items-start gap-3">
                      {/* <div className="flex-shrink-0 mt-1">
                        <svg className="size-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div> */}
                      <div className="flex-1">
                        {/* <h2 className="text-foreground font-semibold text-lg mb-2">摘要</h2> */}
                        <p className="text-muted-foreground text-base leading-relaxed">
                          {stripMarkdown(post.description)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 md:gap-8 md:mt-4 lg:grid-cols-12">
              {/* Table of Contents - Left Sidebar */}
              {showToc && (
                <div className="lg:col-span-3 h-full">
                  {/* Desktop TOC */}
                  <div className="sticky top-24 hidden md:block max-h-[calc(100vh-120px)]">
                    <div className="bg-muted/30 rounded-lg p-4 h-full flex flex-col">
                      <h2 className="text-foreground mb-4 flex items-center gap-2 font-semibold flex-shrink-0">
                        <ListIcon className="size-4" /> {t('toc')}
                      </h2>
                      <TableOfContents toc={post.toc || []} />
                    </div>
                  </div>

                  {/* Mobile TOC Drawer */}
                  {isTocOpen && (
                    <>
                      <div
                        className="md:hidden fixed inset-0 bg-black/50 z-40"
                        onClick={() => setIsTocOpen(false)}
                      />
                      <div className="md:hidden fixed top-0 right-0 bottom-0 w-80 max-w-[85vw] bg-background border-l border-border z-999 overflow-y-auto shadow-xl">
                        <div className="p-6">
                          <h2 className="text-foreground mb-4 flex items-center gap-2 font-semibold text-lg">
                            <ListIcon className="size-5" /> {t('toc')}
                          </h2>
                          <div onClick={() => setIsTocOpen(false)}>
                            <TableOfContents toc={post.toc || []} />
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Main Content - Center */}
              <div className={getMainColSpan()}>
                <article className="p-0">
                  <ImageViewer>
                    {post.body ? (
                      <div id="nice">
                        {post.body}
                      </div>
                    ) : (
                      post.content && (
                        <MarkdownPreview content={post.content} />
                      )
                    )}
                  </ImageViewer>
                </article>

                {/* Previous and Next Navigation */}
                {(prevPost || nextPost) && (
                  <div className="mt-16 border-t border-border pt-8">
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                      {/* Previous Post */}
                      {prevPost ? (
                        <Link
                          href={prevPost.url}
                          className="group flex flex-col gap-2 rounded-lg border border-border bg-muted/30 p-6 transition-all hover:border-primary hover:bg-muted/50"
                        >
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <ChevronLeftIcon className="size-4" />
                            <span>{t('prev_post')}</span>
                          </div>
                          <div className="text-foreground font-medium group-hover:text-primary transition-colors">
                            {prevPost.title}
                          </div>
                        </Link>
                      ) : (
                        <div></div>
                      )}

                      {/* Next Post */}
                      {nextPost && (
                        <Link
                          href={nextPost.url}
                          className="group flex flex-col gap-2 rounded-lg border border-border bg-muted/30 p-6 text-right transition-all hover:border-primary hover:bg-muted/50"
                        >
                          <div className="flex items-center justify-end gap-2 text-sm text-muted-foreground">
                            <span>{t('next_post')}</span>
                            <ChevronRightIcon className="size-4" />
                          </div>
                          <div className="text-foreground font-medium group-hover:text-primary transition-colors">
                            {nextPost.title}
                          </div>
                        </Link>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Author Info - Right Sidebar */}
              {showAuthor && (
                <div className="lg:col-span-3">
                  <div className="sticky top-24">
                    <div className="bg-muted/30 rounded-lg p-6">
                      <div className="text-center">
                        {post.author_image && (
                          <div className="ring-foreground/10 mx-auto mb-4 aspect-square size-20 overflow-hidden rounded-xl border border-transparent shadow-md ring-1 shadow-black/15">
                            <img
                              src={post.author_image}
                              alt={post.author_name}
                              className="h-full w-full object-cover"
                            />
                          </div>
                        )}
                        {post.author_name && (
                          <p className="text-foreground mb-1 text-lg font-semibold">
                            {post.author_name}
                          </p>
                        )}
                        {post.author_role && (
                          <p className="text-muted-foreground mb-4 text-sm">
                            {post.author_role}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </TOCProvider>
  );
}
