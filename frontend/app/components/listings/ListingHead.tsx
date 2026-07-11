'use client';

import useCountries from '@/app/hooks/useCountries';
import { SafeUser } from '@/app/types';
import Image from 'next/image';
import Heading from '../Heading';
import HeartButton from '../HeartButton';

interface Props {
  title: string;
  imageSrc: string;
  locationValue: string;
  id: string;
  currentUser?: SafeUser | null;
}

const ListingHead: React.FC<Props> = ({ title, imageSrc, locationValue, id, currentUser }) => {
  const { getByValue } = useCountries();

  const location = getByValue(locationValue);

  const rating = (() => {
    let hash = 0;
    for (let i = 0; i < id.length; i++) {
      hash = id.charCodeAt(i) + ((hash << 5) - hash);
    }
    const val = Math.abs(hash) % 11;
    return (4.0 + (val / 10)).toFixed(1);
  })();

  return (
    <>
      <Heading title={title} subtitle={`${location?.region}, ${location?.label}`} />
      <div className="w-full h-[60vh] overflow-hidden rounded-xl relative">
        <Image alt="Image" src={imageSrc} fill className="object-cover w-full" />
        {parseFloat(rating) >= 4.8 && (
          <div className="absolute top-5 left-5 bg-white/95 backdrop-blur-sm text-neutral-800 text-sm font-semibold px-3 py-1.5 rounded-md shadow-md flex items-center gap-1 border border-neutral-200 z-10">
            <span className="text-amber-500 font-bold">★</span>
            <span>Superhost</span>
          </div>
        )}
        <div className=" absolute top-5 right-5 z-10">
          <HeartButton listingId={id} currentUser={currentUser || null} />
        </div>
      </div>
    </>
  );
};

export default ListingHead;
