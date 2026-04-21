import { getMDXComponents } from '@/mdx-components';
import { and, count, desc, eq, like, sql } from 'drizzle-orm';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import moment from 'moment';

import { db } from '@/core/db';
import { pagesSource, postsSource } from '@/core/docs/source';
import { generateTOC } from '@/core/docs/toc';
import { post } from '@/config/db/schema';
import { MarkdownContent } from '@/shared/blocks/common/markdown-content';
import {
  Category as BlogCategoryType,
  Post as BlogPostType,
} from '@/shared/types/blocks/blog';

import { getTaxonomies, TaxonomyStatus, TaxonomyType } from './taxonomy';

export type Post = typeof post.$inferSelect;
export type NewPost = typeof post.$inferInsert;
export type UpdatePost = Partial<Omit<NewPost, 'id' | 'createdAt'>>;

export enum PostType {
  ARTICLE = 'article',
  PAGE = 'page',
}

export enum PostStatus {
  PUBLISHED = 'published', // published and visible to the public
  PENDING = 'pending', // pending review by admin
  DRAFT = 'draft', // draft and not visible to the public
  ARCHIVED = 'archived', // archived means deleted
}

export async function addPost(data: NewPost) {
  try {
    const [result] = await db().insert(post).values(data).returning();
    return result;
  } catch (error: any) {
    // Check for unique constraint violation
    if (error.code === '23505' || error.message?.includes('unique')) {
      throw new Error('A post with this slug already exists. Please use a different slug.');
    }
    throw error;
  }
}

export async function updatePost(id: string, data: UpdatePost) {
  try {
    const [result] = await db()
      .update(post)
      .set(data)
      .where(eq(post.id, id))
      .returning();

    return result;
  } catch (error: any) {
    // Check for unique constraint violation
    if (error.code === '23505' || error.message?.includes('unique')) {
      throw new Error('A post with this slug already exists. Please use a different slug.');
    }
    throw error;
  }
}

export async function togglePostPin(id: string, isPinned: boolean) {
  const data: UpdatePost = {
    isPinned,
    pinnedAt: isPinned ? new Date() : null,
  };
  return updatePost(id, data);
}

export async function togglePostRecommend(id: string, isRecommended: boolean) {
  const data: UpdatePost = {
    isRecommended,
  };
  return updatePost(id, data);
}

export async function deletePost(id: string) {
  // 直接删除文章而不是标记为归档
  const result = await db()
    .update(post)
    .set({ status: PostStatus.ARCHIVED })
    .where(eq(post.id, id))
    .returning();

  return result[0];
}

export async function findPost({
  id,
  slug,
  status,
}: {
  id?: string;
  slug?: string;
  status?: PostStatus;
}) {
  const [result] = await db()
    .select()
    .from(post)
    .where(
      and(
        id ? eq(post.id, id) : undefined,
        slug ? eq(post.slug, slug) : undefined,
        status ? eq(post.status, status) : undefined
      )
    )
    .limit(1);

  return result;
}

export async function getPosts({
  type,
  status,
  category,
  tag,
  search,
  page = 1,
  limit = 30,
  sortByCreated,
}: {
  type?: PostType;
  status?: PostStatus;
  category?: string;
  tag?: string[];
  search?: string;
  page?: number;
  limit?: number;
  sortByCreated?: boolean;
} = {}): Promise<Post[]> {
  const baseQuery = db()
    .select()
    .from(post)
    .where(
      and(
        type ? eq(post.type, type) : undefined,
        status ? eq(post.status, status) : undefined,
        category ? like(post.categories, `%${category}%`) : undefined,
        tag ? like(post.tags, `%${tag}%`) : undefined,
        search
          ? sql`${post.title} LIKE ${`%${search}%`}`
          : undefined
      )
    );

  // Apply ordering based on sortByCreated flag
  const orderedQuery = sortByCreated
    ? baseQuery.orderBy(
        desc(post.isPinned),
        desc(post.pinnedAt),
        post.createdAt  // Ascending order by creation time
      )
    : baseQuery.orderBy(
        desc(post.isPinned),
        desc(post.pinnedAt),
        desc(post.updatedAt),
        desc(post.createdAt)
      );

  const result = await orderedQuery
    .limit(limit)
    .offset((page - 1) * limit);

  return result;
}

