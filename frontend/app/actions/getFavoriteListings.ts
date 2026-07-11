import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

export default async function getFavoriteListings() {
  try {
    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    const response = await axios.get(`${BACKEND_URL}/api/users/favorites/`, { headers });
    
    let favorites = [];
    if (response.data && response.data.success && response.data.data) {
      favorites = response.data.data;
    }

    return favorites.map((fav: any) => {
      const l = fav.listing;
      return {
        id: l.id,
        title: l.title,
        description: '',
        imageSrc: l.coverImage || 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80',
        createdAt: fav.createdAt || new Date().toISOString(),
        category: 'apartment',
        roomCount: 1,
        bathroomCount: 1,
        guestCount: 2,
        locationValue: l.country || 'US',
        price: Math.round(parseFloat(l.pricePerNight || '100')),
        userId: 'host-placeholder-id',
      };
    });
  } catch (error: any) {
    console.error("Error in getFavoriteListings:", error);
    return [];
  }
}
