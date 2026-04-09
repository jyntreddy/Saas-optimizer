import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { SpendingSummary } from '@/types';

export function useSpendingSummary() {
  return useQuery({
    queryKey: ['spending-summary'],
    queryFn: async () => {
      const { data } = await apiClient.get<SpendingSummary>('/analytics/spending-summary');
      return data;
    },
  });
}
