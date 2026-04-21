import { defineConfig, defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
});

export const pages = defineDocs({
  dir: 'content/pages',
});

export const posts = defineDocs({
  dir: 'content/posts',
});

export const logs = defineDocs({
  dir: 'content/logs',
});

export default defineConfig({
  mdxOptions: {
    rehypeCodeOptions: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
      // Use defaultLanguage for unknown language codes
      defaultLanguage: 'plaintext',
    },
    // Strip the default remarkImage plugin — it fetches remote image sizes at
    // build time and our R2 pub domain can be flaky on slow/Chinese networks.
    // Without it, <img> just keeps the string src and renders directly.
    remarkPlugins: (v) =>
      v.filter((p) => {
        const name = Array.isArray(p) ? (p[0] as any)?.name : (p as any)?.name;
        return name !== 'remarkImage';
      }),
  },
});
