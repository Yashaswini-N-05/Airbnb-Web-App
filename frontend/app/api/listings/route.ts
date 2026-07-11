import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export const POST = async (request: Request) => {
  try {
    const body = await request.json();
    const { category, location, guestCount, roomCount, bathroomCount, imageSrc, price, title, description } = body;

    if (!title || !description || !price || !imageSrc) {
      return NextResponse.json({ error: 'Missing listing information' }, { status: 400 });
    }

    // Map nextjs categories to Django property_type
    const propertyTypeMap: Record<string, string> = {
      'pools': 'villa',
      'beach': 'house',
      'windmills': 'other',
      'modern': 'apartment',
      'countryside': 'cottage',
      'islands': 'villa',
      'lake': 'house',
      'skiing': 'cabin',
      'castles': 'villa',
      'caves': 'other',
      'camping': 'cabin',
      'arctic': 'cabin',
      'desert': 'other',
      'barns': 'cottage',
      'lux': 'villa'
    };
    
    const categoryLower = category ? category.toLowerCase() : '';
    const property_type = propertyTypeMap[categoryLower] || 'apartment';

    const city = location?.region || location?.label || 'Miami';
    const country = location?.label || 'United States';
    const address = location?.label || '123 Main St';

    // Authenticate as a host (host1) using X-User-Id header
    const headers = { 'X-User-Id': 'b210662e-633f-4666-bfb6-9d827ab696fb' };

    // 1. Create the Listing
    const listingResponse = await axios.post(`${BACKEND_URL}/api/listings/`, {
      title,
      description,
      property_type,
      address,
      city,
      state: "",
      country,
      price_per_night: parseFloat(price),
      max_guests: guestCount || 1,
      bedrooms: roomCount || 1,
      bathrooms: bathroomCount || 1,
      beds: roomCount || 1,
      amenities: ["wifi", "kitchen", "air conditioning"],
      is_active: true
    }, { headers });

    const createdListing = listingResponse.data;
    const listingId = createdListing.id;

    // 2. Create the associated Image for this listing
    if (listingId && imageSrc) {
      try {
        await axios.post(`${BACKEND_URL}/api/listings/${listingId}/images/`, {
          url: imageSrc,
          caption: "Cover",
          is_cover: true,
          order: 0
        }, { headers });
      } catch (imgError) {
        console.error("Error uploading image for listing:", imgError);
      }
    }

    // Map response back to what the frontend expects
    const result = {
      id: listingId,
      title: createdListing.title,
      description: createdListing.description,
      imageSrc: imageSrc,
      category: category,
      roomCount: createdListing.bedrooms,
      bathroomCount: createdListing.bathrooms,
      guestCount: createdListing.maxGuests,
      locationValue: createdListing.country,
      price: Math.round(parseFloat(createdListing.pricePerNight)),
      userId: createdListing.host?.id || 'host-placeholder-id'
    };

    return NextResponse.json(result);
  } catch (error: any) {
    console.error("Error creating listing:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to create listing' }, { status: 500 });
  }
};
