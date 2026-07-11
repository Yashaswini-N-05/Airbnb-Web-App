import React from 'react';
import getCurrentUser from '../actions/getCurrentUser';
import EmptyState from '../components/EmptyState';
import getReservations from '../actions/getReservations';
import ReservationsClient from './ReservationsClient';

const ReservationsPage = async () => {
  const currentUser = await getCurrentUser();

  if (!currentUser) {
    return <EmptyState title="Unauthorized" subtitle="Please login" />;
  }

  // Use the main host ID to load guest reservations on host properties (Step 15)
  const reservations = await getReservations({ authorId: "b210662e-633f-4666-bfb6-9d827ab696fb" });

  if (reservations.length === 0) {
    return (
      <EmptyState title="No reservations found" subtitle="Looks like you have no reservations on your properties" />
    );
  }
  return <ReservationsClient reservations={reservations} currentUser={currentUser} />;
};

export default ReservationsPage;
