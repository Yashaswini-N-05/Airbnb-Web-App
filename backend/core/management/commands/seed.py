from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Image
from reviews.models import Review
from bookings.models import Booking, GuestDetail
from django.utils import timezone
import random
from datetime import timedelta, date


class Command(BaseCommand):
    help = "Seed database with hosts, listings, images, reviews, bookings"

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("Seeding database...")

        # Create 5 hosts
        hosts = []
        for i in range(1, 6):
            email = f"host{i}@example.com"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"host{i}",
                    "first_name": f"Host{i}",
                    "last_name": "Tester",
                    "role": "host",
                    "password": "pbkdf2_sha256$dummy$dummy$dummy",
                },
            )
            hosts.append(user)

        # Create 25 listings
        listings = []
        for i in range(1, 26):
            host = random.choice(hosts)
            listing, created = Listing.objects.get_or_create(
                title=f"Cozy Place #{i}",
                defaults={
                    "host": host,
                    "description": f"A lovely property number {i}.",
                    "property_type": "apartment",
                    "address": f"{i} Example St",
                    "city": "Sample City",
                    "country": "Sample Country",
                    "price_per_night": random.randint(2500, 9000),
                    "max_guests": random.randint(1, 6),
                    "bedrooms": random.randint(1, 4),
                    "bathrooms": random.randint(1, 3),
                    "beds": random.randint(1, 4),
                },
            )
            listings.append(listing)

        # Create 50 images across listings
        img_count = 0
        for listing in listings:
            imgs_for_listing = random.randint(1, 4)
            for j in range(imgs_for_listing):
                if img_count >= 50:
                    break
                Image.objects.get_or_create(
                    listing=listing,
                    url=f"https://picsum.photos/seed/{listing.pk}-{j}/800/600",
                    defaults={
                        "caption": f"Image {j+1} for {listing.title}",
                        "is_cover": j == 0,
                        "order": j,
                    },
                )
                img_count += 1
            if img_count >= 50:
                break

        # Create 10 reviews
        for i in range(1, 11):
            listing = random.choice(listings)
            user = random.choice(hosts)
            Review.objects.get_or_create(
                listing=listing,
                user=user,
                defaults={
                    "content": f"Sample review {i} for {listing.title}",
                    "rating": round(random.uniform(6.0, 10.0), 1),
                    "reviewer_name": f"Reviewer{i}",
                    "reviewer_country": "Wonderland",
                },
            )

        # Create 15 bookings with simple non-overlapping logic per listing
        bookings_created = 0
        today = date.today()
        for listing in listings:
            attempts = 0
            while bookings_created < 15 and attempts < 5:
                start = today + timedelta(days=random.randint(1, 60))
                nights = random.randint(1, 7)
                end = start + timedelta(days=nights)
                # Check overlap
                overlap = Booking.objects.filter(
                    listing=listing,
                    check_in_date__lt=end,
                    check_out_date__gt=start,
                ).exists()
                if not overlap:
                    user = random.choice(hosts)
                    booking = Booking.objects.create(
                        user=user,
                        listing=listing,
                        check_in_date=start,
                        check_out_date=end,
                        guests_count=1,
                        adults_count=1,
                        children_count=0,
                        total_nights=nights,
                        room_rate=listing.price_per_night,
                        taxes=0,
                        fees=0,
                        total_amount=listing.price_per_night * nights,
                        currency="USD",
                        status=Booking.STATUS_CONFIRMED,
                        payment_status=Booking.PAYMENT_PAID,
                    )
                    # create a guest detail
                    GuestDetail.objects.create(
                        booking=booking,
                        first_name="Guest",
                        last_name="Sample",
                        is_primary=True,
                    )
                    bookings_created += 1
                attempts += 1
            if bookings_created >= 15:
                break

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