export async function getPostsCount({
  type,
  status,
  category,
  tag,
  search,
}: {
  type?: PostType;
  status?: PostStatus;
  category?: string;
  tag?: string;
  search?: string;
} = {}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(post)
    .where(
      and(
        type ? eq(post.type, type) : undefined,
        status ? eq(post.status, status) : undefined,
        category ? like(post.categories, `%${category}%`) : undefined,
        tag ? like(post.tags, `%${tag}%`) : undefined,
        search
          ? sql`${post.title} LIKE ${`%${search}%`}`
          : undefined
      )
    )
    .limit(1);

  return result?.count || 0;
}

// get single post, both from local file and database
// database post has higher priority
export async function getPost({
  slug,
  locale,
  postPrefix = '/blog/',
}: {
  slug: string;
  locale: string;
  postPrefix?: string;
}): Promise<BlogPostType | null> {
  let post: BlogPostType | null = null;

  try {
    // get post from database
    const postData = await findPost({ slug, status: PostStatus.PUBLISHED });
    if (postData) {
      // post exist in database
      const content = postData.content || '';

      // Convert markdown content to MarkdownContent component
      const body = content ? <MarkdownContent content={content} /> : undefined;

      // Generate TOC from content
      const toc = content ? generateTOC(content) : undefined;

      post = {
        id: postData.id,
        slug: postData.slug,
        title: postData.title || '',
        description: postData.description || '',
        content: '',
        body: body,
        toc: toc,
        created_at:
          getPostDate({
            created_at: postData.createdAt.toISOString(),
            locale,
          }) || '',
        updated_at:
          getPostDate({
            created_at: postData.updatedAt.toISOString(),
            locale,
          }) || '',
        author_name: postData.authorName || '',
        author_image: postData.authorImage || '',
        author_role: '',
        url: `${postPrefix}${postData.slug}`,
      };

      return post;
    }
  } catch (e) {
    console.log('get post from database failed:', e);
  }

  // get post from locale file
  const localPost = await getLocalPost({ slug, locale, postPrefix });

  return localPost;
}

export async function getLocalPost({
  slug,
  locale,
  postPrefix = '/blog/',
}: {
  slug: string;
  locale: string;
  postPrefix?: string;
}): Promise<BlogPostType | null> {
  const localPost = await postsSource.getPage([slug], locale);
  if (!localPost) {
    return null;
  }

  const MDXContent = localPost.data.body;
  const body = (
    <MDXContent
      components={getMDXComponents({
        // this allows you to link to other pages with relative file paths
        a: createRelativeLink(postsSource, localPost),
      })}
    />
  );

  const frontmatter = localPost.data as any;

  const post: BlogPostType = {
    id: localPost.path,
    slug: slug,
    title: localPost.data.title || '',
    description: localPost.data.description || '',
    content: '',
    body: body,
    toc: localPost.data.toc, // Use fumadocs auto-generated TOC
    created_at: frontmatter.created_at
      ? getPostDate({
          created_at: frontmatter.created_at,
          locale,
        })
      : '',
    author_name: frontmatter.author_name || '',
    author_image: frontmatter.author_image || '',
    author_role: '',
    url: `${postPrefix}${slug}`,
  };

  return post;
}

// get local page from: content/pages/*.md
export async function getLocalPage({
  slug,
  locale,
}: {
  slug: string;
  locale: string;
}): Promise<BlogPostType | null> {
  const localPage = await pagesSource.getPage([slug], locale);
  if (!localPage) {
    return null;
  }

  const MDXContent = localPage.data.body;
  const body = (
    <MDXContent
      components={getMDXComponents({
        // this allows you to link to other pages with relative file paths
        a: createRelativeLink(pagesSource, localPage),
      })}
    />
  );

  const frontmatter = localPage.data as any;

  const post: BlogPostType = {
    id: localPage.path,
    slug: slug,
    title: localPage.data.title || '',
    description: localPage.data.description || '',
    content: '',
    body: body,
    toc: localPage.data.toc, // Use fumadocs auto-generated TOC
    created_at: frontmatter.created_at
      ? getPostDate({
          created_at: frontmatter.created_at,
          locale,
        })
      : '',
    author_name: frontmatter.author_name || '',
    author_image: frontmatter.author_image || '',
    author_role: '',
    url: `/${locale}/${slug}`,
  };

  return post;
}

