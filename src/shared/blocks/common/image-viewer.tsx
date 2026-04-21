'use client';

import { useEffect, useRef, useState } from 'react';
import Lightbox from 'yet-another-react-lightbox';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import 'yet-another-react-lightbox/styles.css';

interface ImageViewerProps {
  children: React.ReactNode;
  className?: string;
}

export function ImageViewer({ children, className }: ImageViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const [images, setImages] = useState<{ src: string; alt?: string }[]>([]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateImages = () => {
      const imgElements = container.querySelectorAll('img');
      const imageList = Array.from(imgElements).map((img) => ({
        src: img.currentSrc || img.src,
        alt: img.alt || '',
      }));
      setImages(imageList);
      
      // Add cursor pointer to images
      imgElements.forEach((img) => {
        img.style.cursor = 'zoom-in';
      });
    };

    updateImages();

    const observer = new MutationObserver(updateImages);
    observer.observe(container, { childList: true, subtree: true, attributes: true, attributeFilter: ['src', 'srcset'] });

    const handleClick = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'IMG') {
        const img = target as HTMLImageElement;
        const imgElements = container.querySelectorAll('img');
        const imgIndex = Array.from(imgElements).indexOf(img);

        if (imgIndex !== -1) {
          e.preventDefault();
          setIndex(imgIndex);
          setOpen(true);
        }
      }
    };

    container.addEventListener('click', handleClick);

    return () => {
      container.removeEventListener('click', handleClick);
      observer.disconnect();
    };
  }, [children]);

  return (
    <>
      <div ref={containerRef} className={className}>
        {children}
      </div>
      {images.length > 0 && (
        <Lightbox
          open={open}
          close={() => setOpen(false)}
          index={index}
          slides={images}
          plugins={[Zoom]}
          zoom={{ maxZoomPixelRatio: 3 }}
          animation={{ fade: 300 }}
          carousel={{ finite: false }}
          controller={{ closeOnBackdropClick: true }}
        />
      )}
    </>
  );
}
