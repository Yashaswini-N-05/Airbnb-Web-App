import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface IParams {
  listingId?: string;
}

export const POST = async (request: Request, { params }: { params: IParams }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    // Send listing_id in snake_case — the camelCase parser converts body fields,
    // but to be safe we send snake_case which is what the backend model expects.
    const response = await axios.post(`${BACKEND_URL}/api/users/favorites/`, {
      listing_id: listingId
    }, { headers });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Error favoriting listing:', error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to favorite' }, { status: 500 });
  }
};

export const DELETE = async (request: Request, { params }: { params: IParams }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' };
    // Query params are NOT converted by camelCase middleware — must use snake_case
    const response = await axios.delete(`${BACKEND_URL}/api/users/favorites/`, {
      headers,
      params: { listing_id: listingId }
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Error unfavoriting listing:', error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to unfavorite' }, { status: 500 });
  }
};
