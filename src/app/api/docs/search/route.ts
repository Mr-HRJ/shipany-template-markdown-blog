import { createFromSource } from 'fumadocs-core/search/server';

import { source } from '@/core/docs/source';

export const { GET } = createFromSource(source, {
  // Keep each locale's pages and URLs while using a tokenizer supported by Orama.
  localeMap: { en: 'english', zh: 'english' },
});
