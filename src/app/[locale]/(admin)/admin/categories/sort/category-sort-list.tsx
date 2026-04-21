'use client';

import { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { RiDraggable } from 'react-icons/ri';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';
import type { Taxonomy } from '@/shared/models/taxonomy';

function SortableItem({ category, sortLabel }: { category: Taxonomy; sortLabel: string }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: category.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-3 rounded-lg border bg-card p-4"
    >
      <button
        className="cursor-grab touch-none active:cursor-grabbing"
        {...attributes}
        {...listeners}
      >
        <RiDraggable className="h-5 w-5 text-muted-foreground" />
      </button>
      <div className="flex-1">
        <div className="font-medium">{category.title}</div>
        <div className="text-sm text-muted-foreground">{category.slug}</div>
      </div>
      <div className="text-sm text-muted-foreground">
        {sortLabel}: {category.sort}
      </div>
    </div>
  );
}

export function CategorySortList({
  categories: initialCategories,
}: {
  categories: Taxonomy[];
}) {
  const [categories, setCategories] = useState(initialCategories);
  const [isSaving, setIsSaving] = useState(false);
  const router = useRouter();
  const t = useTranslations('admin.categories.sort');

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setCategories((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updates = categories.map((cat, index) => ({
        id: cat.id,
        sort: index,
      }));

      const response = await fetch('/api/categories/sort', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates }),
      });

      if (!response.ok) {
        throw new Error(t('messages.save_failed'));
      }

      toast.success(t('messages.save_success'));
      router.push('/admin/categories');
      router.refresh();
    } catch (error) {
      toast.error(t('messages.save_failed'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          {t('description')}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => router.back()}
            className="rounded-md border px-4 py-2 text-sm hover:bg-default"
          >
            {t('buttons.cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isSaving ? t('buttons.saving') : t('buttons.save')}
          </button>
        </div>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={categories.map((c) => c.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {categories.map((category) => (
              <SortableItem key={category.id} category={category} sortLabel={t('sort_label')} />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
