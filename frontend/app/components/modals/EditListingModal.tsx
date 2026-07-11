'use client';

import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { FieldValues, SubmitHandler, useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

import useEditListingModal from '@/app/hooks/useEditListingModal';
import Heading from '../Heading';
import Input from '../inputs/Input';
import Modal from './Modal';

const EditListingModal = () => {
  const router = useRouter();
  const editModal = useEditListingModal();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
    reset,
  } = useForm<FieldValues>({
    defaultValues: {
      title: '',
      description: '',
      price: 1,
    },
  });

  useEffect(() => {
    if (editModal.listing) {
      setValue('title', editModal.listing.title);
      setValue('description', editModal.listing.description);
      setValue('price', editModal.listing.price);
    }
  }, [editModal.listing, setValue]);

  const onSubmit: SubmitHandler<FieldValues> = (data) => {
    if (!editModal.listing) return;

    setIsLoading(true);

    // Map frontend fields to backend expected fields
    const payload = {
      title: data.title,
      description: data.description,
      price_per_night: data.price,
    };

    axios
      .patch(`/api/listings/${editModal.listing.id}`, payload)
      .then(() => {
        toast.success('Listing updated!');
        router.refresh();
        reset();
        editModal.onClose();
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
      <Heading title="Edit your listing" subtitle="Update the details of your property" />
      <Input
        id="title"
        label="Title"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />
      <Input
        id="description"
        label="Description"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />
      <Input
        id="price"
        label="Price per night"
        formatPrice
        type="number"
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
      isOpen={editModal.isOpen}
      title="Edit Listing"
      actionLabel="Save Changes"
      onClose={editModal.onClose}
      onSubmit={handleSubmit(onSubmit)}
      body={bodyContent}
    />
  );
};

export default EditListingModal;
