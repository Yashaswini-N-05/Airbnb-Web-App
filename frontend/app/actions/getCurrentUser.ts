import axios from 'axios';
import { SafeUser } from '../types';
import { CURRENT_USER } from '@/app/config/currentUser';

const BACKEND_URL = 'http://localhost:8000';

const getCurrentUser = async (): Promise<SafeUser | null> => {
  try {
    const headers = { 'X-User-Id': CURRENT_USER };

    let favoriteIds: string[] = [];
    try {
      const favResponse = await axios.get(`${BACKEND_URL}/api/users/favorites/`, { headers });
      if (favResponse.data && favResponse.data.success && favResponse.data.data) {
        favoriteIds = favResponse.data.data.map((fav: any) => fav.listing.id);
      }
    } catch (favError) {
      // Ignore or log error
    }

    return {
      id: String(CURRENT_USER) as any,
      email: `user${String(CURRENT_USER)}@example.com`,
      name: `User ${String(CURRENT_USER)}`,
      image: null,
      hashedPassword: null,
      favoriteIds,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      emailVerified: new Date().toISOString(),
    };
  } catch (error: any) {
    return null;
  }
};

export default getCurrentUser;
