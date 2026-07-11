// Plain TS types replacing @prisma/client imports to avoid Edge Runtime conflicts
export type SafeListing = {
  id: string;
  title: string;
  description: string;
  imageSrc: string;
  createdAt: string;
  category: string;
  roomCount: number;
  bathroomCount: number;
  guestCount: number;
  locationValue: string;
  userId: string;
  price: number;
  reviews?: any[];
  [key: string]: any;
};

export type SafeReservation = {
  id: string;
  userId: string;
  listingId: string;
  startDate: string;
  endDate: string | null;
  totalPrice: number;
  createdAt: string;
  listing: SafeListing;
  [key: string]: any;
};

export type SafeUser = {
  id: string;
  name: string | null;
  email: string | null;
  emailVerified: string | null;
  image: string | null;
  createdAt: string;
  updatedAt: string;
  favoriteIds: string[];
  [key: string]: any;
};

