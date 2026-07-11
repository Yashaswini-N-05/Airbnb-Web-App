import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

interface IPararms {
  listingId?: string;
}

export const POST = async (request: Request, { params }: { params: IPararms }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    const response = await axios.post(`${BACKEND_URL}/api/favorites/`, {
      listingId: listingId
    }, { headers });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error favoriting listing:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to favorite' }, { status: 500 });
  }
};

export const DELETE = async (request: Request, { params }: { params: IPararms }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    const response = await axios.delete(`${BACKEND_URL}/api/favorites/`, {
      headers,
      params: { listingId }
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error unfavoriting listing:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to unfavorite' }, { status: 500 });
  }
};
