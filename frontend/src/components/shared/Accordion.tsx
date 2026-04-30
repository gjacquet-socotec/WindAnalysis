import { useState, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface AccordionItem {
  id: string;
  title: string;
  content: ReactNode;
}

interface AccordionProps {
  items: AccordionItem[];
  defaultOpen?: string[];
  allowMultiple?: boolean;
}

export function Accordion({ items, defaultOpen = [], allowMultiple = true }: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set(defaultOpen));

  const toggleItem = (id: string) => {
    setOpenItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        if (!allowMultiple) {
          newSet.clear();
        }
        newSet.add(id);
      }
      return newSet;
    });
  };

  return (
    <div className="space-y-2">
      {items.map((item) => {
        const isOpen = openItems.has(item.id);

        return (
          <div key={item.id} className="border border-gray-200 rounded-md overflow-hidden">
            {/* Accordion Header */}
            <button
              onClick={() => toggleItem(item.id)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
            >
              <span className="font-semibold text-gray-900">{item.title}</span>
              <ChevronDown
                className={cn('w-5 h-5 text-gray-600 transition-transform', {
                  'transform rotate-180': isOpen,
                })}
              />
            </button>

            {/* Accordion Content */}
            {isOpen && (
              <div className="px-4 py-3 bg-white border-t border-gray-200">
                {item.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