// get posts and categories, both from local files and database
export async function getPostsAndCategories({
  page = 1,
  limit = 30,
  locale,
  search,
  postPrefix = '/blog/',
  categoryPrefix = '/blog/category/',
}: {
  page?: number;
  limit?: number;
  locale: string;
  search?: string;
  postPrefix?: string;
  categoryPrefix?: string;
}) {
  let posts: BlogPostType[] = [];
  let categories: BlogCategoryType[] = [];

  // merge posts from both locale and remote, remove duplicates by slug
  // remote posts have higher priority
  const postsMap = new Map<string, BlogPostType>();

  // 1. get local posts (only if no search query)
  if (!search) {
    const {
      posts: localPosts,
      postsCount: localPostsCount,
      categories: localCategories,
      categoriesCount: localCategoriesCount,
    } = await getLocalPostsAndCategories({
      locale,
      postPrefix,
      categoryPrefix,
    });

    // add local posts to postsMap
    localPosts.forEach((post) => {
      if (post.slug) {
        postsMap.set(post.slug, post);
      }
    });
  }

  // 2. get remote posts
  const {
    posts: remotePosts,
    postsCount: remotePostsCount,
    categories: remoteCategories,
    categoriesCount: remoteCategoriesCount,
  } = await getRemotePostsAndCategories({
    page,
    limit,
    locale,
    search,
    postPrefix,
    categoryPrefix,
  });

  // add remote posts to postsMap
  remotePosts.forEach((post) => {
    if (post.slug) {
      postsMap.set(post.slug, post);
    }
  });

  // Convert map to array and sort by pinned status first, then by created_at desc
  posts = Array.from(postsMap.values()).sort((a, b) => {
    // First, sort by pinned status (pinned posts first)
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;
    
    // If both are pinned or both are not pinned, sort by created_at desc (newest first)
    const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
    const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
    return dateB - dateA;
  });

  return {
    posts,
    postsCount: posts.length,
    categories: remoteCategories, // todo: merge local categories
    categoriesCount: remoteCategoriesCount, // todo: merge local categories count
  };
}

// get remote posts and categories
export async function getRemotePostsAndCategories({
  page = 1,
  limit = 30,
  locale,
  search,
  postPrefix = '/blog/',
  categoryPrefix = '/blog/category/',
}: {
  page?: number;
  limit?: number;
  locale: string;
  search?: string;
  postPrefix?: string;
  categoryPrefix?: string;
}) {
  const dbPostsList: BlogPostType[] = [];
  const dbCategoriesList: BlogCategoryType[] = [];

  try {
    // get posts from database
    const dbPosts = await getPosts({
      type: PostType.ARTICLE,
      status: PostStatus.PUBLISHED,
      search,
      page,
      limit,
    });

    if (!dbPosts || dbPosts.length === 0) {
      return {
        posts: [],
        postsCount: 0,
        categories: [],
        categoriesCount: 0,
      };
    }

    // get categories from database first to build category map
    const dbCategories = await getTaxonomies({
      type: TaxonomyType.CATEGORY,
      status: TaxonomyStatus.PUBLISHED,
    });

    // Build category map for quick lookup by ID (not slug)
    const categoryMap = new Map<string, BlogCategoryType>();
    (dbCategories || []).forEach((category) => {
      categoryMap.set(category.id, {
        id: category.id,
        slug: category.slug,
        title: category.title,
        url: `${categoryPrefix}${category.slug}`,
      });
    });

    dbPostsList.push(
      ...dbPosts.map((post) => {
        // Parse categories from comma-separated string (IDs, not slugs)
        const postCategories: BlogCategoryType[] = [];
        if (post.categories) {
          const categoryIds = post.categories.split(',').map(s => s.trim()).filter(Boolean);
          categoryIds.forEach((id) => {
            const category = categoryMap.get(id);
            if (category) {
              postCategories.push(category);
            }
          });
        }

        return {
          id: post.id,
          slug: post.slug,
          title: post.title || '',
          description: post.description || '',
          author_name: post.authorName || '',
          author_image: post.authorImage || '',
          created_at:
            getPostDate({
              created_at: post.createdAt.toISOString(),
              locale,
            }) || '',
          updated_at:
            getPostDate({
              created_at: post.updatedAt.toISOString(),
              locale,
            }) || '',
          image: post.image || '',
          url: `${postPrefix}${post.slug}`,
          isPinned: post.isPinned,
          isRecommended: post.isRecommended,
          categories: postCategories,
        };
      })
    );

    // Use categories from categoryMap
    dbCategoriesList.push(...Array.from(categoryMap.values()));
  } catch (e) {
    console.log('get remote posts and categories failed:', e);
  }

  return {
    posts: dbPostsList,
    postsCount: dbPostsList.length,
    categories: dbCategoriesList,
    categoriesCount: dbCategoriesList.length,
  };
}

