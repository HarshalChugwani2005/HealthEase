import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
  AreaChart,
  Area,
} from 'recharts';

export const LineChartWidget = ({ data = [], xKey = 'label', yKey = 'value', color = '#1C6DD0', height = 220 }) => (
  <div className="w-full h-full">
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const BarChartWidget = ({ data = [], xKey = 'label', bars = [{ key: 'value', color: '#00B8A9' }], stacked = false, height = 220 }) => (
  <div className="w-full h-full">
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {bars.map((b) => (
          <Bar key={b.key} dataKey={b.key} stackId={stacked ? 'a' : undefined} fill={b.color} radius={[6,6,0,0]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export const AreaChartWidget = ({ data = [], xKey = 'label', yKey = 'value', color = '#6C63FF', height = 220 }) => (
  <div className="w-full h-full">
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Area type="monotone" dataKey={yKey} stroke={color} fillOpacity={1} fill="url(#colorArea)" />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);
