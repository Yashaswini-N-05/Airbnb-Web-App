import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Image
from reviews.models import Review
from bookings.models import Booking, GuestDetail
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

User = get_user_model()

PROPERTY_TYPES = ["apartment", "house", "villa", "cabin", "condo", "cottage"]

AMENITIES_LIST = [
    "wifi", "pool", "parking", "kitchen", "air conditioning",
    "heating", "washer", "dryer", "tv", "gym", "hot tub",
    "pet friendly", "workspace", "elevator"
]

TITLES_AND_DESCRIPTIONS = [
    ("Cozy Beachfront Apartment", "A beautiful beachfront apartment with amazing ocean views, perfect for a relaxing getaway. Steps from the sand, restaurants, and shops. Includes fully equipped kitchen and high speed wifi."),
    ("Modern Downtown Loft", "Sleek and modern loft in the heart of downtown. Features double-height ceilings, floor-to-ceiling windows, design furniture, and access to a shared rooftop terrace with city views."),
    ("Luxury Forest Cabin", "Escape to nature in this luxury cabin tucked in the woods. Enjoy a private hot tub, wrap-around deck, outdoor fire pit, and stunning mountain views. Close to hiking and skiing."),
    ("Charming Garden Cottage", "Quaint and cozy cottage surrounded by lush gardens. Quiet neighborhood, perfect for solo travelers or couples. Easy access to public transport and local cafes."),
    ("Stunning Oceanview Villa", "An expansive luxury villa with a private infinity pool overlooking the ocean. Features 4 bedrooms, chef's kitchen, spacious living areas, and direct beach access. Unforgettable sunsets await!"),
    ("Minimalist City Studio", "Compact and functional studio apartment close to major sights and universities. Ideal for business travelers and tourists looking for a clean, convenient base."),
    ("Historic Townhouse", "Elegant townhouse with historic charm and modern amenities. High ceilings, original fireplaces, and a private brick patio. Located in a historic neighborhood near parks."),
    ("Scenic Mountain Lodge", "Spacious lodge in the mountains. High wood beams, indoor fireplace, and huge windows. Great for families and large groups. Near ski lifts and trailheads."),
    ("Peaceful Lakefront House", "Charming home right on the lake. Private dock, kayaks available, and a large deck for barbecues. Relax and enjoy the peace and quiet of lakeside living."),
    ("Contemporary Pool Oasis", "Beautiful modern home with a large private swimming pool, sun loungers, and outdoor dining area. Perfect for group vacations or family fun in the sun.")
]

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1527030280862-64139fbe04ca?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1602941525421-8f8b81d3edbb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1502005229762-fc1b2d812cae?auto=format&fit=crop&w=800&q=80",
]

CITIES = [
    ("Miami", "United States"),
    ("New York", "United States"),
    ("Los Angeles", "United States"),
    ("Denver", "United States"),
    ("Seattle", "United States"),
    ("Paris", "France"),
    ("London", "United Kingdom"),
    ("Tokyo", "Japan"),
    ("Rome", "Italy"),
    ("Barcelona", "Spain"),
]


