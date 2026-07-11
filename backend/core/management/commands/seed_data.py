"""
Seed script: ensures Country and City exist, creates 30 users (20 guests, 10 hosts),
HotelType, HotelChain, Facilities, and inserts hotels with all fields plus rooms,
room amenities, bed types, and images. Raises if no countries or cities exist.
"""
import random
from decimal import Decimal
import time

import structlog
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from core.models import City, Country

logger = structlog.get_logger(__name__)
from facilities.models import Category, Facility
from hotels.models import Hotel, HotelImage, HotelType, HotelChain
from rooms.models import BedType, Room, RoomAmenity, RoomBedType, RoomImage


User = get_user_model()

DEFAULT_PASSWORD = "Abcdefgh.1"
GUEST_EMAIL_PREFIX = "guest"
HOST_EMAIL_PREFIX = "host"
EMAIL_DOMAIN = "example.com"
PLACEHOLDER_IMAGE = "https://picsum.photos/800/600"

SAMPLE_HOTEL_NAMES = [
    "Sunset Resort & Spa",
    "Grand Plaza Hotel",
    "Riverside Inn",
    "Mountain View Lodge",
    "Seaside Boutique Hotel",
    "City Center Suites",
    "Garden Palace Hotel",
    "Lakeside Retreat",
    "Urban Comfort Inn",
    "Heritage Grand Hotel",
    "Skyline Tower Hotel",
    "Tranquil Gardens Resort",
    "Harbor View Hotel",
    "Alpine Lodge",
    "Metro Express Inn",
    "Royal Bay Hotel",
    "Mirage Palace",
    "Cedar Grove Inn",
    "Pacific Dream Hotel",
    "Aurora Sands Resort",
    "Golden Leaf Suites",
    "Crystal Shores Hotel",
    "Oasis Downtown Inn",
    "Evergreen Retreat",
    "Vista Horizon Lodge",
    "Majestic Waters Hotel",
    "Cosmopolitan Grand",
    "Summit Heights Hotel",
    "Lagoon Prime Resort",
    "Pearl City Hotel",
    "The Urban Escape",
    "Whispering Pines Lodge",
    "Maple Crown Hotel",
    "Sunrise Waterfront Inn",
    "Cobalt City Suites",
    "Blossom Hill Hotel",
    "Serene Valley Resort",
]

HOTEL_TYPES = [
    (1, "Resort", "Full-service resort with amenities", "palm-tree"),
    (2, "Business Hotel", "For business travelers", "briefcase"),
    (3, "Boutique Hotel", "Small unique properties", "star"),
    (4, "Budget Hotel", "Affordable accommodation", "wallet"),
    (5, "Luxury Hotel", "Premium 5-star experience", "crown"),
]

HOTEL_CHAINS = [
    (1, "Grand Hotels International", "Luxury chain worldwide"),
    (2, "Comfort Stay", "Mid-scale family hotels"),
    (3, "Urban Nest", "City center boutique chain"),
    (4, "Sun & Sea Resorts", "Beach and resort properties"),
    (5, "Mountain Lodge Co", "Alpine and nature lodges"),
]

CATEGORIES_AND_FACILITIES = [
    ("Wellness", [
        ("Pool", "Swimming pool", "waves"),
        ("Spa", "Spa and wellness center", "spa"),
        ("Gym", "Fitness center", "dumbbell"),
    ]),
    ("Services", [
        ("WiFi", "Free WiFi", "wifi"),
        ("Parking", "Free parking", "car"),
        ("Breakfast", "Breakfast included", "coffee"),
        ("Room Service", "24h room service", "utensils"),
    ]),
    ("Accessibility", [
        ("Elevator", "Elevator access", "building"),
        ("Wheelchair", "Wheelchair accessible", "accessibility"),
    ]),
]

ROOM_AMENITIES = [
    ("TV", 1, "Flat-screen TV", "tv"),
    ("AC", 2, "Air conditioning", "snowflake"),
    ("Safe", 3, "In-room safe", "lock"),
    ("Minibar", 4, "Minibar", "wine"),
    ("Desk", 5, "Work desk", "desk"),
    ("Balcony", 6, "Private balcony", "sun"),
]

BED_TYPES = [
    ("Single bed(s)", "90-100 cm wide"),
    ("Double bed(s)", "131-150 cm wide"),
    ("Queen bed(s)", "151-180 cm wide"),
    ("King bed(s)", "181-210 cm wide"),
    ("Extra-large double bed(s)", "181-210 cm wide"),
]

ROOM_NAMES = [
    "Standard Double",
    "Deluxe King",
    "Superior Twin",
    "Executive Suite",
    "Family Room",
    "Ocean View Double",
    "Garden View Room",
]

