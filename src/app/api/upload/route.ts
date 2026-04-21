import { NextRequest, NextResponse } from 'next/server';
import { getAllConfigs } from '@/shared/models/config';
import { getStorageServiceWithConfigs } from '@/shared/services/storage';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // 从数据库获取配置
    const configs = await getAllConfigs();
    
    // 检查R2配置
    if (!configs.r2_account_id || !configs.r2_access_key || !configs.r2_secret_key || !configs.r2_bucket_name) {
      return NextResponse.json(
        { error: 'R2 storage not configured in admin settings' },
        { status: 500 }
      );
    }

    // 使用配置创建 storage service
    const storageService = getStorageServiceWithConfigs(configs);

    // 生成文件名，添加日期文件夹
    const now = new Date();
    const dateFolder = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 8);
    const ext = file.name.split('.').pop();
    const key = `uploads/${dateFolder}/${timestamp}-${randomStr}.${ext}`;

    // 上传文件
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    const result = await storageService.uploadFile({
      body: buffer,
      key,
      contentType: file.type,
      disposition: 'inline',
    });

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Upload failed' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      url: result.url,
    });
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Upload failed' },
      { status: 500 }
    );
  }
}
