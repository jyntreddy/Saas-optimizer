'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// TODO: Replace with real data from API
const mockData = [
  { month: 'Jan', spend: 450 },
  { month: 'Feb', spend: 520 },
  { month: 'Mar', spend: 480 },
  { month: 'Apr', spend: 650 },
  { month: 'May', spend: 590 },
  { month: 'Jun', spend: 720 },
];

export function SpendingChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={mockData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="spend" stroke="#0ea5e9" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
