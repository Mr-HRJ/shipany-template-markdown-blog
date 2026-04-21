'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@radix-ui/react-avatar';
import { Calendar, Grid, List, Loader2, Search, X, Menu } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { Link } from '@/core/i18n/navigation';
import { cn } from '@/shared/lib/utils';
import {
  Blog as BlogType,
  Category as CategoryType,
  Post as PostType,
} from '@/shared/types/blocks/blog';

// 扩展 PostType 以包含新字段
interface ExtendedPostType extends PostType {
  isPinned?: boolean;
  isRecommended?: boolean;
}

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

// Check if a post is published within the last 3 days
function isNewPost(createdAt: string): boolean {
  if (!createdAt) return false;
  
  try {
    const postDate = new Date(createdAt);
    const now = new Date();
    const diffTime = now.getTime() - postDate.getTime();
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    
    return diffDays <= 3;
  } catch {
    return false;
  }
}

export function Blog({
  className,
  ...props
}: {
  className?: string;
  blog?: BlogType;
  section?: any;
  [key: string]: any;
}) {
  const blog: BlogType = props.blog || ({
    ...props,
    ...(props.section || {}),
  } as BlogType);
  const t = useTranslations('blog.page');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list'); // 默认列表模式
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [displayedPosts, setDisplayedPosts] = useState<ExtendedPostType[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);
  
  const POSTS_PER_PAGE = 12;

  // 当搜索查询改变时,更新 URL 参数并触发服务端搜索
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    
    // 使用 setTimeout 进行防抖
    const timeoutId = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      if (value.trim()) {
        params.set('search', value.trim());
      } else {
        params.delete('search');
      }
      // 重置页码
      params.delete('page');
      
      router.push(`?${params.toString()}`);
    }, 500); // 500ms 防抖

    return () => clearTimeout(timeoutId);
  };

  // 加载更多文章
  const loadMore = useCallback(() => {
    if (isLoading || !hasMore) return;
    
    setIsLoading(true);
    
    // 模拟异步加载
    setTimeout(() => {
      const startIndex = (page - 1) * POSTS_PER_PAGE;
      const endIndex = startIndex + POSTS_PER_PAGE;
      const newPosts = (blog.posts || []).slice(startIndex, endIndex);
      
      if (newPosts.length > 0) {
        setDisplayedPosts((prev) => [...prev, ...newPosts]);
        setPage((prev) => prev + 1);
        setHasMore(endIndex < (blog.posts || []).length);
      } else {
        setHasMore(false);
      }
      
      setIsLoading(false);
    }, 300);
  }, [page, blog.posts, isLoading, hasMore]);

  // 初始加载
  useEffect(() => {
    setDisplayedPosts([]);
    setPage(1);
    setHasMore(true);
  }, [blog.posts]);

  useEffect(() => {
    if (displayedPosts.length === 0 && (blog.posts || []).length > 0) {
      loadMore();
    }
  }, [displayedPosts, blog.posts, loadMore]);

  // Intersection Observer 用于滚动加载
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [hasMore, isLoading, loadMore]);

  return (
    <section
      id={blog.id}
      className={cn('py-18 md:py-20', blog.className, className)}
    >
      <div className="container">
        {/* 移动端分类菜单按钮 */}
        <button
          onClick={() => setIsCategoryOpen(!isCategoryOpen)}
          className="md:hidden absolute top-2 right-4 z-50 p-2 rounded-lg bg-background border border-border shadow-lg"
          aria-label="Toggle categories"
        >
          <Menu className="size-6" />
        </button>

        {/* 移动端分类抽屉 */}
        {isCategoryOpen && (
          <>
            <div
              className="md:hidden fixed inset-0 bg-black/50 z-40"
              onClick={() => setIsCategoryOpen(false)}
            />
            <div className="md:hidden fixed top-0 right-0 bottom-0 w-80 max-w-[85vw] bg-background border-l border-border z-9999 overflow-y-auto shadow-xl">
              <div className="p-6">
                <h3 className="mb-4 text-lg font-semibold">{t('categories')}</h3>
                <nav className="space-y-1">
                  {blog.categories?.map((category: CategoryType) => (
                    <Link
                      key={category.slug}
                      href={
                        !category.slug || category.slug === 'all'
                          ? '/blog'
                          : `/blog/category/${category.slug}`
                      }
                      onClick={() => setIsCategoryOpen(false)}
                      className={cn(
                        'block rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent',
                        blog.currentCategory?.slug === category.slug &&
                          'bg-accent font-medium'
                      )}
                    >
                      {category.title}
                    </Link>
                  ))}
                </nav>
              </div>
            </div>
          </>
        )}

        <div className="flex flex-col gap-6 md:flex-row">
          {/* 左侧分类 - 仅桌面端显示 */}
          <aside className="hidden md:block w-full md:w-64 md:flex-shrink-0">
            <div className="sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto rounded-lg border bg-card p-4">
              <h3 className="mb-4 font-semibold">{t('categories')}</h3>
              <nav className="space-y-1">
                {blog.categories?.map((category: CategoryType) => (
                  <Link
                    key={category.slug}
                    href={
                      !category.slug || category.slug === 'all'
                        ? '/blog'
                        : `/blog/category/${category.slug}`
                    }
                    className={cn(
                      'block rounded-md px-3 py-2 text-sm transition-colors hover:bg-primary hover:text-primary-foreground',
                      blog.currentCategory?.slug === category.slug &&
                        'bg-primary text-primary-foreground font-medium'
                    )}
                  >
                    {category.title || t('all')}
                  </Link>
                ))}
              </nav>
            </div>
          </aside>

          {/* 右侧内容 */}
          <div className="flex-1">
            {/* 顶部标题和视图切换 */}
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex-1">
                {blog.sr_only_title && (
                  <h1 className="sr-only">{blog.sr_only_title}</h1>
                )}
                <h2 className="text-2xl font-bold">{blog.title}</h2>
                <p className="text-muted-foreground mt-1 text-sm">
                  {blog.description}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={cn(
                    'rounded-md p-2 transition-colors',
                    viewMode === 'grid'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-primary/10'
                  )}
                  aria-label={t('grid_view')}
                >
                  <Grid className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={cn(
                    'rounded-md p-2 transition-colors',
                    viewMode === 'list'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-primary/10'
                  )}
                  aria-label={t('list_view')}
                >
                  <List className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* 搜索框 */}
            <div className="mb-6">
              <div className="relative">
                <Search className="text-muted-foreground absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder={t('search_placeholder')}
                  value={searchQuery}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="w-full rounded-lg border bg-background px-10 py-2 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                {searchQuery && (
                  <button
                    onClick={() => handleSearchChange('')}
                    className="text-muted-foreground hover:text-foreground absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                    aria-label={t('clear_search')}
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
              {searchQuery && (
                <p className="text-muted-foreground mt-2 text-sm">
                  {t('found_posts', { count: (blog.posts || []).length })}
                </p>
              )}
            </div>

            {/* 文章列表 */}
            {displayedPosts.length > 0 ? (
              <>
                <div
                  className={cn(
                    viewMode === 'grid'
                      ? 'grid gap-6 sm:grid-cols-2 lg:grid-cols-3'
                      : 'space-y-4'
                  )}
                >
                  {displayedPosts.map((item, idx) => (
                    <Link
                      key={`${item.id}-${idx}`}
                      href={item.url || ''}
                      target={item.target || '_blank'}
                      className={cn(
                        'block overflow-hidden rounded-lg border bg-card transition-shadow hover:shadow-md',
                        viewMode === 'list' && 'flex flex-col gap-4 sm:flex-row'
                      )}
                    >
                      {item.image && (
                        <div
                          className={cn(
                            viewMode === 'grid'
                              ? 'aspect-video w-full'
                              : 'h-48 w-full sm:h-32 sm:w-48 sm:flex-shrink-0'
                          )}
                        >
                          <img
                            src={item.image}
                            alt={item.title || ''}
                            className="h-full w-full object-cover"
                          />
                        </div>
                      )}
                      <div className="flex-1 p-4">
                        <div className="mb-2 flex items-start gap-2">
                          <h3 className="flex-1 text-lg font-semibold line-clamp-2">
                            {item.title}
                            {isNewPost(item.created_at || '') && (
                              <span className="ml-2 inline-flex items-center rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-white dark:bg-green-900/30 dark:text-green-400">
                                {t('new')}
                              </span>
                            )}
                            {item.isRecommended && (
                              <span className="ml-2 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                                {t('recommended')}
                              </span>
                            )}
                          </h3>
                          {item.isPinned && (
                            <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900/30 dark:text-red-400">
                              {t('pinned')}
                            </span>
                          )}
                        </div>
                        <p className="text-muted-foreground mb-3 text-sm line-clamp-2">
                          {stripMarkdown(item.description || '')}
                        </p>
                        <div className="text-muted-foreground flex flex-wrap items-center gap-4 text-xs">
                          {item.created_at && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {item.created_at}
                            </div>
                          )}
                          {item.author_name && (
                            <div className="flex items-center gap-1">
                              {item.author_image && (
                                <Avatar>
                                  <AvatarImage
                                    src={item.author_image}
                                    alt={item.author_name}
                                    className="h-4 w-4 rounded-full"
                                  />
                                  <AvatarFallback>
                                    {item.author_name.charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                              )}
                              {item.author_name}
                            </div>
                          )}
                          {/* Show categories only when viewing "All" category */}
                          {(!blog.currentCategory?.slug || blog.currentCategory?.slug === 'all') && 
                           item.categories && 
                           item.categories.length > 0 && (
                            <div className="flex items-center gap-1 flex-wrap">
                              {item.categories.map((category, catIdx) => (
                                <span
                                  key={`${category.slug}-${catIdx}`}
                                  className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-green-500 dark:border-green-900 bg-transparent text-gray-6 hover:bg-green-500/10"
                                >
                                  {category.title}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>

                {/* 加载指示器 */}
                <div
                  ref={observerTarget}
                  className="mt-8 flex justify-center"
                >
                  {isLoading && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      {t('loading')}
                    </div>
                  )}
                  {!hasMore && displayedPosts.length > 0 && (
                    <p className="text-muted-foreground text-sm">
                      {t('all_loaded')}
                    </p>
                  )}
                </div>
              </>
            ) : (blog.posts || []).length === 0 && searchQuery ? (
              <div className="text-muted-foreground py-12 text-center">
                <p>{t('no_results')}</p>
                <button
                  onClick={() => handleSearchChange('')}
                  className="mt-4 text-sm text-primary hover:underline"
                >
                  {t('clear_search')}
                </button>
              </div>
            ) : (
              <div className="text-muted-foreground py-12 text-center">
                {t('no_content')}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
