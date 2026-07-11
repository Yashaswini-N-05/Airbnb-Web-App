'use client';

import { format } from 'date-fns';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import useCountries from '../../hooks/useCountries';
import { SafeListing, SafeReservation, SafeUser } from '../../types';
import Button from '../Button';
import HeartButton from '../HeartButton';

interface Props {
  data: SafeListing;
  reservation?: SafeReservation;
  onAction?: (id: string) => void;
  disabled?: boolean;
  actionLabel?: string;
  actionId?: string;
  currentUser?: SafeUser | null;
  onEdit?: (listing: SafeListing) => void;
}

const ListingCard: React.FC<Props> = ({
  data,
  reservation,
  onAction,
  disabled,
  actionLabel,
  actionId = '',
  currentUser,
  onEdit,
}) => {
  const router = useRouter();
  const { getByValue } = useCountries();

  const location = getByValue(data.locationValue);

  const handleCancel = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      e.stopPropagation();
      if (disabled) {
        return;
      }

      onAction?.(actionId);
    },
    [onAction, disabled, actionId]
  );

  const price = useMemo(() => {
    if (reservation) {
      return reservation.totalPrice;
    }

    return data.price;
  }, [reservation, data.price]);

  const reservationDate = useMemo(() => {
    if (!reservation) {
      return null;
    }
    const start = new Date(reservation.startDate);
    const end = new Date(reservation.endDate!);

    return `${format(start, 'PP')} - ${format(end, 'PP')}`;
  }, [reservation]);

  const rating = useMemo(() => {
    // Generate a pseudo-random but deterministic rating between 4.0 and 5.0 based on listing ID
    let hash = 0;
    for (let i = 0; i < data.id.length; i++) {
      hash = data.id.charCodeAt(i) + ((hash << 5) - hash);
    }
    const val = Math.abs(hash) % 11; // 0 to 10
    return (4.0 + (val / 10)).toFixed(1);
  }, [data.id]);

  return (
    <div onClick={() => router.push(`/listings/${data.id}`)} className="col-span-1 cursor-pointer group">
      <div className="flex flex-col gap-2 w-full">
        <div className="aspect-square w-full relative overflow-hidden rounded-xl">
          <Image
            alt="Listing"
            src={data.imageSrc}
            fill
            className="object-cover h-full w-full group-hover:scale-110 transition"
          />
          {parseFloat(rating) >= 4.8 && (
            <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm text-neutral-800 text-xs font-semibold px-2.5 py-1 rounded-md shadow-sm flex items-center gap-1 border border-neutral-200 z-10">
              <span className="text-amber-500 font-bold">★</span>
              <span>Superhost</span>
            </div>
          )}
          <div className="absolute top-3 right-3 z-10">
            <HeartButton listingId={data.id} currentUser={currentUser || null} />
          </div>
        </div>

        <div className="flex flex-row items-center justify-between gap-1">
          <div className="font-semibold text-lg">
            {location?.region} {location?.label}
          </div>
          <div className="flex flex-row items-center gap-1 font-light">
            <span>★</span>
            <span>{rating}</span>
          </div>
        </div>
        <div className="font-light text-neutral-500">{reservationDate || data.category}</div>
        <div className="flex flex-row items-center gap-1">
          <div className="font-semibold">$ {price}</div>
          {!reservation && <div className="font-light">night</div>}
        </div>

        {onAction && actionLabel && (
          <div className="flex flex-row gap-2 mt-2 w-full">
            {onEdit && (
              <Button
                disabled={disabled}
                small
                outline
                label="Edit"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(data);
                }}
              />
            )}
            <Button disabled={disabled} small label={actionLabel} onClick={handleCancel} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ListingCard;
