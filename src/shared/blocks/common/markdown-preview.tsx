// components/MarkdownPreview.tsx
'use client';

import { useMemo, useEffect, useRef } from 'react';
import MarkdownIt from 'markdown-it';
import { slug as githubSlug } from 'github-slugger';

import '@/config/style/mdnice.css';

export interface TocItem {
  id: string;
  text: string;
  level: number;
}

export function getTocItems(content: string): TocItem[] {
  if (!content) return [];

  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  const toc: TocItem[] = [];
  const seenSlugs = new Map<string, number>();
  let match;

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const text = match[2].trim();
    
    let baseSlug = githubSlug(text);
    if (seenSlugs.has(baseSlug)) {
      const count = seenSlugs.get(baseSlug)! + 1;
      seenSlugs.set(baseSlug, count);
      baseSlug = `${baseSlug}-${count}`;
    } else {
      seenSlugs.set(baseSlug, 0);
    }

    toc.push({ id: baseSlug, text, level });
  }

  return toc;
}

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  typographer: false,
});

// Store seen slugs for the current render
let currentSeenSlugs: Map<string, number>;

// Custom renderer for headings with IDs
md.renderer.rules.heading_open = function (tokens, idx) {
  const token = tokens[idx];
  const level = token.markup.length;
  const nextToken = tokens[idx + 1];

  if (nextToken && nextToken.type === 'inline') {
    const headingText = nextToken.content;
    let baseSlug = githubSlug(headingText);
    
    if (currentSeenSlugs.has(baseSlug)) {
      const count = currentSeenSlugs.get(baseSlug)! + 1;
      currentSeenSlugs.set(baseSlug, count);
      baseSlug = `${baseSlug}-${count}`;
    } else {
      currentSeenSlugs.set(baseSlug, 0);
    }
    
    return `<h${level} id="${baseSlug}">`;
  }

  return `<h${level}>`;
};

// Custom renderer for links with nofollow
md.renderer.rules.link_open = function (tokens, idx, options, env, renderer) {
  const token = tokens[idx];
  const hrefIndex = token.attrIndex('href');

  if (hrefIndex >= 0) {
    const href = token.attrGet('href');
    // Add nofollow to all links
    token.attrSet('rel', 'nofollow');
    // Optionally add target="_blank" for external links
    if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
      token.attrSet('target', '_blank');
    }
  }

  return renderer.renderToken(tokens, idx, options);
};

// Custom renderer for images with lazy loading
md.renderer.rules.image = function (tokens, idx, options, env, self) {
  const token = tokens[idx];
  const src = token.attrGet('src');
  const alt = token.content;
  const title = token.attrGet('title');
  
  return `<img src="${src}" alt="${alt}" title="${title || ''}" loading="lazy" class="lazy-image" />`;
};

interface MarkdownPreviewProps {
  content: string;
}

export function MarkdownPreview({ content }: MarkdownPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  const html = useMemo(() => {
    if (!content) return '';
    
    // Fix common markdown formatting issues
    let fixedContent = content;
    
    // Protect ** by temporarily replacing with placeholder
    fixedContent = fixedContent.replace(/\*\*/g, '§§');
    
    // Replace all remaining * with newline + list marker
    fixedContent = fixedContent.replace(/\*\s+/g, '\n   - ');
    
    // Restore **
    fixedContent = fixedContent.replace(/§§/g, '**');
    
    // Add newlines before numbered items
    fixedContent = fixedContent.replace(/(\d+)\.\s+/g, '\n\n$1. ');
    
    // Reset seen slugs for each render
    currentSeenSlugs = new Map();
    return md.render(fixedContent);
  }, [content]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Handle images that might have already loaded (cached)
    const images = container.querySelectorAll('img.lazy-image');
    images.forEach((img) => {
      const imgElement = img as HTMLImageElement;
      if (imgElement.complete) {
        imgElement.style.opacity = '1';
      } else {
        imgElement.addEventListener('load', () => {
          imgElement.style.opacity = '1';
        });
      }
    });
  }, [html]);

  return (
    <div
      id="nice"
      ref={containerRef}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
