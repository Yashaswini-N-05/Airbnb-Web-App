import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const POST = async (request: Request) => {
  try {
    const body = await request.json();
    const { listingId, startDate, endDate } = body;

    if (!listingId || !startDate || !endDate) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    const checkIn = new Date(startDate).toISOString().split('T')[0];
    const checkOut = new Date(endDate).toISOString().split('T')[0];

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };

    const response = await axios.post(`${BACKEND_URL}/api/bookings/`, {
      listing_id: listingId,
      check_in_date: checkIn,
      check_out_date: checkOut,
      guests_count: 1,
      adults_count: 1,
      children_count: 0,
      special_requests: "Booked from NextJS frontend",
      guest_details: [
        {
          first_name: "GuestFirst1",
          last_name: "GuestLast1",
          email: "guest1@example.com",
          is_primary: true
        }
      ]
    }, { headers });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error creating booking in NextJS api/reservations route:", error.response?.data || error.message);
    const errData = error.response?.data;
    const errMsg = errData?.errors || errData?.detail || 'Booking validation failed: overlapping dates or invalid data.';
    return NextResponse.json({ error: errMsg }, { status: error.response?.status || 400 });
  }
};
