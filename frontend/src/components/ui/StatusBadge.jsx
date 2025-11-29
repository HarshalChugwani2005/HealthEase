import React from 'react';
import clsx from 'clsx';

const variants = {
  pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  paid: 'bg-green-100 text-green-800 border-green-200',
  admitted: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  discharged: 'bg-teal-100 text-teal-800 border-teal-200',
  critical: 'bg-red-100 text-red-800 border-red-200',
  default: 'bg-gray-100 text-gray-800 border-gray-200',
};

export const StatusBadge = ({ status = 'default', children, className }) => {
  const key = String(status).toLowerCase();
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border',
        variants[key] || variants.default,
        className
      )}
    >
      {children || String(status).toUpperCase()}
    </span>
  );
};
