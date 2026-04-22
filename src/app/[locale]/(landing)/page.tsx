import { getTranslations, setRequestLocale } from 'next-intl/server';

import { getThemePage } from '@/core/theme';
import { getPostsAndCategories } from '@/shared/models/post';
import {
  Blog as BlogType,
  Category as CategoryType,
  Post as PostType,
} from '@/shared/types/blocks/blog';

export default async function LandingPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ page?: number; pageSize?: number }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  // load blog data
  const t = await getTranslations('blog');

  let posts: PostType[] = [];
  let categories: CategoryType[] = [];

  // current category data
  const currentCategory: CategoryType = {
    id: 'all',
    slug: 'all',
    title: t('page.all'),
    url: `/blog`,
  };

  try {
    const { page: pageNum, pageSize } = await searchParams;
    const page = pageNum || 1;
    const limit = pageSize || 30;

    const { posts: allPosts, categories: allCategories } =
      await getPostsAndCategories({
        locale,
        page,
        limit,
      });

    // Hide the seed placeholder post; real blog posts added via admin still show.
    posts = allPosts.filter((p) => !(p.title || '').includes('YourAppName'));
    categories = allCategories;

    categories.unshift(currentCategory);
  } catch (error) {
    console.log('getting posts failed:', error);
  }

  // Feature the doc manuals as entries at the top of the blog listing.
  const featuredDocs: PostType[] = [
    {
      id: 'docs-ai-chuhai',
      slug: 'docs-ai-chuhai',
      title: 'AI 出海手册',
      description:
        'AI 出海全链路知识库：找需求、开发、SEO、GEO、流量、投流、外链、数据分析、支付、复盘。',
      url: '/docs',
      isRecommended: true,
    },
    {
      id: 'docs-shipany-two',
      slug: 'docs-shipany-two',
      title: 'ShipAny Two 手册',
      description:
        'ShipAny Two 模板的快速开始、配置、支付集成、部署与常见问题完整指南。',
      url: '/docs/shipany-two/getting-started/readme',
      isRecommended: true,
    },
    {
      id: 'docs-joyflix',
      slug: 'docs-joyflix',
      title: 'JoyFlix 手册',
      description:
        'AI 视频生成站（JoyFlix）模板的快速上手、R2/数据库配置、Doubao-Seedance 接入、Stripe/Creem 支付、部署与常见问题指南。',
      url: '/docs/joyflix/getting-started/readme',
      isRecommended: true,
    },
    {
      id: 'docs-nanobanana',
      slug: 'docs-nanobanana',
      title: 'Nano Banana 手册',
      description:
        'AI 图片生成站（Nano Banana）模板的快速上手、Showcases/Hairstyles 数据管理、支付集成、部署与常见问题指南。',
      url: '/docs/nanobanana/getting-started/readme',
      isRecommended: true,
    },
    {
      id: 'docs-gamiary',
      slug: 'docs-gamiary',
      title: 'Gamiary 手册',
      description:
        '游戏站（Gamiary）模板的快速上手、游戏分类/列表配置、Neon 数据库接入、部署与常见问题指南。',
      url: '/docs/gamiary/getting-started/readme',
      isRecommended: true,
    },
    {
      id: 'docs-blog',
      slug: 'docs-blog',
      title: 'Blog 手册',
      description:
        '博客模板的快速上手、Post/Subscribe/高德地图 配置、部署与常见问题指南。',
      url: '/docs/blog/getting-started/readme',
      isRecommended: true,
    },
    {
      id: 'docs-markdown-blog',
      slug: 'docs-markdown-blog',
      title: 'Markdown Blog 手册',
      description:
        'Markdown 博客模板的快速上手、Categories/Post 配置、部署与常见问题指南。',
      url: '/docs/markdown-blog/getting-started/readme',
      isRecommended: true,
    },
  ];
  posts = [...featuredDocs, ...posts];

  // build blog data
  const blog: BlogType = {
    ...t.raw('blog'),
    categories,
    currentCategory,
    posts,
  };

  // load page component
  const Page = await getThemePage('blog');

  return <Page locale={locale} blog={blog} />;
}
