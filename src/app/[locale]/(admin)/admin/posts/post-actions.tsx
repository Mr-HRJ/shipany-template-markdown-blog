'use client';

import { useTranslations } from 'next-intl';
import { toast } from 'sonner';

import { Dropdown } from '@/shared/blocks/table/dropdown';
import { Post } from '@/shared/models/post';
import { NavItem } from '@/shared/types/blocks/common';

import {
  deletePostAction,
  togglePostPinAction,
  togglePostRecommendAction,
} from './actions';

export function PostActions({ item }: { item: Post }) {
  const t = useTranslations('admin.posts');

  const actions: NavItem[] = [
    {
      name: 'pin',
      title: item.isPinned ? t('list.buttons.unpin') : t('list.buttons.pin'),
      icon: item.isPinned ? 'RiUnpinLine' : 'RiPushpinLine',
      handler: async () => {
        const res = await togglePostPinAction(item.id, !item.isPinned);
        if (res.status === 'success') {
          toast.success(item.isPinned ? t('list.messages.unpinned') : t('list.messages.pinned'));
        } else {
          toast.error(res.message);
        }
      },
    },
    {
      name: 'recommend',
      title: item.isRecommended ? t('list.buttons.unrecommend') : t('list.buttons.recommend'),
      icon: item.isRecommended ? 'RiStarLine' : 'RiStarFill',
      handler: async () => {
        const res = await togglePostRecommendAction(item.id, !item.isRecommended);
        if (res.status === 'success') {
          toast.success(item.isRecommended ? t('list.messages.unrecommended') : t('list.messages.recommended'));
        } else {
          toast.error(res.message);
        }
      },
    },
    {
      name: 'edit',
      title: t('list.buttons.edit'),
      icon: 'RiEditLine',
      url: `/admin/posts/${item.id}/edit`,
    },
    {
      name: 'view',
      title: t('list.buttons.view'),
      icon: 'RiEyeLine',
      url: `/blog/${item.slug}`,
      target: '_blank',
    },
    {
      name: 'delete',
      title: t('list.buttons.delete'),
      icon: 'RiDeleteBinLine',
      handler: async () => {
        if (confirm(t('list.messages.delete_confirm') || 'Are you sure you want to delete this post?')) {
          const res = await deletePostAction(item.id);
          if (res.status === 'success') {
            toast.success(t('list.messages.deleted'));
          } else {
            toast.error(res.message);
          }
        }
      },
    },
  ];

  return <Dropdown value={actions} metadata={{}} />;
}
