import { getTranslations, setRequestLocale } from 'next-intl/server';

import { PERMISSIONS, requirePermission } from '@/core/rbac';
import { Header, Main, MainHeader } from '@/shared/blocks/dashboard';
import { TableCard } from '@/shared/blocks/table';
import {
  getPosts,
  getPostsCount,
  Post,
  PostStatus,
  PostType,
} from '@/shared/models/post';
import { getTaxonomies } from '@/shared/models/taxonomy';
import { Button, Crumb } from '@/shared/types/blocks/common';
import { type Table } from '@/shared/types/blocks/table';

import { PostActions } from './post-actions';

export default async function PostsPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ page?: number; pageSize?: number; search?: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  // Check if user has permission to read posts
  await requirePermission({
    code: PERMISSIONS.POSTS_READ,
    redirectUrl: '/admin/no-permission',
    locale,
  });

  const { page: pageNum, pageSize, search } = await searchParams;
  const page = pageNum || 1;
  const limit = pageSize || 30;

  const t = await getTranslations('admin.posts');

  const crumbs: Crumb[] = [
    { title: t('list.crumbs.admin'), url: '/admin' },
    { title: t('list.crumbs.posts'), is_active: true },
  ];

  const total = await getPostsCount({
    type: PostType.ARTICLE,
    status: PostStatus.PUBLISHED,
    search,
  });

  const posts = await getPosts({
    type: PostType.ARTICLE,
    status: PostStatus.PUBLISHED,
    search,
    page,
    limit,
  });

  const table: Table = {
    columns: [
      { name: 'title', title: t('fields.title') },
      { name: 'authorName', title: t('fields.author_name') },
      {
        name: 'categories',
        title: t('fields.categories'),
        className: 'max-w-[200px] truncate',
        callback: async (item: Post) => {
          if (!item.categories) {
            return '-';
          }
          const categoriesIds = item.categories.split(',');
          const categories = await getTaxonomies({
            ids: categoriesIds,
          });
          if (!categories) {
            return '-';
          }

          const categoriesNames = categories.map((category) => {
            return category.title;
          });

          return categoriesNames.join(', ');
        },
      },
      { name: 'createdAt', title: t('fields.created_at'), type: 'time' },
      { name: 'updatedAt', title: t('fields.updated_at'), type: 'time' },
      {
        name: 'action',
        title: '',
        callback: (item: Post) => {
          return <PostActions item={item} />;
        },
      },
    ],
    data: posts,
    pagination: {
      total,
      page,
      limit,
    },
  };

  const actions: Button[] = [
    {
      id: 'add',
      title: t('list.buttons.add'),
      icon: 'RiAddLine',
      url: '/admin/posts/add',
    },
  ];

  return (
    <>
      <Header crumbs={crumbs} />
      <Main>
        <MainHeader title={t('list.title')} actions={actions} />
        <div className="mb-4">
          <form action="/admin/posts" method="get" className="flex gap-2">
            <input
              type="text"
              name="search"
              defaultValue={search}
              placeholder={t('list.search_placeholder')}
              className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              {t('list.search_button')}
            </button>
            {search && (
              <a
                href="/admin/posts"
                className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                {t('list.clear_button')}
              </a>
            )}
          </form>
        </div>
        <TableCard table={table} />
      </Main>
    </>
  );
}
