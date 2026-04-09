export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    refresh: '/auth/refresh',
  },
  users: {
    list: '/users',
    create: '/users',
    me: '/users/me',
    byId: (id: number) => `/users/${id}`,
  },
  subscriptions: {
    list: '/subscriptions',
    create: '/subscriptions',
    byId: (id: number) => `/subscriptions/${id}`,
    update: (id: number) => `/subscriptions/${id}`,
    delete: (id: number) => `/subscriptions/${id}`,
  },
  analytics: {
    summary: '/analytics/spending-summary',
    byCategory: '/analytics/spending-by-category',
    trends: '/analytics/trends',
  },
  recommendations: {
    costSavings: '/recommendations/cost-savings',
    duplicates: '/recommendations/duplicate-services',
    unused: '/recommendations/unused-subscriptions',
  },
} as const;
