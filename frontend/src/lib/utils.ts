export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
};

export const calculateAnnualCost = (cost: number, billingCycle: string): number => {
  switch (billingCycle) {
    case 'monthly':
      return cost * 12;
    case 'yearly':
      return cost;
    case 'quarterly':
      return cost * 4;
    default:
      return cost * 12;
  }
};

export const getDaysUntilRenewal = (renewalDate: string | Date): number => {
  const now = new Date();
  const renewal = new Date(renewalDate);
  const diffTime = renewal.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};
