'use client';

import MarkdownIt from 'markdown-it';
import { slug } from 'github-slugger';
import { ImageViewer } from './image-viewer';
import { CodeBlockEnhancer } from './code-block-enhancer';

import './markdown.css';

function generateHeadingId(text: string): string {
  return slug(text);
}

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
});

// Custom renderer for headings with IDs
md.renderer.rules.heading_open = function (tokens, idx) {
  const token = tokens[idx];
  const level = token.markup.length;
  const nextToken = tokens[idx + 1];

  if (nextToken && nextToken.type === 'inline') {
    const headingText = nextToken.content;
    const id = generateHeadingId(headingText);
    return `<h${level} id="${id}">`;
  }

  return `<h${level}>`;
};

// Custom renderer for links - open external links in new tab, keep anchor links in same page
md.renderer.rules.link_open = function (tokens, idx, options, _env, renderer) {
  const token = tokens[idx];
  const hrefIndex = token.attrIndex('href');

  if (hrefIndex >= 0) {
    const href = token.attrs?.[hrefIndex]?.[1] || '';
    
    // Check if it's an anchor link (starts with #)
    if (href.startsWith('#')) {
      // Keep anchor links in the same page, remove any existing target attribute
      const targetIndex = token.attrIndex('target');
      if (targetIndex >= 0) {
        token.attrs?.splice(targetIndex, 1);
      }
    } else {
      // Open external/internal links in new tab
      token.attrSet('target', '_blank');
      token.attrSet('rel', 'noopener noreferrer');
    }
  }

  return renderer.renderToken(tokens, idx, options);
};

// Custom renderer for images - add lazy loading
md.renderer.rules.image = function (tokens, idx, options, _env, renderer) {
  const token = tokens[idx];
  token.attrSet('loading', 'lazy');
  return renderer.renderToken(tokens, idx, options);
};

interface MarkdownContentProps {
  content: string;
  id?: string;
}

/**
 * Client-side Markdown renderer for database posts with image viewer and code copy
 * This component uses markdown-it which works in all environments including Edge Runtime
 */
export function MarkdownContent({ content, id = 'nice' }: MarkdownContentProps) {
  const html = content ? md.render(content) : '';

  return (
    <ImageViewer>
      <CodeBlockEnhancer />
      <div id={id} className="markdown-body" dangerouslySetInnerHTML={{ __html: html }} />
    </ImageViewer>
  );
}