HOTEL_DESCRIPTION_TEMPLATES = [
    "{} offers a comfortable stay in the heart of {}. Modern amenities and friendly service for business and leisure travelers.",
    "Welcome to {} in {}. A peaceful retreat with well-appointed rooms and convenient access to local attractions.",
    "{} combines comfort and style in {}. Enjoy a relaxing stay with quality service and thoughtful amenities.",
    "Experience {} in {}. Ideal for both short getaways and extended stays, with attentive staff and a welcoming atmosphere.",
    "{} is your home away from home in {}. Relax in our cozy rooms and make the most of your visit.",
]


class Command(BaseCommand):
    help = (
        "Insert seed data: require Country/City exist, create users, hotel types/chains, "
        "facilities, then hotels with all fields and rooms (amenities, bed types, images)."
    )

    def handle(self, *args, **options):
        logger.info("seed_data_started")
        try:
            self._require_countries_and_cities()
            hosts, guests = self._create_users()
            categories = self._create_categories()
            facilities = self._create_facilities(categories)
            hotel_types = self._create_hotel_types()
            chains = self._create_hotel_chains()
            room_amenities = self._create_room_amenities()
            bed_types = self._create_bed_types()
            self._create_hotels(
                hosts, facilities, hotel_types, chains, room_amenities, bed_types
            )
        except CommandError as exc:
            logger.warning("seed_data_command_error", error=str(exc))
            raise
        except Exception:
            logger.error("seed_data_failed", exc_info=True)
            raise
        logger.info("seed_data_completed")

    def _require_countries_and_cities(self):
        country_count = Country.objects.count()
        city_count = City.objects.count()
        if country_count == 0:
            raise CommandError(
                "No countries found. Run 'python manage.py import_cities' first to load countries and cities."
            )
        if city_count == 0:
            raise CommandError(
                "No cities found. Run 'python manage.py import_cities' first to load countries and cities."
            )
        self.stdout.write(
            self.style.SUCCESS(f"Found {country_count} countries and {city_count} cities.")
        )

    def _create_users(self):
        created_hosts = []
        created_guests = []
        for i in range(1, 11):
            email = f"{HOST_EMAIL_PREFIX}_{i}@{EMAIL_DOMAIN}"
            username = f"{HOST_EMAIL_PREFIX}_{i}"
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                user = User.objects.create(
                    email=email,
                    username=username,
                    first_name=f"Host{i}",
                    last_name="User",
                    role=User.HOST,
                    host_approval_status="approved",
                    is_verified_host=True,
                )
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            created_hosts.append(user)
        for i in range(1, 21):
            email = f"{GUEST_EMAIL_PREFIX}_{i}@{EMAIL_DOMAIN}"
            username = f"{GUEST_EMAIL_PREFIX}_{i}"
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                user = User.objects.create(
                    email=email,
                    username=username,
                    first_name=f"Guest{i}",
                    last_name="User",
                    role=User.GUEST,
                )
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            created_guests.append(user)
        self.stdout.write(
            self.style.SUCCESS(
                f"Users ready: {len(created_hosts)} hosts, {len(created_guests)} guests."
            )
        )
        return created_hosts, created_guests

    def _create_categories(self):
        categories = []
        for name, _ in CATEGORIES_AND_FACILITIES:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": f"{name} amenities", "is_active": True},
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"Categories/Facilities: {len(categories)} categories."))
        return categories

    def _create_facilities(self, categories):
        facilities = []
        for (cat_name, fac_list), category in zip(CATEGORIES_AND_FACILITIES, categories):
            for name, desc, icon in fac_list:
                fac, _ = Facility.objects.get_or_create(
                    name=name,
                    defaults={
                        "description": desc,
                        "icon": icon,
                        "category": category,
                        "is_active": True,
                    },
                )
                facilities.append(fac)
        self.stdout.write(self.style.SUCCESS(f"Facilities: {len(facilities)} created/ready."))
        return facilities

    def _create_hotel_types(self):
        created = []
        for type_id, name, desc, icon in HOTEL_TYPES:
            ht, _ = HotelType.objects.get_or_create(
                type_id=type_id,
                defaults={"name": name, "description": desc, "icon": icon, "is_active": True},
            )
            created.append(ht)
        self.stdout.write(self.style.SUCCESS(f"Hotel types: {len(created)}."))
        return created

    def _create_hotel_chains(self):
        countries = list(Country.objects.all()[:5])
        created = []
        for i, (chain_id, name, desc) in enumerate(HOTEL_CHAINS):
            country = countries[i % len(countries)] if countries else None
            ch, _ = HotelChain.objects.get_or_create(
                chain_id=chain_id,
                defaults={
                    "name": name,
                    "description": desc,
                    "headquarters_country": country,
                    "website": f"https://example.com/{name.lower().replace(' ', '-')}",
                    "is_active": True,
                },
            )
            created.append(ch)
        self.stdout.write(self.style.SUCCESS(f"Hotel chains: {len(created)}."))
        return created

    def _create_room_amenities(self):
        created = []
        for name, order, desc, icon in ROOM_AMENITIES:
            ra, _ = RoomAmenity.objects.get_or_create(
                name=name,
                defaults={"order": order, "description": desc, "icon": icon, "is_active": True},
            )
            created.append(ra)
        self.stdout.write(self.style.SUCCESS(f"Room amenities: {len(created)}."))
        return created

    def _create_bed_types(self):
        created = []
        for bed_type, size in BED_TYPES:
            bt, _ = BedType.objects.get_or_create(
                type=bed_type,
                defaults={"size": size},
            )
            created.append(bt)
        self.stdout.write(self.style.SUCCESS(f"Bed types: {len(created)}."))
        return created

    def _create_hotels(self, hosts, facilities, hotel_types, chains, room_amenities, bed_types):
        cities = list(City.objects.select_related("country").all())
        if not cities:
            raise CommandError("No cities available for hotels.")
        names_used_in_city = set()  # (name, city_id) to avoid duplicate name per city
        hotels_created = 0
        for idx, host in enumerate(hosts):
            for j in range(5):
                city = cities[(idx * 5 + j) % len(cities)]
                name = SAMPLE_HOTEL_NAMES[(idx * 5 + j) % len(SAMPLE_HOTEL_NAMES)]
                candidate = name
                k = 0
                key = (candidate, city.id)
                while key in names_used_in_city:
                    k += 1
                    candidate = f"{name} {k}"
                    key = (candidate, city.id)
                names_used_in_city.add(key)
                if Hotel.objects.filter(name=candidate, city=city).exists():
                    continue
                if Hotel.objects.filter(owner=host, name=candidate).exists():
                    continue
                stars = min(3 + (idx + j) % 3, 5)
                rating = Decimal(str(round(7.0 + random.uniform(0, 2.5), 1)))
                lat = city.latitude or Decimal(str(round(random.uniform(-90, 90), 6)))
                lon = city.longitude or Decimal(str(round(random.uniform(-180, 180), 6)))
                hotel_type = hotel_types[(idx + j) % len(hotel_types)]
                chain = chains[(idx + j) % len(chains)] if chains else None
                hotel_facilities = random.sample(facilities, min(random.randint(3, 7), len(facilities)))
                desc_tpl = HOTEL_DESCRIPTION_TEMPLATES[(idx + j) % len(HOTEL_DESCRIPTION_TEMPLATES)]
                description = desc_tpl.format(candidate, city.name)
                hotel = Hotel.objects.create(
                    name=candidate,
                    description=description,
                    owner=host,
                    city=city,
                    address=f"Sample address for {candidate}, {city.name}, {city.country.name}",
                    address_suburb=city.name,
                    stars=stars,
                    rating=rating,
                    ranking=idx * 5 + j,
                    reviews_count=random.randint(10, 500),
                    best_seller=random.choice([True, False]),
                    latitude=lat,
                    longitude=lon,
                    main_photo=PLACEHOLDER_IMAGE,
                    thumbnail=PLACEHOLDER_IMAGE,
                    hotel_type=hotel_type,
                    chain=chain,
                    is_active=True,
                )
                hotel.facilities.set(hotel_facilities)
                if not HotelImage.objects.filter(hotel=hotel).exists():
                    HotelImage.objects.create(
                        hotel=hotel,
                        url=PLACEHOLDER_IMAGE,
                        caption=f"Main view - {candidate}",
                        order=1,
                        default_image=True,
                    )
                num_rooms = random.randint(2, 4)
                for rn in range(num_rooms):
                    room_name = ROOM_NAMES[rn % len(ROOM_NAMES)]
                    if Room.objects.filter(hotel=hotel, name=room_name).exists():
                        room_name = f"{room_name} {rn + 1}"
                    adults = random.randint(2, 4)
                    children = random.randint(0, 2)
                    occupancy = adults + children
                    room_price = Decimal(str(round(random.uniform(80, 350), 2)))
                    room = Room.objects.create(
                        hotel=hotel,
                        name=room_name,
                        description=f"Comfortable {room_name.lower()} with modern amenities.",
                        size=random.randint(20, 45),
                        unit="m2",
                        adults=adults,
                        children=children,
                        occupancy=occupancy,
                        price=room_price,
                        is_active=True,
                    )
                    room.amenities.set(random.sample(room_amenities, min(3, len(room_amenities))))
                    bt = random.choice(bed_types)
                    RoomBedType.objects.get_or_create(
                        room=room,
                        bed_type=bt,
                        defaults={"quantity": 1},
                    )
                    if not RoomImage.objects.filter(room=room).exists():
                        RoomImage.objects.create(
                            room=room,
                            url=PLACEHOLDER_IMAGE,
                            description=room_name,
                            main_photo=(rn == 0),
                        )
                hotels_created += 1
                time.sleep(1)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {hotels_created} hotels with rooms, amenities, bed types, and images."
            )
        )
