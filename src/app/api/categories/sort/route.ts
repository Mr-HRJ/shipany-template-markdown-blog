import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/core/db';
import { taxonomy } from '@/config/db/schema';
import { eq } from 'drizzle-orm';
import { getUserInfo } from '@/shared/models/user';

export async function POST(request: NextRequest) {
  try {
    const user = await getUserInfo();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { updates } = await request.json();

    if (!Array.isArray(updates)) {
      return NextResponse.json({ error: 'Invalid data' }, { status: 400 });
    }

    // Update each category's sort value
    await Promise.all(
      updates.map(({ id, sort }: { id: string; sort: number }) =>
        db().update(taxonomy).set({ sort }).where(eq(taxonomy.id, id))
      )
    );

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Sort categories error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
