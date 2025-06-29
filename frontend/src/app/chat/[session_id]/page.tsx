'use client';

import ChatSection from '@/components/chat/Section';
import { useAuth } from '@/context/AuthContext';
import { use } from 'react';

export default function Home({ params }: { params: Promise<{ session_id: string }> }) {
  const { user } = useAuth();

  const { session_id: sessionId } = use(params);

  return user ? (
    <ChatSection sessionId={sessionId} />
  ) : (
    <div>Hello, World! No user logged in!</div>
  );
}
