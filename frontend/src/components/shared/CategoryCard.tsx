import { useState, type ReactNode } from 'react';
import { ChevronDown, type LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

interface CategoryCardProps {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
  defaultOpen?: boolean;
  collapsible?: boolean;
}

export function CategoryCard({
  title,
  icon: Icon,
  children,
  defaultOpen = true,
  collapsible = true,
}: CategoryCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const toggleOpen = () => {
    if (collapsible) {
      setIsOpen((prev) => !prev);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
      {/* Header */}
      <div
        className={cn(
          'bg-primary-dark text-white px-4 py-3 flex items-center justify-between',
          collapsible && 'cursor-pointer hover:bg-blue-700 transition-colors'
        )}
        onClick={toggleOpen}
      >
        <div className="flex items-center space-x-3">
          {Icon && <Icon className="w-6 h-6" />}
          <h3 className="text-xl font-bold">{title}</h3>
        </div>

        {collapsible && (
          <ChevronDown
            className={cn('w-6 h-6 transition-transform', {
              'transform rotate-180': isOpen,
            })}
          />
        )}
      </div>

      {/* Content */}
      {isOpen && <div className="p-4">{children}</div>}
    </div>
  );
}
