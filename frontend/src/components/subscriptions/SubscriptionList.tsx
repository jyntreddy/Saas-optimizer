'use client';

import { useSubscriptions } from '@/hooks/useSubscriptions';

interface SubscriptionListProps {
  limit?: number;
}

export function SubscriptionList({ limit }: SubscriptionListProps) {
  const { data: subscriptions, isLoading } = useSubscriptions();

  if (isLoading) {
    return <div>Loading subscriptions...</div>;
  }

  const displaySubscriptions = limit 
    ? subscriptions?.slice(0, limit) 
    : subscriptions;

  return (
    <div className="space-y-3">
      {displaySubscriptions?.map((subscription) => (
        <div
          key={subscription.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
        >
          <div>
            <h3 className="font-semibold">{subscription.service_name}</h3>
            <p className="text-sm text-gray-600">
              {subscription.billing_cycle || 'monthly'}
            </p>
          </div>
          <div className="text-right">
            <p className="font-bold">${subscription.cost}</p>
            <span
              className={`text-xs px-2 py-1 rounded-full ${
                subscription.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {subscription.status}
            </span>
          </div>
        </div>
      ))}
      {(!displaySubscriptions || displaySubscriptions.length === 0) && (
        <p className="text-gray-500 text-center py-8">No subscriptions found</p>
      )}
    </div>
  );
}
