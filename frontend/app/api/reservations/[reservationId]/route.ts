import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface IPararms {
  reservationId?: string;
}

export const DELETE = async (request: Request, { params }: { params: IPararms }) => {
  try {
    const { reservationId } = params;
    if (!reservationId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    const response = await axios.post(`${BACKEND_URL}/api/bookings/${reservationId}/cancel/`, {}, {
      headers
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error deleting reservation:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to delete reservation' }, { status: 500 });
  }
};
