export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  service_name: string;
  provider?: string;
  cost: number;
  billing_cycle?: string;
  status: 'active' | 'cancelled' | 'expired' | 'trial';
  start_date?: string;
  renewal_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface SpendingSummary {
  total_monthly_spend: number;
  total_yearly_spend: number;
  total_subscriptions: number;
  estimated_annual_cost: number;
}

export interface Recommendation {
  type: string;
  subscription_id: number;
  service_name: string;
  message: string;
  potential_savings: number;
}
