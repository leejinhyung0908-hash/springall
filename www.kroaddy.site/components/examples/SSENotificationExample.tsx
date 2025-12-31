/**
 * SSE Notification Example
 * - Server-Sent Events를 사용한 실시간 알림 예제
 */

'use client';

import { useSSE } from '@/lib/hooks/useSSE';

interface Notification {
  id: string;
  message: string;
  timestamp: string;
  type: 'info' | 'warning' | 'error';
}

export function SSENotificationExample() {
  const { data: notifications, isConnected, error } = useSSE<Notification>(
    '/notifications',
    { enabled: true, reconnect: true }
  );

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">실시간 알림 (SSE)</h2>
        <div className="flex items-center gap-2">
          <span
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          Error: {error.message}
        </div>
      )}

      <div className="space-y-2">
        {notifications.length === 0 && (
          <p className="text-gray-500 text-center py-8">
            알림이 없습니다. 서버에서 알림을 기다리는 중...
          </p>
        )}

        {notifications.map((notification, index) => (
          <div
            key={`${notification.id}-${index}`}
            className={`p-3 rounded shadow ${
              notification.type === 'error'
                ? 'bg-red-50 border-l-4 border-red-500'
                : notification.type === 'warning'
                ? 'bg-yellow-50 border-l-4 border-yellow-500'
                : 'bg-blue-50 border-l-4 border-blue-500'
            }`}
          >
            <div className="flex justify-between items-start">
              <p className="font-medium">{notification.message}</p>
              <span className="text-xs text-gray-500">
                {new Date(notification.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

