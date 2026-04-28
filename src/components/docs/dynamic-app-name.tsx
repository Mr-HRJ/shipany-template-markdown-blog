'use client';

import { usePathname } from 'next/navigation';

const HANDBOOK_TITLES: Record<string, string> = {
  'shipany-two': 'ShipAny Two 手册',
  joyflix: 'JoyFlix 手册',
  nanobanana: 'Nano Banana 手册',
  gamiary: 'Gamiary 手册',
  blog: 'Blog 手册',
  'markdown-blog': 'Markdown Blog 手册',
  'gpt-image2': 'GPT Image 2 手册',
};

export function DynamicAppName({ fallback }: { fallback: string }) {
  const pathname = usePathname() || '';
  const m = pathname.match(/\/docs\/([^/]+)/);
  const slug = m?.[1];
  const title = slug && HANDBOOK_TITLES[slug] ? HANDBOOK_TITLES[slug] : fallback;
  return <>{title}</>;
}
