import axios from 'axios';
import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

interface IParams {
  listingId?: string;
}

export const POST = async (request: Request, { params }: { params: IParams }) => {
  try {
    const { listingId } = params;
    if (!listingId) {
      return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
    }

    const body = await request.json();
    const { rating, content, title } = body;

    // Use default reviewer metadata
    const headers = { 'X-User-Id': '7bb66c05-0953-45ea-a835-41e39a9c61f8' }; // guest1
    
    const payload = {
      title: title || 'Stay Review',
      content: content,
      rating: parseFloat(rating),
      reviewer_name: 'Guest Tester',
      reviewer_country: 'United States',
      review_date: new Date().toISOString().split('T')[0],
    };

    const response = await axios.post(`${BACKEND_URL}/api/listings/${listingId}/reviews/`, payload, {
      headers,
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Error creating review:', error.response?.data || error.message);
    return NextResponse.json({ error: 'Failed to submit review' }, { status: 500 });
  }
};
