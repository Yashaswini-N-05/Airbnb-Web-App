import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface IParams {
  listingId?: string;
  userId?: string;
  authorId?: string;
}

export default async function getReservations(params: IParams) {
  try {
    const { listingId, userId, authorId } = params;

    const queryParams: any = {};
    if (listingId) {
      queryParams.listingId = listingId;
    }
    if (userId) {
      queryParams.userId = userId;
    }
    if (authorId) {
      queryParams.authorId = authorId;
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };

    const response = await axios.get(`${BACKEND_URL}/api/bookings/`, {
      params: queryParams,
      headers
    });

    let reservations = [];
    if (response.data) {
      if (Array.isArray(response.data)) {
        reservations = response.data;
      } else if (response.data.results && Array.isArray(response.data.results)) {
        reservations = response.data.results;
      } else if (response.data.data && Array.isArray(response.data.data)) {
        reservations = response.data.data;
      }
    }

    return reservations.map((res: any) => ({
      id: res.id,
      userId: res.user?.id || '',
      listingId: res.listing?.id || '',
      startDate: res.checkInDate,
      endDate: res.checkOutDate,
      totalPrice: Math.round(parseFloat(res.totalAmount || '0')),
      createdAt: res.createdAt || new Date().toISOString(),
      listing: {
        id: res.listing?.id || '',
        title: res.listing?.title || '',
        description: '',
        imageSrc: res.listing?.coverImage || 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80',
        createdAt: res.listing?.createdAt || new Date().toISOString(),
        category: 'apartment',
        roomCount: 1,
        bathroomCount: 1,
        guestCount: 2,
        locationValue: res.listing?.country || 'US',
        price: Math.round(parseFloat(res.listing?.pricePerNight || '100')),
        userId: 'host-placeholder-id',
      }
    }));
  } catch (error: any) {
    console.error("Error in getReservations:", error);
    return [];
  }
}
