'use client';

import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  ArrowUpRight,
  Bookmark,
  BookOpen,
  Calendar,
  ChevronDown,
  Code2,
  FileText,
  Gamepad2,
  Grid2X2,
  ImageIcon,
  Layers3,
  List,
  Search,
  Video,
  X,
} from 'lucide-react';
import { useTranslations } from 'next-intl';

import { Link, usePathname } from '@/core/i18n/navigation';
import { Button } from '@/shared/components/ui/button';
import { cn } from '@/shared/lib/utils';
import { Blog as BlogType, Post as PostType } from '@/shared/types/blocks/blog';

import '@/config/style/library.css';

const PAGE_SIZE = 12;
const manualIcons = {
  'docs-ai-chuhai': BookOpen,
  'docs-shipany-two': Layers3,
  'docs-joyflix': Video,
  'docs-nanobanana': ImageIcon,
  'docs-gamiary': Gamepad2,
  'docs-blog': FileText,
  'docs-markdown-blog': Code2,
  'docs-gpt-image2': ImageIcon,
};

function stripMarkdown(text: string) {
  return text
    .replace(/```[\s\S]*?```/g, '')
    .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/(^#{1,6}\s+|[*_`>])/gm, '')
    .trim();
}

function isManual(post: PostType) {
  return Boolean(post.id && post.id in manualIcons);
}

function LibraryHero({ manual }: { manual: PostType }) {
  const t = useTranslations('blog.library');

  return (
    <div className="library-hero">
      <div className="library-intro">
        <h1>{t('hero_title')}</h1>
        <p>{t('hero_description')}</p>
        <div className="flex flex-wrap gap-3">
          <Button asChild size="lg">
            <Link href={manual.url || '/docs'}>
              <BookOpen className="size-4" aria-hidden="true" />
              {t('start_reading')}
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <a href="#library-catalog">{t('browse_manuals')}</a>
          </Button>
        </div>
        <div className="library-topics" aria-label={t('covered_topics')}>
          <span>{t('topic_build')}</span>
          <span>{t('topic_grow')}</span>
          <span>{t('topic_launch')}</span>
        </div>
      </div>
      <Link
        href={manual.url || '/docs'}
        className="library-feature"
        aria-label={t('start_reading')}
      >
        <div className="library-book">
          <div className="library-book-top">
            <BookOpen size={24} strokeWidth={1.5} aria-hidden="true" />
            <span>{t('main_manual')}</span>
          </div>
          <div className="library-book-title">
            AI 出海
            <br />
            实战手册
          </div>
          <div className="library-book-bottom">
            <span>{t('book_caption')}</span>
            <ArrowUpRight size={21} aria-hidden="true" />
          </div>
          <span className="library-bookmark" aria-hidden="true" />
        </div>
        <div className="library-feature-note">
          <span>{t('start_here')}</span>
          <span>{t('step_by_step')}</span>
        </div>
      </Link>
    </div>
  );
}

function PostCard({ post, view }: { post: PostType; view: 'grid' | 'list' }) {
  const t = useTranslations('blog');
  const manual = isManual(post);
  const Icon = manualIcons[post.id as keyof typeof manualIcons] || FileText;
  const palette =
    post.id === 'docs-ai-chuhai'
      ? 'green'
      : post.id === 'docs-joyflix' || post.id === 'docs-gpt-image2'
        ? 'blue'
        : post.id === 'docs-nanobanana' || post.id === 'docs-gamiary'
          ? 'gold'
          : 'slate';

  return (
    <Link
      href={post.url || '/blog'}
      target={post.target || '_self'}
      rel={post.target === '_blank' ? 'noopener noreferrer' : undefined}
      className={cn('library-entry', view === 'list' && 'library-entry-row')}
      data-palette={palette}
    >
      {post.image ? (
        <img
          src={post.image}
          alt=""
          loading="lazy"
          className="library-entry-image"
        />
      ) : (
        <div className="library-entry-symbol" aria-hidden="true">
          <Icon size={24} strokeWidth={1.6} />
        </div>
      )}
      <div className="library-entry-content">
        <div className="library-entry-kind">
          <span>{manual ? t('library.manual') : t('library.article')}</span>
          {post.isPinned ? (
            <span>{t('page.pinned')}</span>
          ) : (
            post.isRecommended && (
              <Bookmark size={13} aria-label={t('page.recommended')} />
            )
          )}
        </div>
        <h3>{post.title}</h3>
        <p>{stripMarkdown(post.description || '')}</p>
        <div className="library-entry-meta">
          {post.created_at ? (
            <span>
              <Calendar size={12} aria-hidden="true" />
              {post.created_at}
            </span>
          ) : (
            manual && <span>{t('library.manual_details')}</span>
          )}
          {post.author_name && (
            <span className="min-w-0 truncate">{post.author_name}</span>
          )}
          <ArrowUpRight size={17} aria-hidden="true" />
        </div>
        {post.categories && post.categories.length > 0 && (
          <div className="text-muted-foreground mt-3 flex flex-wrap gap-2 text-xs">
            {post.categories.map((category) => (
              <span key={category.id || category.slug}>{category.title}</span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}

export function Blog({
  className,
  blog: suppliedBlog,
  section,
  ...data
}: {
  className?: string;
  blog?: BlogType;
  section?: Partial<BlogType>;
  posts?: PostType[];
  categories?: BlogType['categories'];
  currentCategory?: BlogType['currentCategory'];
}) {
  const blog = suppliedBlog || {
    ...data,
    ...section,
    posts: data.posts || section?.posts || [],
  };
  const t = useTranslations('blog');
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const query = searchParams.get('search') || '';
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [filter, setFilter] = useState<'all' | 'manuals' | 'articles'>('all');
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const sentinel = useRef<HTMLDivElement>(null);
  const home = pathname === '/';
  const posts = blog.posts || [];
  const manuals = posts.filter(isManual);
  const mainManual = manuals.find((post) => post.id === 'docs-ai-chuhai');
  const filteredPosts = posts.filter((post) => {
    if (filter === 'manuals' && !isManual(post)) return false;
    if (filter === 'articles' && isManual(post)) return false;
    return `${post.title || ''} ${stripMarkdown(post.description || '')}`
      .toLocaleLowerCase()
      .includes(query.trim().toLocaleLowerCase());
  });
  const hasMore = visibleCount < filteredPosts.length;

  useEffect(() => {
    if (!hasMore || !sentinel.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisibleCount((count) => count + PAGE_SIZE);
      },
      { rootMargin: '160px' }
    );
    observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [hasMore, visibleCount, query, filter]);

  function updateSearch(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set('search', value);
    else params.delete('search');
    window.history.replaceState(
      null,
      '',
      `${window.location.pathname}${params.size ? `?${params}` : ''}${window.location.hash}`
    );
    setVisibleCount(PAGE_SIZE);
  }

  return (
    <section
      id={blog.id}
      className={cn('library-page', blog.className, className)}
    >
      <div className="container">
        {home && mainManual ? (
          <LibraryHero manual={mainManual} />
        ) : (
          <div className="library-page-heading">
            <h1>{blog.title || t('blog.title')}</h1>
            <p>{blog.description || t('blog.description')}</p>
          </div>
        )}
        <div id="library-catalog" className="library-catalog">
          <div className="library-catalog-heading">
            <div>
              <h2>
                {home ? t('library.catalog_title') : t('library.all_content')}
              </h2>
              <p>
                {t('library.catalog_description', {
                  manuals: manuals.length,
                  articles: posts.length - manuals.length,
                })}
              </p>
            </div>
            <div className="library-search">
              <Search size={18} aria-hidden="true" />
              <input
                type="search"
                value={query}
                onChange={(event) => updateSearch(event.target.value)}
                placeholder={t('library.search_placeholder')}
                aria-label={t('library.search_placeholder')}
              />
              {query && (
                <button
                  type="button"
                  onClick={() => updateSearch('')}
                  aria-label={t('page.clear_search')}
                >
                  <X size={16} aria-hidden="true" />
                </button>
              )}
            </div>
          </div>
          <div className="library-toolbar">
            <div
              className="library-filters"
              role="group"
              aria-label={t('library.content_type')}
            >
              {(['all', 'manuals', 'articles'] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={filter === value}
                  onClick={() => {
                    setFilter(value);
                    setVisibleCount(PAGE_SIZE);
                  }}
                >
                  {t(`library.filter_${value}`)}
                  <span>
                    {value === 'all'
                      ? posts.length
                      : value === 'manuals'
                        ? manuals.length
                        : posts.length - manuals.length}
                  </span>
                </button>
              ))}
            </div>
            <div
              className="library-view"
              role="group"
              aria-label={t('library.view_mode')}
            >
              <button
                type="button"
                aria-label={t('page.grid_view')}
                aria-pressed={view === 'grid'}
                onClick={() => setView('grid')}
              >
                <Grid2X2 size={17} aria-hidden="true" />
              </button>
              <button
                type="button"
                aria-label={t('page.list_view')}
                aria-pressed={view === 'list'}
                onClick={() => setView('list')}
              >
                <List size={19} aria-hidden="true" />
              </button>
            </div>
          </div>
          {blog.categories && blog.categories.length > 1 && (
            <nav
              className="mb-6 flex flex-wrap gap-2"
              aria-label={t('page.categories')}
            >
              {blog.categories.map((category) => (
                <Link
                  key={category.id || category.slug}
                  href={
                    category.url ||
                    (category.slug === 'all'
                      ? '/blog'
                      : `/blog/category/${category.slug}`)
                  }
                  aria-current={
                    category.slug === blog.currentCategory?.slug
                      ? 'page'
                      : undefined
                  }
                  className="text-muted-foreground hover:bg-accent aria-[current=page]:bg-accent aria-[current=page]:text-accent-foreground rounded-md px-3 py-2 text-sm"
                >
                  {category.title}
                </Link>
              ))}
            </nav>
          )}
          {query && (
            <p className="text-muted-foreground mb-5 text-sm" role="status">
              {t('page.found_posts', { count: filteredPosts.length })}
            </p>
          )}
          {filteredPosts.length ? (
            <div
              className={cn(
                'library-entries',
                view === 'list' && 'library-entries-list'
              )}
            >
              {filteredPosts.slice(0, visibleCount).map((post) => (
                <PostCard
                  key={post.id || post.url || post.slug}
                  post={post}
                  view={view}
                />
              ))}
            </div>
          ) : (
            <div className="library-empty" role="status">
              <Search size={28} strokeWidth={1.5} aria-hidden="true" />
              <h3>{query ? t('page.no_results') : t('page.no_content')}</h3>
              <p>{t('library.empty_hint')}</p>
              <Button
                variant="outline"
                onClick={() => {
                  updateSearch('');
                  setFilter('all');
                }}
              >
                {t('library.reset_filters')}
              </Button>
            </div>
          )}
          <div ref={sentinel} className="library-end">
            {hasMore ? (
              <Button
                variant="outline"
                onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
              >
                {t('library.load_more')}
                <ChevronDown size={16} />
              </Button>
            ) : (
              filteredPosts.length > 0 && <span>{t('library.end_note')}</span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
