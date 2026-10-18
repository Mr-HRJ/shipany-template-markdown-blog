import Image from 'next/image';

import { Link } from '@/core/i18n/navigation';
import { cn } from '@/shared/lib/utils';
import { Brand as BrandType } from '@/shared/types/blocks/common';

export function BrandLogo({ brand }: { brand: BrandType }) {
  return (
    <Link
      href={brand.url || '/'}
      target={brand.target || '_self'}
      rel={brand.target === '_blank' ? 'noopener noreferrer' : undefined}
      className={cn(
        'focus-visible:ring-ring inline-flex min-w-0 items-center gap-3 rounded-lg focus-visible:ring-2 focus-visible:ring-offset-4 focus-visible:outline-none',
        brand.className
      )}
    >
      {brand.logo && (
        <Image
          src={brand.logo.src}
          alt={brand.title ? '' : brand.logo.alt || ''}
          width={brand.logo.width || 80}
          height={brand.logo.height || 80}
          className="size-9 shrink-0 rounded-xl object-cover"
          unoptimized={brand.logo.src.startsWith('http')}
          priority
        />
      )}
      {brand.title && (
        <span className="truncate text-lg font-semibold tracking-tight">
          {brand.title}
        </span>
      )}
    </Link>
  );
}
