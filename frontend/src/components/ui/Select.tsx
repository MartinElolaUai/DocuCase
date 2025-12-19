import { forwardRef, SelectHTMLAttributes } from 'react';
import clsx from 'clsx';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="label">{label}</label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={clsx(
              'input appearance-none pr-10',
              error && 'input-error',
              className
            )}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-surface-400">
            <ChevronDownIcon className="w-5 h-5" />
          </div>
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-400">{error}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;

