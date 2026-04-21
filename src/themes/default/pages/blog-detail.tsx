import { Post as PostType } from '@/shared/types/blocks/blog';
import { BlogDetail } from '@/themes/default/blocks';

export default async function BlogDetailPage({
  locale,
  post,
  prevPost,
  nextPost,
}: {
  locale?: string;
  post: PostType;
  prevPost: { title: string; url: string } | null;
  nextPost: { title: string; url: string } | null;
}) {
  return <BlogDetail post={post} prevPost={prevPost} nextPost={nextPost} />;
}
