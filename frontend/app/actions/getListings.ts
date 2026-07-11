import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface IListingsParams {
  userId?: string;
  guestCount?: number;
  roomCount?: number;
  bathroomCount?: number;
  startDate?: string;
  endDate?: string;
  locationValue?: string;
  category?: string;
  page?: number;
}

export default async function getListings(params: IListingsParams) {
  try {
    const { userId, roomCount, guestCount, bathroomCount, locationValue, startDate, endDate, category } = params;

    const queryParams: any = {};
    if (userId) {
      queryParams.host = userId;
    }
    if (category) {
      const catLower = category.toLowerCase();
      const CATEGORY_MAP: Record<string, string> = {
        beach: 'house',
        windmills: 'cabin',
        modern: 'apartment',
        countryside: 'cottage',
        pools: 'villa',
        islands: 'villa',
        lake: 'cabin',
        skiing: 'cabin',
        castles: 'townhouse',
        camping: 'treehouse',
        arctic: 'cabin',
        cave: 'treehouse',
        desert: 'house',
        barns: 'cottage',
        lux: 'villa',
      };
      const mappedType = CATEGORY_MAP[catLower] || catLower;
      if (['apartment', 'house', 'villa', 'cabin', 'condo', 'cottage', 'studio', 'loft', 'townhouse', 'boat', 'treehouse'].includes(mappedType)) {
        queryParams.property_type = mappedType;
      }
    }
    if (locationValue) {
      queryParams.search = locationValue;
    }
    if (params.page) {
      queryParams.page = params.page;
    }

    const response = await axios.get(`${BACKEND_URL}/api/listings/`, {
      params: queryParams,
    });

    let listings = [];
    if (response.data) {
      if (Array.isArray(response.data)) {
        listings = response.data;
      } else if (response.data.results && Array.isArray(response.data.results)) {
        listings = response.data.results;
      } else if (response.data.data && Array.isArray(response.data.data)) {
        listings = response.data.data;
      }
    }
    
    // Map backend Listing structure to frontend Prisma expected structure
    return listings.map((l: any) => ({
      id: l.id,
      title: l.title,
      description: l.description || '',
      imageSrc: l.coverImage || 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80',
      createdAt: l.createdAt || new Date().toISOString(),
      category: l.propertyType || 'apartment',
      roomCount: l.bedrooms || 1,
      bathroomCount: l.bathrooms || 1,
      guestCount: l.maxGuests || 1,
      locationValue: l.country || 'US',
      price: Math.round(parseFloat(l.pricePerNight || '100')),
      userId: l.host?.id || 'host-id-placeholder',
    }));
  } catch (error: any) {
    console.error("Error in getListings:", error);
    return [];
  }
}
