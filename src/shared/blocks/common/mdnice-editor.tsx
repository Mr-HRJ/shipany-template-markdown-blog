'use client';

import { useEffect, useRef, useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { EditorView } from '@codemirror/view';
import { mdMirrorExtension } from '@/config/codemirror-theme';
import MarkdownIt from 'markdown-it';
// @ts-ignore
import markdownItKatex from 'markdown-it-katex';
import 'katex/dist/katex.min.css';
import '@/config/style/mdnice.css';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';
import { Tabs, TabsList, TabsTrigger } from '@/shared/components/ui/tabs';
import { Monitor, Smartphone } from 'lucide-react';

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  typographer: false,
}).use(markdownItKatex);

type PreviewMode = 'pc' | 'mobile';

const compressImage = async (file: File, quality = 0.7): Promise<File> => {
  if (!file.type.startsWith('image/')) return file;

  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target?.result as string;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          resolve(file);
          return;
        }

        let width = img.width;
        let height = img.height;
        const maxDimension = 1920;

        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = (height / width) * maxDimension;
            width = maxDimension;
          } else {
            width = (width / height) * maxDimension;
            height = maxDimension;
          }
        }

        canvas.width = width;
        canvas.height = height;
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(
          (blob) => {
            if (!blob || blob.size >= file.size) {
              resolve(file);
              return;
            }

            const newName = file.name.replace(/\.[^/.]+$/, '') + '.jpg';
            const compressedFile = new File([blob], newName, {
              type: 'image/jpeg',
              lastModified: Date.now(),
            });
            
            console.log(`Image compressed: ${file.size} -> ${compressedFile.size} bytes`);
            resolve(compressedFile);
          },
          'image/jpeg',
          quality
        );
      };
      img.onerror = () => resolve(file);
    };
    reader.onerror = () => resolve(file);
  });
};

