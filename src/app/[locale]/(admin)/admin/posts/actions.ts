'use server';

import { revalidatePath } from 'next/cache';
import { deletePost, togglePostPin, togglePostRecommend } from '@/shared/models/post';

export async function togglePostPinAction(id: string, isPinned: boolean) {
  try {
    await togglePostPin(id, isPinned);
    revalidatePath('/admin/posts');
    return { status: 'success' };
  } catch (error) {
    console.error('togglePostPinAction error:', error);
    return { status: 'error', message: 'Failed to pin/unpin post' };
  }
}

export async function togglePostRecommendAction(id: string, isRecommended: boolean) {
  try {
    await togglePostRecommend(id, isRecommended);
    revalidatePath('/admin/posts');
    return { status: 'success' };
  } catch (error) {
    console.error('togglePostRecommendAction error:', error);
    return { status: 'error', message: 'Failed to recommend/unrecommend post' };
  }
}

export async function deletePostAction(id: string) {
  try {
    await deletePost(id);
    revalidatePath('/admin/posts');
    return { status: 'success' };
  } catch (error) {
    console.error('deletePostAction error:', error);
    return { status: 'error', message: 'Failed to delete post' };
  }
}
