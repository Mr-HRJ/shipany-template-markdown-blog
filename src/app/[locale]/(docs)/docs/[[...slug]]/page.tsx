import { notFound } from 'next/navigation';
import { getMDXComponents } from '@/mdx-components';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import {
  DocsBody,
  DocsDescription,
  DocsPage,
  DocsTitle,
} from 'fumadocs-ui/page';

import { source } from '@/core/docs/source';

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

export default async function DocsContentPage(props: {
  params: Promise<{ slug?: string[]; locale?: string }>;
}) {
  const params = await props.params;
  const slug = encodeSlug(params.slug);
  const page = source.getPage(slug, params.locale);

  if (!page) notFound();

  const MDXContent = page.data.body;

  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full}
      tableOfContent={{
        style: 'clerk',
      }}
    >
      <DocsTitle>{page.data.title}</DocsTitle>
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