class Command(BaseCommand):
    help = "Seeds the database with Airbnb-clone sample data: 5 hosts, 25 listings, 50 images, 10 reviews, and 15 bookings."

    def handle(self, *args, **options):
        import uuid
        from users.models import UserProfile
        self.stdout.write("Starting database seeding...")

        # Fixed UUIDs matching frontend config/currentUser.ts and page hardcodes
        MAIN_HOST_ID   = uuid.UUID("b210662e-633f-4666-bfb6-9d827ab696fb")
        MAIN_GUEST_ID  = uuid.UUID("7bb66c05-0953-45ea-a835-41e39a9c61f8")

        # 1. Create primary Host (fixed UUID so frontend hardcodes always match)
        main_host, created = User.objects.get_or_create(
            email="host1@example.com",
            defaults={
                "id": MAIN_HOST_ID,
                "username": "host_1",
                "first_name": "Jane",
                "last_name": "Smith",
                "role": User.HOST,
                "is_verified_host": True,
                "host_approval_status": "approved",
                "email_verified": True,
            }
        )
        if created:
            main_host.set_password("password123")
            main_host.save()
            UserProfile.objects.get_or_create(main_host, defaults={"bio": "Superhost with 5 years experience!"})
        # Ensure the UUID is always correct even if user existed with different id
        if str(main_host.id) != str(MAIN_HOST_ID):
            User.objects.filter(pk=main_host.pk).update(id=MAIN_HOST_ID)
            main_host.refresh_from_db()

        # 2. Create primary Guest (fixed UUID so AutoUserAuthentication always finds them)
        main_guest, created = User.objects.get_or_create(
            email="guest1@example.com",
            defaults={
                "id": MAIN_GUEST_ID,
                "username": "guest_1",
                "first_name": "Alex",
                "last_name": "Johnson",
                "role": User.GUEST,
                "email_verified": True,
            }
        )
        if created:
            main_guest.set_password("password123")
            main_guest.save()
            UserProfile.objects.get_or_create(main_guest, defaults={"bio": "Love travelling!"})
        if str(main_guest.id) != str(MAIN_GUEST_ID):
            User.objects.filter(pk=main_guest.pk).update(id=MAIN_GUEST_ID)
            main_guest.refresh_from_db()

        # 3. Create 4 more Host Users
        hosts = [main_host]
        for i in range(2, 6):
            email = f"host{i}@example.com"
            username = f"host_{i}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "first_name": f"HostFirst{i}",
                    "last_name": f"HostLast{i}",
                    "role": User.HOST,
                    "is_verified_host": True,
                    "host_approval_status": "approved",
                    "email_verified": True,
                }
            )
            if created:
                user.set_password("password123")
                user.save()
                UserProfile.objects.get_or_create(user=user, defaults={"bio": f"Hi, I am Host {i}!"})
            hosts.append(user)

        self.stdout.write(f"Seeded {len(hosts)} Host Users.")

        # 4. Create 4 more Guest Users
        guests = [main_guest]
        for i in range(2, 6):
            email = f"guest{i}@example.com"
            username = f"guest_{i}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "first_name": f"GuestFirst{i}",
                    "last_name": f"GuestLast{i}",
                    "role": User.GUEST,
                    "email_verified": True,
                }
            )
            if created:
                user.set_password("password123")
                user.save()
                UserProfile.objects.get_or_create(user=user, defaults={"bio": f"Hi, I am Guest {i}!"})
            guests.append(user)

        self.stdout.write(f"Seeded {len(guests)} Guest Users.")

        # Delete existing Listings/Images/Reviews/Bookings to have a clean count
        Image.objects.all().delete()
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()

        # 2. Create 25 Listings
        listings = []
        for i in range(25):
            title_base, desc = random.choice(TITLES_AND_DESCRIPTIONS)
            title = f"{title_base} #{i+1}"
            host = random.choice(hosts)
            property_type = random.choice(PROPERTY_TYPES)
            city_info = random.choice(CITIES)
            
            listing = Listing.objects.create(
                host=host,
                title=title,
                description=desc,
                property_type=property_type,
                address=f"{random.randint(10, 999)} Main Street",
                city=city_info[0],
                country=city_info[1],
                latitude=Decimal(f"{random.uniform(-90, 90):.6f}"),
                longitude=Decimal(f"{random.uniform(-180, 180):.6f}"),
                price_per_night=Decimal(f"{random.randint(50, 500)}.00"),
                max_guests=random.randint(1, 8),
                bedrooms=random.randint(1, 4),
                bathrooms=random.randint(1, 3),
                beds=random.randint(1, 5),
                amenities=random.sample(AMENITIES_LIST, random.randint(3, 8)),
                is_active=True
            )
            listings.append(listing)

        self.stdout.write(f"Seeded {len(listings)} Listings.")

        # 3. Create 50 Images (2 images per listing)
        images_created = 0
        for listing in listings:
            # Main Cover Image
            url1 = random.choice(IMAGE_URLS)
            Image.objects.create(
                listing=listing,
                url=url1,
                caption="Main Area",
                is_cover=True,
                order=0
            )
            # Secondary Image
            url2 = random.choice([u for u in IMAGE_URLS if u != url1])
            Image.objects.create(
                listing=listing,
                url=url2,
                caption="Cozy Corner",
                is_cover=False,
                order=1
            )
            images_created += 2

        self.stdout.write(f"Seeded {images_created} Images.")

        # 4. Create 10 Reviews
        for i in range(10):
            listing = random.choice(listings)
            user = random.choice(guests)
            rating = Decimal(f"{random.randint(7, 10)}.0")
            Review.objects.create(
                listing=listing,
                user=user,
                title="Amazing stay!",
                content="The place was extremely clean and spacious. The host was incredibly welcoming and helpful. Highly recommended!",
                rating=rating,
                reviewer_name=user.get_full_name(),
                reviewer_country=user.country or "USA",
                review_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                is_active=True,
                is_verified=True
            )

        self.stdout.write("Seeded 10 Reviews.")

        # 5. Create 15 Bookings (at least 3 must belong to main_guest so Trips page works)
        booking_count = 0
        attempts = 0
        main_guest_bookings = 0
        while booking_count < 15 and attempts < 100:
            attempts += 1
            listing = random.choice(listings)
            # Force main_guest for the first 3 bookings
            guest = main_guest if main_guest_bookings < 3 else random.choice(guests)
            
            # Generate random start and end dates
            start_offset = random.randint(1, 90)
            length = random.randint(2, 7)
            check_in = timezone.now().date() + timedelta(days=start_offset)
            check_out = check_in + timedelta(days=length)
            
            # Check for overlaps
            overlapping = Booking.objects.filter(
                listing=listing,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).exists()
            
            if not overlapping:
                total_nights = (check_out - check_in).days
                total_amount = listing.price_per_night * total_nights
                
                booking = Booking.objects.create(
                    user=guest,
                    listing=listing,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    guests_count=random.randint(1, listing.max_guests),
                    adults_count=1,
                    children_count=0,
                    room_rate=listing.price_per_night,
                    total_amount=total_amount,
                    currency="USD",
                    status=Booking.STATUS_CONFIRMED,
                    payment_status=Booking.PAYMENT_PAID
                )
                
                # Create Guest Detail
                GuestDetail.objects.create(
                    booking=booking,
                    first_name=guest.first_name,
                    last_name=guest.last_name,
                    email=guest.email,
                    is_primary=True
                )
                
                booking_count += 1
                if guest == main_guest:
                    main_guest_bookings += 1

        self.stdout.write(f"Seeded {booking_count} Bookings (took {attempts} attempts).")
        self.stdout.write("Database seeding completed successfully!")
