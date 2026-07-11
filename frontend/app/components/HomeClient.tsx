'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { BsMap, BsListUl } from 'react-icons/bs';

import Container from './Container';
import ListingCard from './listings/ListingCard';
import LoadMore from './LoadMore';
import { SafeListing, SafeUser } from '../types';

// Dynamically import Map to prevent SSR errors
const ListingsMap = dynamic(() => import('./ListingsMap'), {
  ssr: false,
});

interface HomeClientProps {
  listings: SafeListing[];
  currentUser?: SafeUser | null;
}

const HomeClient: React.FC<HomeClientProps> = ({ listings, currentUser }) => {
  const [showMap, setShowMap] = useState(false);

  return (
    <Container>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setShowMap((prev) => !prev)}
        className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-neutral-900 dark:bg-neutral-800 text-white px-6 py-3 rounded-full flex items-center gap-2 shadow-xl hover:scale-105 transition duration-200 z-50 font-semibold text-sm tracking-wide border border-neutral-700/50"
      >
        {showMap ? (
          <>
            <span>Show list</span>
            <BsListUl size={16} />
          </>
        ) : (
          <>
            <span>Show map</span>
            <BsMap size={16} />
          </>
        )}
      </button>

      {showMap ? (
        <div className="pt-24 min-h-[80vh] flex flex-col justify-center items-center">
          <ListingsMap listings={listings} />
        </div>
      ) : (
        <>
          <div className="pt-24 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-8">
            {listings.map((listing: SafeListing) => (
              <ListingCard
                currentUser={currentUser}
                key={listing.id}
                data={listing}
              />
            ))}
          </div>
          <LoadMore hasNextPage={listings.length >= 20} />
        </>
      )}
    </Container>
  );
};

export default HomeClient;
