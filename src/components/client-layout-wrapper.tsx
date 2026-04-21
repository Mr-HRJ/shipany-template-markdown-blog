'use client';

import { useEffect } from 'react';

export function ClientLayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    document.body.classList.add('loaded');
  }, []);

  return <>{children}</>;
}
