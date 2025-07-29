import React from 'react';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/20/solid';
import clsx from 'clsx';

const MetricCard = ({ title, value, icon, trend, color = 'blue' }) => {
  const getColorClasses = (color) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50 dark:bg-blue-900/20',
        icon: 'text-blue-600 dark:text-blue-400',
        border: 'border-blue-200 dark:border-blue-800'
      },
      green: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        icon: 'text-green-600 dark:text-green-400',
        border: 'border-green-200 dark:border-green-800'
      },
      red: {
        bg: 'bg-red-50 dark:bg-red-900/20',
        icon: 'text-red-600 dark:text-red-400',
        border: 'border-red-200 dark:border-red-800'
      },
      yellow: {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        icon: 'text-yellow-600 dark:text-yellow-400',
        border: 'border-yellow-200 dark:border-yellow-800'
      },
      purple: {
        bg: 'bg-purple-50 dark:bg-purple-900/20',
        icon: 'text-purple-600 dark:text-purple-400',
        border: 'border-purple-200 dark:border-purple-800'
      }
    };
    return colors[color] || colors.blue;
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up':
        return <ArrowUpIcon className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowDownIcon className="h-4 w-4 text-red-500" />;
      case 'neutral':
      default:
        return <MinusIcon className="h-4 w-4 text-gray-400" />;
    }
  };

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'up':
        return 'text-green-600 dark:text-green-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
      case 'neutral':
      default:
        return 'text-gray-500 dark:text-gray-400';
    }
  };

  const colorClasses = getColorClasses(color);

  return (
    <div className="relative overflow-hidden rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700 transition-all duration-200 hover:shadow-md">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={clsx(
              'inline-flex items-center justify-center p-3 rounded-md',
              colorClasses.bg
            )}>
              <div className={clsx('h-6 w-6', colorClasses.icon)}>
                {icon}
              </div>
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {value}
                </div>
                {trend && (
                  <div className={clsx(
                    'ml-2 flex items-baseline text-sm font-semibold',
                    getTrendColor(trend.direction)
                  )}>
                    {getTrendIcon(trend.direction)}
                    <span className="ml-1">
                      {trend.value}
                    </span>
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
      
      {/* Subtle gradient overlay */}
      <div className={clsx(
        'absolute inset-x-0 bottom-0 h-1',
        colorClasses.bg.replace('bg-', 'bg-gradient-to-r from-').replace('/20', '/40'),
        'to-transparent'
      )} />
    </div>
  );
};

export default MetricCard;