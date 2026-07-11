import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

interface IPararms {
  listingId?: string;
}

export const DELETE = async (request: Request, { params }: { params: IPararms }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    // Authenticate as host1
    const headers = { 'X-User-Id': 'b210662e-633f-4666-bfb6-9d827ab696fb' };
    const response = await axios.delete(`${BACKEND_URL}/api/listings/${listingId}/`, {
      headers
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error deleting listing:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to delete listing' }, { status: 500 });
  }
};

export const PATCH = async (request: Request, { params }: { params: IPararms }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const body = await request.json();
    
    // Authenticate as host1
    const headers = { 'X-User-Id': 'b210662e-633f-4666-bfb6-9d827ab696fb' };
    const response = await axios.patch(`${BACKEND_URL}/api/listings/${listingId}/`, body, {
      headers
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error updating listing:", error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to update listing' }, { status: 500 });
  }
};
