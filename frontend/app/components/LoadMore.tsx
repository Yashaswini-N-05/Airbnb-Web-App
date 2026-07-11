'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import qs from 'query-string';
import { useCallback } from 'react';
import Button from './Button';

interface LoadMoreProps {
  hasNextPage?: boolean;
}

const LoadMore: React.FC<LoadMoreProps> = ({ hasNextPage = true }) => {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleNextPage = useCallback(() => {
    let currentQuery: any = {};

    if (searchParams) {
      currentQuery = qs.parse(searchParams.toString());
    }

    const currentPage = parseInt((currentQuery.page as string) || '1', 10);
    const updatedQuery: any = {
      ...currentQuery,
      page: currentPage + 1,
    };

    const url = qs.stringifyUrl(
      {
        url: '/',
        query: updatedQuery,
      },
      { skipNull: true }
    );

    router.push(url);
  }, [router, searchParams]);

  if (!hasNextPage) return null;

  return (
    <div className="flex justify-center mt-10 w-full">
      <div className="w-48">
        <Button outline label="Load More" onClick={handleNextPage} />
      </div>
    </div>
  );
};

export default LoadMore;