export function MdniceEditor({
  value,
  onChange,
  placeholder,
  minHeight = 400,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: number;
  showToolbar?: boolean;
}) {
  const t = useTranslations('common.editor');
  const [previewHtml, setPreviewHtml] = useState('');
  const previewRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);
  const [previewMode, setPreviewMode] = useState<PreviewMode>('pc');
  const editorRef = useRef<any>(null);
  const isSyncingRef = useRef(false);

  const handlePaste = async (event: ClipboardEvent) => {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        event.preventDefault();
        const file = item.getAsFile();
        if (!file) continue;

        const editor = editorRef.current?.view;
        const cursorPosition = editor?.state.selection.main.head || 0;

        const toastId = `upload-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        const fileName = file.name || t('image');
        
        toast.loading(t('compressing_and_uploading', { fileName }), { id: toastId });

        try {
          const compressedFile = await compressImage(file);
          
          const formData = new FormData();
          formData.append('file', compressedFile);

          const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
          });

          const result = await response.json();
          if (result.success && result.url) {
            toast.success(t('upload_success'), { id: toastId });
            
            const imageMarkdown = `![image](${result.url})\n`;
            const currentValue = value || '';
            
            const newValue = 
              currentValue.slice(0, cursorPosition) + 
              imageMarkdown + 
              currentValue.slice(cursorPosition);
            
            onChange(newValue);
            
            // 设置光标到插入内容的末尾
            requestAnimationFrame(() => {
              if (editor) {
                const newCursorPos = cursorPosition + imageMarkdown.length;
                editor.dispatch({
                  selection: { anchor: newCursorPos, head: newCursorPos },
                  scrollIntoView: true
                });
                editor.focus();
              }
            });
          } else {
            toast.error(`${t('upload_failed')}: ${result.error || 'unknown error'}`, { id: toastId });
          }
        } catch (error) {
          console.error('Upload error:', error);
          toast.error(t('upload_failed'), { id: toastId });
        }
      }
    }
  };

  useEffect(() => {
    setMounted(true);
    if (value) {
      setPreviewHtml(md.render(value));
    }
  }, []);

  useEffect(() => {
    if (value !== undefined) {
      setPreviewHtml(md.render(value || ''));
    }
  }, [value]);

  useEffect(() => {
    const editor = editorRef.current?.view?.dom;
    if (editor) {
      editor.addEventListener('paste', handlePaste);
      return () => editor.removeEventListener('paste', handlePaste);
    }
  }, [value]);

  useEffect(() => {
    if (!mounted) return;
    
    const timer = setTimeout(() => {
      const editorScroll = editorRef.current?.view?.scrollDOM;
      const previewScroll = previewRef.current;

      if (!editorScroll || !previewScroll) return;

      // 监听预览区域图片加载完成
      const waitForImages = () => {
        const images = previewScroll.querySelectorAll('img');
        const promises = Array.from(images).map(img => {
          if (img.complete) return Promise.resolve();
          return new Promise(resolve => {
            img.addEventListener('load', resolve, { once: true });
            img.addEventListener('error', resolve, { once: true });
          });
        });
        return Promise.all(promises);
      };

      const handleEditorScroll = () => {
        if (isSyncingRef.current) return;
        isSyncingRef.current = true;
        
        // 等待图片加载后再同步滚动
        waitForImages().then(() => {
          const scrollPercentage = editorScroll.scrollTop / (editorScroll.scrollHeight - editorScroll.clientHeight || 1);
          if (!isNaN(scrollPercentage)) {
            previewScroll.scrollTop = scrollPercentage * (previewScroll.scrollHeight - previewScroll.clientHeight);
          }
          requestAnimationFrame(() => { isSyncingRef.current = false; });
        });
      };

      const handlePreviewScroll = () => {
        if (isSyncingRef.current) return;
        isSyncingRef.current = true;
        
        const scrollPercentage = previewScroll.scrollTop / (previewScroll.scrollHeight - previewScroll.clientHeight || 1);
        if (!isNaN(scrollPercentage)) {
          editorScroll.scrollTop = scrollPercentage * (editorScroll.scrollHeight - editorScroll.clientHeight);
        }
        
        requestAnimationFrame(() => { isSyncingRef.current = false; });
      };

      editorScroll.addEventListener('scroll', handleEditorScroll, { passive: true });
      previewScroll.addEventListener('scroll', handlePreviewScroll, { passive: true });

      return () => {
        editorScroll.removeEventListener('scroll', handleEditorScroll);
        previewScroll.removeEventListener('scroll', handlePreviewScroll);
      };
    }, 100);

    return () => clearTimeout(timer);
  }, [mounted, previewHtml]);

  if (!mounted) {
    return null;
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border bg-card p-3">
      <div className="flex items-center justify-end ">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{t('preview_mode')}</span>
          <Tabs value={previewMode} onValueChange={(v) => setPreviewMode(v as PreviewMode)}>
            <TabsList>
              <TabsTrigger value="pc" className="gap-1">
                <Monitor className="h-4 w-4" />
                {t('pc')}
              </TabsTrigger>
              <TabsTrigger value="mobile" className="gap-1">
                <Smartphone className="h-4 w-4" />
                {t('mobile')}
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>

      {/* 编辑器和预览区域 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 编辑器 */}
        <div className="flex flex-col">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-foreground">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            {t('editor')}
          </div>
          <div className="overflow-hidden rounded-lg border shadow-sm">
            <CodeMirror
              ref={editorRef}
              value={value}
              height="600px"
              extensions={[markdown(), mdMirrorExtension, EditorView.lineWrapping]}
              onChange={(val) => onChange(val)}
              placeholder={placeholder}
              basicSetup={{
                lineNumbers: true,
                highlightActiveLineGutter: false,
                highlightActiveLine: false,
                foldGutter: true,
              }}
            />
          </div>
        </div>

        {/* 预览区域 */}
        <div className="flex flex-col">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-foreground">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            {t('real_time_preview')}
          </div>
          <div
            ref={previewRef}
            className={`markdown-preview overflow-auto rounded-lg border bg-background shadow-sm ${
              previewMode === 'mobile' ? 'max-w-[375px] min-w-[300px] mx-auto' : ''
            }`}
            style={{ height: '600px', padding: previewMode === 'mobile' ? '16px' : '24px' }}
          >
            {previewHtml ? (
              <div
                id="nice"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <svg className="mx-auto mb-3 h-12 w-12 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-sm">{t('start_typing')}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
