# Airbnb Clone — SDE Fullstack Assignment

A full-stack Airbnb clone built with **Next.js 13** (frontend) and **Django REST Framework** (backend), using **SQLite** for persistence.

---

## 🗂 Project Structure

```
Airbnb/
├── backend/          # Django REST API
│   ├── backend/      # Django project settings & URLs
│   ├── users/        # Custom user model, auth, profiles
│   ├── listings/     # Property listings + images
│   ├── bookings/     # Reservation / booking system
│   ├── reviews/      # Listing reviews
│   ├── core/         # Shared models, countries
│   ├── utils/        # Helpers: auth, response, pagination
│   └── manage.py
│
└── frontend/         # Next.js 13 App Router
    ├── app/
    │   ├── actions/   # Server-side data fetching
    │   ├── api/       # Next.js API routes (proxy to backend)
    │   ├── components/# Reusable UI components
    │   ├── hooks/     # Zustand modal hooks
    │   ├── listings/  # Listing detail page
    │   ├── trips/     # My Trips page
    │   ├── favorites/ # Wishlist page
    │   ├── properties/# Host dashboard
    │   └── reservations/ # Host reservations view
    └── ...
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Seed database with sample data (listings, users, bookings)
python manage.py seed

# Start Django server
python manage.py runserver
```

Backend runs at: **http://localhost:8000**

API docs: **http://localhost:8000/api/docs/**

### 2. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 🏗 Architecture Overview

```
Browser  ──►  Next.js (3000)  ──►  Django REST API (8000)  ──►  SQLite
              App Router             DRF ViewSets
              Server Actions         AutoUserAuthentication
              Next.js API routes
```

### Authentication (Mocked for Evaluation)
Real auth is mocked. A seeded guest UUID is sent as the `X-User-Id` header from all Next.js API routes. Django's `AutoUserAuthentication` resolves this header to a real `User` instance from the database, so all database relations (bookings, favorites, listings) work correctly.

| Role | UUID |
|---|---|
| Guest (currentUser) | `7bb66c05-0953-45ea-a835-41e39a9c61f8` |
| Host (creates listings) | `b210662e-633f-4666-bfb6-9d827ab696fb` |

---

## 🗄 Database Schema

### `users_user`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | VARCHAR | Unique |
| full_name | VARCHAR | |
| role | VARCHAR | `guest` / `host` / `admin` |
| is_superhost | BOOLEAN | |
| avatar | URL | |
| date_joined | DATETIME | |

### `listings_listing`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| host_id | FK → user | |
| title | VARCHAR | |
| description | TEXT | |
| property_type | VARCHAR | apartment/house/villa/cabin/etc. |
| address, city, country | VARCHAR | |
| latitude, longitude | DECIMAL | |
| price_per_night | DECIMAL | |
| max_guests, bedrooms, bathrooms, beds | INT | |
| amenities | JSON | e.g. ["wifi","pool"] |
| is_active | BOOLEAN | |

### `listings_image`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| listing_id | FK → listing | |
| url | URLField | |
| is_cover | BOOLEAN | |
| order | INT | |

### `bookings_booking`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| booking_reference | VARCHAR | Unique e.g. TN-XXXXXXXX |
| user_id | FK → user | Guest |
| listing_id | FK → listing | |
| check_in_date | DATE | |
| check_out_date | DATE | |
| guests_count, adults_count | INT | |
| total_nights, room_rate | INT/DECIMAL | |
| taxes, fees, total_amount | DECIMAL | |
| status | VARCHAR | pending/confirmed/cancelled/etc. |
| payment_status | VARCHAR | pending/paid/refunded/etc. |

### `reviews_review`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| listing_id | FK → listing | |
| user_id | FK → user | |
| title | VARCHAR | |
| content | TEXT | |
| rating | DECIMAL | 0–10 |
| reviewer_name | VARCHAR | |

---

## 🔌 API Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/listings/` | List all active listings (filterable) |
| POST | `/api/listings/` | Create listing (host) |
| GET | `/api/listings/{id}/` | Listing detail |
| PATCH/DELETE | `/api/listings/{id}/` | Update/delete listing (host) |
| GET | `/api/listings/{id}/images/` | List images |
| POST | `/api/listings/{id}/images/` | Add image |
| GET | `/api/listings/{id}/reviews/` | List reviews |
| POST | `/api/listings/{id}/reviews/` | Add review |
| GET | `/api/bookings/` | User's bookings |
| POST | `/api/bookings/` | Create booking |
| DELETE | `/api/bookings/{id}/` | Cancel/delete booking |
| POST | `/api/bookings/{id}/complete-payment/` | Mock payment confirmation |
| GET | `/api/favorites/` | User's favorites |
| POST | `/api/favorites/` | Add favorite |
| DELETE | `/api/favorites/` | Remove favorite |
| GET | `/api/users/profile/` | Current user profile |
| GET | `/api/docs/` | Swagger UI (full API docs) |

---

## ✅ Features Implemented

- [x] Home page — listing grid with photo, title, location, price
- [x] Category filter row (Pools, Beach, Windmills, Modern, Countryside, etc.)
- [x] Search bar — location, date range, guest count
- [x] Shareable search URL filters
- [x] Listing detail page — gallery, description, host info, amenities, map
- [x] Date-range picker with booked dates blocked
- [x] Price breakdown (nightly rate × nights)
- [x] Reviews section on listing detail
- [x] End-to-end booking flow → persists to SQLite
- [x] My Trips (guest view of own bookings) + cancellation
- [x] Host: create listing (multi-step modal)
- [x] Host: delete listing
- [x] My Properties dashboard
- [x] My Reservations (host view of guest bookings on their properties)
- [x] Wishlist / Favorites (toggle + persist)
- [x] Toasts / notifications
- [x] Mock checkout (payment is simulated)
- [x] Seeded database (users, listings, bookings, reviews)
- [x] Swagger API docs at `/api/docs/`

---

## 📝 Assumptions & Notes

1. **Auth is mocked** — real user authentication (JWT, sessions) is scaffolded in Django but bypassed in the frontend via `X-User-Id` header. This is intentional for the evaluation demo.
2. **Payments are mocked** — `POST /api/bookings/{id}/complete-payment/` simulates payment without a real provider.
3. **Image upload** — images are stored as URLs (Unsplash / Cloudinary-compatible). The RentModal accepts any valid image URL.
4. **Map** — Leaflet renders based on country coordinates from the `world-countries` dataset.
5. **SQLite** — for development only. Swap `DATABASES` in `settings.py` for PostgreSQL in production.
