'use client';

import { MoreHorizontal } from 'lucide-react';

import { Link } from '@/core/i18n/navigation';
import { SmartIcon } from '@/shared/blocks/common/smart-icon';
import { Button } from '@/shared/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/components/ui/dropdown-menu';
import { NavItem } from '@/shared/types/blocks/common';

export function Dropdown({
  value,
  placeholder,
  metadata,
  className,
}: {
  value: NavItem[];
  placeholder?: string;
  metadata: Record<string, any>;
  className?: string;
}) {
  if (!value || value.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="data-[state=open]:bg-muted flex h-8 w-8 p-0"
        >
          <MoreHorizontal />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[160px]">
        {value?.map((item) => {
          const content = (
            <div className="flex w-full items-center gap-2">
              {item.icon && (
                <SmartIcon name={item.icon as string} className="h-4 w-4" />
              )}
              {item.title}
            </div>
          );

          if (item.url) {
            return (
              <DropdownMenuItem key={item.title} asChild>
                <Link
                  href={item.url || ''}
                  target={item.target || '_self'}
                  className="flex w-full items-center gap-2"
                >
                  {content}
                </Link>
              </DropdownMenuItem>
            );
          }

          if (item.handler || item.onClick) {
            return (
              <DropdownMenuItem
                key={item.title}
                onClick={async () => {
                  if (item.handler) {
                    await item.handler();
                  } else if (item.onClick) {
                    item.onClick();
                  }
                }}
              >
                {content}
              </DropdownMenuItem>
            );
          }

          return (
            <DropdownMenuItem key={item.title}>{content}</DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
