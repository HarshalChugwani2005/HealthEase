import React from 'react';
import clsx from 'clsx';

export const Card = ({ children, className = '', ...props }) => {
    return (
        <div
            className={clsx(
                'bg-white rounded-xl shadow-lg p-6',
                'border border-gray-100',
                'hover:shadow-xl transition-shadow duration-300',
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};

export const CardHeader = ({ children, className = '' }) => {
    return (
        <div className={clsx('mb-4 pb-4 border-b border-gray-200', className)}>
            {children}
        </div>
    );
};

export const CardTitle = ({ children, className = '' }) => {
    return (
        <h3 className={clsx('text-xl font-bold text-gray-900', className)}>
            {children}
        </h3>
    );
};

export const CardContent = ({ children, className = '' }) => {
    return <div className={clsx('', className)}>{children}</div>;
};

export default Card;
