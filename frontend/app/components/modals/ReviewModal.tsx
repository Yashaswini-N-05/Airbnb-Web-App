'use client';

import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FieldValues, SubmitHandler, useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

import useReviewModal from '@/app/hooks/useReviewModal';
import Heading from '../Heading';
import Input from '../inputs/Input';
import Modal from './Modal';

const ReviewModal = () => {
  const router = useRouter();
  const reviewModal = useReviewModal();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset,
  } = useForm<FieldValues>({
    defaultValues: {
      rating: 5,
      content: '',
      title: 'Amazing stay!',
    },
  });

  const rating = watch('rating');

  const setCustomValue = (id: string, value: any) => {
    setValue(id, value, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    });
  };

  const onSubmit: SubmitHandler<FieldValues> = (data) => {
    if (!reviewModal.listingId) return;

    setIsLoading(true);

    axios
      .post(`/api/listings/${reviewModal.listingId}/reviews`, data)
      .then(() => {
        toast.success('Review submitted successfully!');
        router.refresh();
        reset();
        reviewModal.onClose();
      })
      .catch(() => {
        toast.error('Something went wrong.');
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const bodyContent = (
    <div className="flex flex-col gap-4">
      <Heading title="Leave a review" subtitle="How was your stay at this property?" />
      
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-neutral-800">Rating (1 to 5 stars)</label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((val) => (
            <button
              key={val}
              type="button"
              onClick={() => setCustomValue('rating', val)}
              className={`px-4 py-2 border rounded-md transition ${
                rating === val 
                  ? 'bg-rose-500 text-white border-rose-500' 
                  : 'bg-white text-neutral-600 hover:bg-neutral-100 border-neutral-300'
              }`}
            >
              ★ {val}
            </button>
          ))}
        </div>
      </div>

      <Input
        id="title"
        label="Review Title"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />
      <Input
        id="content"
        label="Your review comment"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />
    </div>
  );

  return (
    <Modal
      disabled={isLoading}
      isOpen={reviewModal.isOpen}
      title="Write a Review"
      actionLabel="Submit Review"
      onClose={reviewModal.onClose}
      onSubmit={handleSubmit(onSubmit)}
      body={bodyContent}
    />
  );
};

export default ReviewModal;
