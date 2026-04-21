'use client';

import { useEffect } from 'react';
import { toast } from 'sonner';

/**
 * Enhances code blocks with copy functionality
 */
export function CodeBlockEnhancer() {
  useEffect(() => {
    const addCopyButtons = () => {
      const codeBlocks = document.querySelectorAll('pre code');
      
      codeBlocks.forEach((codeBlock) => {
        const pre = codeBlock.parentElement;
        if (!pre || pre.querySelector('.code-copy-button')) return;

        // Create copy button
        const button = document.createElement('button');
        button.className = 'code-copy-button';
        button.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        `;
        button.title = 'Copy code';

        button.addEventListener('click', async () => {
          const code = codeBlock.textContent || '';
          try {
            await navigator.clipboard.writeText(code);
            button.innerHTML = `
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            `;
            toast.success('Code copied to clipboard');
            
            setTimeout(() => {
              button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              `;
            }, 2000);
          } catch (err) {
            toast.error('Failed to copy code');
          }
        });

        // Add button directly to pre element
        pre.style.position = 'relative';
        pre.appendChild(button);
      });
    };

    // Initial setup
    addCopyButtons();

    // Watch for content changes
    const observer = new MutationObserver(() => {
      addCopyButtons();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  return null;
}
