import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface IParams {
  listingId?: string;
}

export default async function getListingById(params: IParams) {
  try {
    const { listingId } = params;
    if (!listingId) {
      return null;
    }

    const response = await axios.get(`${BACKEND_URL}/api/listings/${listingId}/`);
    let l = response.data;
    if (l && l.data && !l.id) {
      l = l.data;
    }

    if (!l) {
      return null;
    }

    return {
      id: l.id,
      title: l.title,
      description: l.description || '',
      imageSrc: l.images?.[0]?.url || 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80',
      createdAt: l.createdAt || new Date().toISOString(),
      category: l.propertyType || 'apartment',
      roomCount: l.bedrooms || 1,
      bathroomCount: l.bathrooms || 1,
      guestCount: l.maxGuests || 1,
      locationValue: l.country || 'US',
      price: Math.round(parseFloat(l.pricePerNight || '100')),
      reviews: l.reviews || [],
      userId: l.host?.id || 'host-id-placeholder',
      user: {
        id: l.host?.id || 'host-id-placeholder',
        name: l.host?.fullName || 'Host User',
        email: l.host?.email || 'host@example.com',
        image: l.host?.avatar || null,
        hashedPassword: null,
        favoriteIds: [],
        createdAt: l.host?.dateJoined || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        emailVerified: null,
      }
    };
  } catch (error: any) {
    console.error("Error in getListingById:", error);
    return null;
  }
}
