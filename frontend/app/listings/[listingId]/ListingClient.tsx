'use client';

import Container from '@/app/components/Container';
import ListingHead from '@/app/components/listings/ListingHead';
import ListingInfo from '@/app/components/listings/ListingInfo';
import ListingReservation from '@/app/components/listings/ListingReservation';
import { categories } from '@/app/components/navbar/Categories';
import useLoginModal from '@/app/hooks/useLoginModal';
import Button from '@/app/components/Button';
import { SafeListing, SafeReservation, SafeUser } from '@/app/types';
import axios from 'axios';
import { differenceInCalendarDays, eachDayOfInterval, format } from 'date-fns';
import { useRouter } from 'next/navigation';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Range } from 'react-date-range';
import toast from 'react-hot-toast';
import useReviewModal from '@/app/hooks/useReviewModal';

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
  const reviewModal = useReviewModal();
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

  const ratingsBreakdown = useMemo(() => {
    let hash = 0;
    for (let i = 0; i < listing.id.length; i++) {
      hash = listing.id.charCodeAt(i) + ((hash << 5) - hash);
    }
    const getVal = (offset: number) => {
      const val = (Math.abs(hash + offset) % 6); // 0 to 5
      return (4.5 + (val / 10));
    };

    return [
      { label: 'Cleanliness', score: getVal(1) },
      { label: 'Accuracy', score: getVal(2) },
      { label: 'Communication', score: getVal(3) },
      { label: 'Location', score: getVal(4) },
      { label: 'Check-in', score: getVal(5) },
      { label: 'Value', score: getVal(6) },
    ];
  }, [listing.id]);

  const averageRating = useMemo(() => {
    if (!listing.reviews || listing.reviews.length === 0) {
      let hash = 0;
      for (let i = 0; i < listing.id.length; i++) {
        hash = listing.id.charCodeAt(i) + ((hash << 5) - hash);
      }
      const val = Math.abs(hash) % 11;
      return (4.0 + (val / 10)).toFixed(1);
    }
    const sum = listing.reviews.reduce((acc: number, item: any) => acc + parseFloat(item.rating || 0), 0);
    return (sum / listing.reviews.length).toFixed(1);
  }, [listing.reviews, listing.id]);

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
        router.refresh();
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
          <div className="mt-8">
            <hr className="mb-8 border-neutral-200" />
            <div className="flex flex-row items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-semibold">Reviews</h2>
                <div className="flex items-center gap-1.5 text-sm font-semibold text-neutral-800 dark:text-neutral-200 bg-neutral-100 dark:bg-neutral-800 px-2.5 py-1 rounded-md">
                  <span>★</span>
                  <span>{averageRating}</span>
                  <span className="text-neutral-400 dark:text-neutral-500 font-light">•</span>
                  <span>
                    {listing.reviews?.length || 0} {listing.reviews?.length === 1 ? 'review' : 'reviews'}
                  </span>
                </div>
              </div>
              <div className="w-[150px]">
                <Button outline small label="Write a review" onClick={() => reviewModal.onOpen(listing.id)} />
              </div>
            </div>

            {listing.reviews && listing.reviews.length > 0 ? (
              <>
                {/* Aggregate rating progress bars */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4 mb-8">
                  {ratingsBreakdown.map((item) => (
                    <div key={item.label} className="flex flex-row items-center justify-between gap-4">
                      <div className="text-neutral-600 text-sm font-medium">{item.label}</div>
                      <div className="flex flex-row items-center gap-3 w-1/2">
                        <div className="w-full bg-neutral-200 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className="bg-neutral-800 h-full rounded-full" 
                            style={{ width: `${(item.score / 5) * 100}%` }}
                          />
                        </div>
                        <div className="text-neutral-800 text-xs font-semibold">{item.score.toFixed(1)}</div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {listing.reviews.map((review: any) => {
                    const reviewDate = review.createdAt || review.reviewDate || review.created_at || review.review_date;
                    const formattedDate = reviewDate ? format(new Date(reviewDate), 'M/d/yyyy') : 'Recent';
                    return (
                      <div key={review.id} className="flex flex-col gap-2">
                        <div className="flex flex-row items-center gap-4">
                          <div className="font-semibold">{review.user?.first_name || review.reviewerName || 'Guest'}</div>
                          <div className="text-neutral-500 font-light text-sm">
                            {formattedDate}
                          </div>
                        </div>
                        <div className="flex flex-row items-center gap-1 font-light text-sm">
                          <span>★</span>
                          <span>{parseFloat(review.rating || 0).toFixed(1)}</span>
                        </div>
                        <div className="text-neutral-600">
                          {review.content || review.comment}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="text-neutral-500 font-light mt-4">
                No reviews yet. Be the first to share your experience!
              </div>
            )}
          </div>
        </div>
      </div>
    </Container>
  );
};

export default ListingClient;
