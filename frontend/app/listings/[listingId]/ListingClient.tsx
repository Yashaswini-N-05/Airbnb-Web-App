'use client';

import Container from '@/app/components/Container';
import ListingHead from '@/app/components/listings/ListingHead';
import ListingInfo from '@/app/components/listings/ListingInfo';
import ListingReservation from '@/app/components/listings/ListingReservation';
import { categories } from '@/app/components/navbar/Categories';
import useLoginModal from '@/app/hooks/useLoginModal';
import { SafeListing, SafeReservation, SafeUser } from '@/app/types';
import axios from 'axios';
import { differenceInCalendarDays, eachDayOfInterval } from 'date-fns';
import { useRouter } from 'next/navigation';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Range } from 'react-date-range';
import toast from 'react-hot-toast';

const initialDateRange = {
  startDate: new Date(),
  endDate: new Date(),
  key: 'selection',
};

interface Props {
  reservations?: SafeReservation[];
  listing: SafeListing & {
    user: SafeUser;
  };
  currentUser?: SafeUser | null;
}

const ListingClient: React.FC<Props> = ({ reservations = [], listing, currentUser }) => {
  const loginModal = useLoginModal();
  const router = useRouter();

  const disabledDates = useMemo(() => {
    let dates: Date[] = [];

    reservations.forEach((reservation) => {
      const range = eachDayOfInterval({
        start: new Date(reservation.startDate),
        end: new Date(reservation.endDate!),
      });

      dates = [...dates, ...range];
    });

    return dates;
  }, [reservations]);

  const [isLoading, setIsLoading] = useState(false);
  const [totalPrice, setTotalPrice] = useState(listing.price);
  const [dateRange, setDateRange] = useState<Range>(initialDateRange);

  const onCreateReservation = useCallback(() => {
    if (!currentUser) {
      return loginModal.onOpen();
    }

    setIsLoading(true);

    axios
      .post('/api/reservations', {
        totalPrice,
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        listingId: listing?.id,
      })
      .then(() => {
        toast.success('Listing reserved!');
        setDateRange(initialDateRange);
        router.push('/trips');
      })
      .catch((error) => {
        const errorMsg = error.response?.data?.error || 'Something went wrong.';
        toast.error(errorMsg);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [totalPrice, dateRange, listing?.id, router, currentUser, loginModal]);

  useEffect(() => {
    if (dateRange.startDate && dateRange.endDate) {
      const dayCount = differenceInCalendarDays(dateRange.endDate, dateRange.startDate);

      if (dayCount && listing.price) {
        setTotalPrice(dayCount * listing.price);
      } else {
        setTotalPrice(listing.price);
      }
    }
  }, [dateRange, listing.price]);

  const category = useMemo(() => {
    return categories.find((category) => category.label === listing.category);
  }, [listing.category]);

  return (
    <Container>
      <div className=" max-w-screen-lg mx-auto">
        <div className="flex flex-col gap-6">
          <ListingHead
            title={listing.title}
            imageSrc={listing.imageSrc}
            locationValue={listing.locationValue}
            id={listing.id}
            currentUser={currentUser}
          />
          <div className="grid grid-cols-1 md:grid-cols-7 md:gap-10 mt-6">
            <ListingInfo
              user={listing.user}
              category={category}
              description={listing.description}
              roomCount={listing.roomCount}
              guestCount={listing.guestCount}
              bathroomCount={listing.bathroomCount}
              locationValue={listing.locationValue}
            />
            <div className="order-first mb-10 md:order-last md:col-span-3">
              <ListingReservation
                price={listing.price}
                totalPrice={totalPrice}
                onChangeDate={(value) => setDateRange(value)}
                dateRange={dateRange}
                onSubmit={onCreateReservation}
                disabled={isLoading}
                disabledDates={disabledDates}
              />
            </div>
          </div>
          {listing.reviews && listing.reviews.length > 0 && (
            <div className="mt-8">
              <hr className="mb-8 border-neutral-200" />
              <h2 className="text-2xl font-semibold mb-6">Reviews</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {listing.reviews.map((review: any) => (
                  <div key={review.id} className="flex flex-col gap-2">
                    <div className="flex flex-row items-center gap-4">
                      <div className="font-semibold">{review.user?.first_name || 'Guest'}</div>
                      <div className="text-neutral-500 font-light text-sm">
                        {new Date(review.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex flex-row items-center gap-1 font-light text-sm">
                      <span>★</span>
                      <span>{review.rating.toFixed(1)}</span>
                    </div>
                    <div className="text-neutral-600">
                      {review.comment}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Container>
  );
};

export default ListingClient;
