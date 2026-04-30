import { useState, useMemo } from 'react';

interface UsePaginationProps {
  totalItems: number;
  itemsPerPage?: number;
}

interface UsePaginationReturn<T> {
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  startIndex: number;
  endIndex: number;
  canGoNext: boolean;
  canGoPrevious: boolean;
  goToPage: (page: number) => void;
  goNext: () => void;
  goPrevious: () => void;
  goToFirst: () => void;
  goToLast: () => void;
  getCurrentPageItems: (items: T[]) => T[];
}

/**
 * Hook for pagination logic
 * Automatically manages page state and navigation
 */
export function usePagination<T = any>({
  totalItems,
  itemsPerPage = 10,
}: UsePaginationProps): UsePaginationReturn<T> {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));

  // Ensure current page is valid when totalItems changes
  const validCurrentPage = useMemo(() => {
    return Math.min(currentPage, totalPages);
  }, [currentPage, totalPages]);

  const startIndex = (validCurrentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

  const canGoNext = validCurrentPage < totalPages;
  const canGoPrevious = validCurrentPage > 1;

  const goToPage = (page: number) => {
    const validPage = Math.max(1, Math.min(page, totalPages));
    setCurrentPage(validPage);
  };

  const goNext = () => {
    if (canGoNext) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const goPrevious = () => {
    if (canGoPrevious) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  const goToFirst = () => {
    setCurrentPage(1);
  };

  const goToLast = () => {
    setCurrentPage(totalPages);
  };

  const getCurrentPageItems = (items: T[]): T[] => {
    return items.slice(startIndex, endIndex);
  };

  return {
    currentPage: validCurrentPage,
    totalPages,
    itemsPerPage,
    startIndex,
    endIndex,
    canGoNext,
    canGoPrevious,
    goToPage,
    goNext,
    goPrevious,
    goToFirst,
    goToLast,
    getCurrentPageItems,
  };
}
