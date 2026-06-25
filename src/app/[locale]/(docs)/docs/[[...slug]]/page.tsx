import { notFound } from 'next/navigation';
import { getMDXComponents } from '@/mdx-components';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import {
  DocsBody,
  DocsDescription,
  DocsPage,
  DocsTitle,
} from 'fumadocs-ui/page';
import { findNeighbour } from 'fumadocs-core/server';

import { source } from '@/core/docs/source';
import { redirect } from '@/core/i18n/navigation';

export const dynamic = 'force-dynamic';
export const dynamicParams = true;

// Fumadocs indexes pages under encodeURI(segment). Next.js 16.2 passes
// URL-encoded segments to page() but decoded segments to generateMetadata(),
// so we normalize to encodeURI here for consistent lookup.
function encodeSlug(slug?: string[]) {
  return slug?.map((s) => {
    try {
      // If already encoded, decoding yields a different string; encodeURI that back.
      // If raw, encodeURI produces the canonical encoded form.
      return encodeURI(decodeURI(s));
    } catch {
      return s;
    }
  });
}

const HANDBOOK_ROOTS = new Set([
  'shipany-two',
  'joyflix',
  'nanobanana',
  'gamiary',
  'blog',
  'markdown-blog',
]);

// ISO `2026-06-16` -> `06/16/2026` to match the source site's date format.
function formatDate(iso?: string) {
  if (!iso) return undefined;
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  return m ? `${m[2]}/${m[3]}/${m[1]}` : iso;
}

export default async function DocsContentPage(props: {
  params: Promise<{ slug?: string[]; locale?: string }>;
}) {
  const params = await props.params;
  const slug = encodeSlug(params.slug);

  // fumadocs skips a root folder's index.mdx, so /docs/<handbook> can't be
  // matched by searchPath and the sidebar falls back to the full tree. Send
  // visitors straight to the first real page instead. Use next-intl's redirect
  // so the locale prefix follows the `as-needed` rule (no bouncing).
  if (slug && slug.length === 1 && HANDBOOK_ROOTS.has(slug[0])) {
    redirect({
      href: `/docs/${slug[0]}/getting-started/readme`,
      locale: (params.locale || 'en') as 'en' | 'zh',
    });
  }

  const page = source.getPage(slug, params.locale);

  if (!page) notFound();

  const MDXContent = page.data.body;

  // Compute prev/next on the server so the footer doesn't depend on
  // `usePathname()` during hydration (that caused grid-cols-1 ↔ grid-cols-2
  // hydration mismatch warnings).
  const tree = (source.pageTree as any)[params.locale || 'en'];
  const neighbour = findNeighbour(tree, page.url);

  // Source-site publish/update dates (only /sea articles carry these).
  const created = formatDate((page.data as { date?: string }).date);
  const updated = formatDate((page.data as { updated?: string }).updated);

  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full}
      tableOfContent={{
        style: 'clerk',
      }}
      footer={{ items: neighbour }}
    >
      <DocsTitle>{page.data.title}</DocsTitle>
      {created && (
        <div className="mb-6 flex justify-between text-sm text-fd-muted-foreground">
          <div>Created: {created}</div>
          {updated && <div className="sm:text-right">Updated: {updated}</div>}
        </div>
      )}
      <DocsDescription>{page.data.description}</DocsDescription>
      <DocsBody>
        <MDXContent
          components={getMDXComponents({
            // this allows you to link to other pages with relative file paths
            a: createRelativeLink(source, page),
          })}
        />
      </DocsBody>
    </DocsPage>
  );
}

export async function generateStaticParams() {
  return source.generateParams('slug', 'locale');
}

export async function generateMetadata(props: {
  params: Promise<{ slug?: string[]; locale?: string }>;
}) {
  const params = await props.params;
  const slug = encodeSlug(params.slug);
  const page = source.getPage(slug, params.locale);
  if (!page) notFound();

  return {
    title: page.data.title,
    description: page.data.description,
  };
}
