'use client';

import { useSpendingSummary } from '@/hooks/useAnalytics';
import { DollarSign, CreditCard, TrendingUp, Calendar } from 'lucide-react';

export function StatsCards() {
  const { data: summary, isLoading } = useSpendingSummary();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const stats = [
    {
      name: 'Monthly Spend',
      value: `$${summary?.total_monthly_spend.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Subscriptions',
      value: summary?.total_subscriptions || 0,
      icon: CreditCard,
      color: 'bg-green-500',
    },
    {
      name: 'Annual Cost',
      value: `$${summary?.estimated_annual_cost.toFixed(2) || '0.00'}`,
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      name: 'Yearly Spend',
      value: `$${summary?.total_yearly_spend.toFixed(2) || '0.00'}`,
      icon: Calendar,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold mt-2">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
