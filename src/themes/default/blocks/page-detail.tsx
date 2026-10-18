import { CalendarIcon } from 'lucide-react';

import { MarkdownPreview } from '@/shared/blocks/common/markdown-preview';
import { type Post as PostType } from '@/shared/types/blocks/blog';

import '@/config/style/reading.css';

export async function PageDetail({ post }: { post: PostType }) {
  return (
    <section
      id={post.id}
      className="reading-page px-5 pt-28 pb-24 md:px-8 md:pt-36 md:pb-32"
    >
      <div className="mx-auto w-full max-w-[70ch]">
        <header className="border-border mb-10 border-b pb-10 md:mb-12 md:pb-12">
          <h1 className="text-foreground font-serif text-3xl leading-snug font-semibold tracking-tight text-balance md:text-5xl">
            {post.title}
          </h1>
          {post.description && (
            <p className="text-muted-foreground mt-6 text-base leading-8 md:text-lg">
              {post.description}
            </p>
          )}
          {post.created_at && (
            <div className="text-muted-foreground mt-5 flex items-center gap-2 text-sm">
              <CalendarIcon className="size-4" aria-hidden="true" />
              <span>{post.created_at}</span>
            </div>
          )}
        </header>
        <article className="reading-content min-w-0">
          {post.body ? (
            <div id="nice">{post.body}</div>
          ) : (
            post.content && <MarkdownPreview content={post.content} />
          )}
        </article>
      </div>
    </section>
  );
}
