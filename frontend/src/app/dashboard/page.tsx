'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { SubscriptionList } from '@/components/subscriptions/SubscriptionList';
import { SpendingChart } from '@/components/analytics/SpendingChart';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        
        <StatsCards />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Spending Overview</h2>
            <SpendingChart />
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Recent Subscriptions</h2>
            <SubscriptionList limit={5} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
