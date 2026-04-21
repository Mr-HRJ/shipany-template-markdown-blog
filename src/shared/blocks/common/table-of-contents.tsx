'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { cn } from '@/shared/lib/utils';
import type { TOCItemType } from '@/core/docs/toc';

interface TableOfContentsProps {
  toc: TOCItemType[];
  className?: string;
}

export function TableOfContents({ toc, className }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>('');
  const containerRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<Map<string, HTMLAnchorElement>>(new Map());
  const userClickedRef = useRef(false);
  const clickedIdRef = useRef<string>('');

  // Scroll the active item into view within the TOC container
  const scrollActiveIntoView = useCallback((id: string) => {
    const itemEl = itemRefs.current.get(id);
    const containerEl = containerRef.current;
    if (itemEl && containerEl) {
      const containerRect = containerEl.getBoundingClientRect();
      const itemRect = itemEl.getBoundingClientRect();
      
      if (itemRect.top < containerRect.top || itemRect.bottom > containerRect.bottom) {
        itemEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, []);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleScroll = () => {
      // 用户点击后完全忽略滚动监听
      if (userClickedRef.current) {
        return;
      }

      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const headings = Array.from(document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]'));
        
        if (headings.length === 0) return;
        
        const tocIds = new Set(toc.map(item => item.url.replace('#', '')));
        let activeHeading: Element | null = null;
        
        for (let i = headings.length - 1; i >= 0; i--) {
          const heading = headings[i];
          const rect = heading.getBoundingClientRect();
          
          if (!tocIds.has(heading.id)) continue;
          
          if (rect.top <= 120) {
            activeHeading = heading;
            break;
          }
        }
        
        if (!activeHeading) {
          for (const heading of headings) {
            if (tocIds.has(heading.id)) {
              activeHeading = heading;
              break;
            }
          }
        }

        if (activeHeading && activeHeading.id) {
          const id = activeHeading.id;
          if (id !== activeId) {
            setActiveId(id);
            scrollActiveIntoView(id);
          }
        }
      }, 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearTimeout(timeoutId);
    };
  }, [scrollActiveIntoView, activeId, toc]);

  if (!toc?.length) return null;

  const getDepthStyles = (depth: number) => {
    const baseStyles: Record<number, string> = {
      1: 'pl-3 text-sm font-semibold',
      2: 'pl-3 text-sm font-medium',
      3: 'pl-6 text-xs',
      4: 'pl-9 text-xs opacity-80',
    };
    return baseStyles[depth] || baseStyles[2];
  };

  const setItemRef = useCallback((id: string, el: HTMLAnchorElement | null) => {
    if (el) {
      itemRefs.current.set(id, el);
    } else {
      itemRefs.current.delete(id);
    }
  }, []);

  return (
    <div 
      ref={containerRef}
      className={cn('flex flex-col space-y-1 text-sm max-h-[calc(100vh-200px)] overflow-y-auto scrollbar-thin', className)}
    >
      {toc.map((item) => {
        const id = item.url.replace('#', '');
        const isActive = activeId === id;
        
        return (
          <a
            key={item.url}
            ref={(el) => setItemRef(id, el)}
            href={item.url}
            className={cn(
              'block py-1.5 transition-all duration-200 border-l-2 hover:text-foreground',
              getDepthStyles(item.depth),
              isActive
                ? 'text-primary border-primary bg-primary/5'
                : 'text-muted-foreground border-transparent hover:border-muted-foreground/30'
            )}
            onClick={(e) => {
              e.preventDefault();
              
              // 立即更新选中状态
              clickedIdRef.current = id;
              setActiveId(id);
              
              // 禁用滚动监听
              userClickedRef.current = true;
              
              const element = document.getElementById(id);
              if (!element) return;
              
              // 使用instant滚动，避免smooth动画期间的问题
              const targetY = element.getBoundingClientRect().top + window.scrollY - 100;
              window.scrollTo({
                top: targetY,
                behavior: 'instant'
              });
              
              // 等待DOM更新和图片加载
              const checkAndAdjust = () => {
                const el = document.getElementById(id);
                if (!el) return;
                
                const rect = el.getBoundingClientRect();
                const currentTop = rect.top;
                
                // 如果位置偏差超过5px，重新调整
                if (Math.abs(currentTop - 100) > 5) {
                  const newTargetY = window.scrollY + currentTop - 100;
                  window.scrollTo({
                    top: newTargetY,
                    behavior: 'instant'
                  });
                }
              };
              
              // 多次检查和调整，应对懒加载图片
              setTimeout(checkAndAdjust, 100);
              setTimeout(checkAndAdjust, 300);
              setTimeout(checkAndAdjust, 600);
              setTimeout(checkAndAdjust, 1000);
              
              // 2秒后恢复滚动监听
              setTimeout(() => {
                userClickedRef.current = false;
              }, 2000);
            }}
          >
            {item.title}
          </a>
        );
      })}
    </div>
  );
}