// get local posts and categories
export async function getLocalPostsAndCategories({
  locale,
  postPrefix = '/blog/',
  categoryPrefix = '/blog/category/',
}: {
  locale: string;
  postPrefix?: string;
  categoryPrefix?: string;
}) {
  const localPostsList: BlogPostType[] = [];

  // get posts from local files
  const localPosts = postsSource.getPages(locale);

  // no local posts
  if (!localPosts || localPosts.length === 0) {
    return {
      posts: [],
      postsCount: 0,
      categories: [],
      categoriesCount: 0,
    };
  }

  // Build posts data from local content
  localPostsList.push(
    ...localPosts.map((post) => {
      const frontmatter = post.data as any;
      const slug = getPostSlug({
        url: post.url,
        locale,
        prefix: postPrefix,
      });

      return {
        id: post.path,
        slug: slug,
        title: post.data.title || '',
        description: post.data.description || '',
        author_name: frontmatter.author_name || '',
        author_image: frontmatter.author_image || '',
        created_at: frontmatter.created_at
          ? getPostDate({
              created_at: frontmatter.created_at,
              locale,
            })
          : '',
        image: frontmatter.image || '',
        url: `${postPrefix}${slug}`,
      };
    })
  );

  return {
    posts: localPostsList,
    postsCount: localPostsList.length,
    categories: [],
    categoriesCount: 0,
  };
}

// Helper function to replace slug for local posts
export function getPostSlug({
  url,
  locale,
  prefix = '/blog/',
}: {
  url: string; // post url, like: /zh/blog/what-is-xxx
  locale: string; // locale
  prefix?: string; // post slug prefix
}): string {
  if (url.startsWith(prefix)) {
    return url.replace(prefix, '');
  } else if (url.startsWith(`/${locale}${prefix}`)) {
    return url.replace(`/${locale}${prefix}`, '');
  }

  return url;
}

export function getPostDate({
  created_at,
  locale,
}: {
  created_at: string;
  locale?: string;
}) {
  return moment(created_at)
    .locale(locale || 'en')
    .format(locale === 'zh' ? 'YYYY/MM/DD' : 'MMM D, YYYY');
}

// Helper function to remove frontmatter from markdown content
export function removePostFrontmatter(content: string): string {
  // Match frontmatter pattern: ---\n...content...\n---
  const frontmatterRegex = /^---\r?\n[\s\S]*?\r?\n---\r?\n/;
  return content.replace(frontmatterRegex, '').trim();
}

// Get previous and next posts
export async function getAdjacentPosts({
  slug,
  locale,
  postPrefix = '/blog/',
}: {
  slug: string;
  locale: string;
  postPrefix?: string;
}): Promise<{
  prevPost: { title: string; url: string } | null;
  nextPost: { title: string; url: string } | null;
}> {
  try {
    // Get current post from database to find its category
    const currentPost = await findPost({ slug, status: PostStatus.PUBLISHED });
    
    if (!currentPost || !currentPost.categories) {
      return { prevPost: null, nextPost: null };
    }

    // Get the first category ID
    const categoryIds = currentPost.categories.split(',').map((s: string) => s.trim()).filter(Boolean);
    if (categoryIds.length === 0) {
      return { prevPost: null, nextPost: null };
    }
    const categoryId = categoryIds[0];

    // Get all posts in the same category, sorted by creation time ascending
    const postsInCategory = await getPosts({
      type: PostType.ARTICLE,
      status: PostStatus.PUBLISHED,
      category: categoryId,
      page: 1,
      limit: 1000,
      sortByCreated: true, // Sort by creation time
    });

    if (!postsInCategory || postsInCategory.length === 0) {
      return { prevPost: null, nextPost: null };
    }

    // Find current post index
    const currentIndex = postsInCategory.findIndex((post) => post.slug === slug);

    if (currentIndex === -1) {
      return { prevPost: null, nextPost: null };
    }

    // Posts are sorted by creation time ascending (oldest first), so:
    // - prevPost (上一篇) should be the previous post in the array (currentIndex - 1)
    // - nextPost (下一篇) should be the next post in the array (currentIndex + 1)
    const prevPost =
      currentIndex > 0
        ? {
            title: postsInCategory[currentIndex - 1].title || '',
            url: `${postPrefix}${postsInCategory[currentIndex - 1].slug}`,
          }
        : null;

    const nextPost =
      currentIndex < postsInCategory.length - 1
        ? {
            title: postsInCategory[currentIndex + 1].title || '',
            url: `${postPrefix}${postsInCategory[currentIndex + 1].slug}`,
          }
        : null;

    return { prevPost, nextPost };
  } catch (error) {
    console.error('Error getting adjacent posts:', error);
    return { prevPost: null, nextPost: null };
  }
}
