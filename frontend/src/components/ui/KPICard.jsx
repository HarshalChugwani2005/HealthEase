import React from 'react';
import clsx from 'clsx';

export const KPICard = ({
  title,
  value,
  sublabel,
  trend,
  icon: Icon,
  tone = 'default',
  className,
}) => {
  const tones = {
    default: 'bg-white',
    info: 'bg-blue-50',
    success: 'bg-emerald-50',
    warn: 'bg-amber-50',
  };

  const toneText = {
    default: 'text-gray-900',
    info: 'text-blue-700',
    success: 'text-emerald-700',
    warn: 'text-amber-700',
  };

  return (
    <div className={clsx('rounded-xl p-5 border card-shadow', tones[tone], className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 font-medium">{title}</p>
          <p className={clsx('mt-2 text-3xl font-bold', toneText[tone])}>{value}</p>
          {sublabel && <p className="text-xs text-gray-500 mt-1">{sublabel}</p>}
        </div>
        {Icon && (
          <div className="h-10 w-10 rounded-lg bg-white/70 flex items-center justify-center border">
            <Icon className={clsx('h-5 w-5', toneText[tone])} />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 text-xs">
          <span className={clsx(trend.delta >= 0 ? 'text-emerald-600' : 'text-red-600', 'font-semibold')}>
            {trend.delta >= 0 ? '▲' : '▼'} {Math.abs(trend.delta)}%
          </span>
          <span className="text-gray-500"> vs last period</span>
        </div>
      )}
    </div>
  );
};
