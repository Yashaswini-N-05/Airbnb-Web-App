import json
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import structlog
from django.core.management.base import BaseCommand, CommandError

from core.models import City, Country

logger = structlog.get_logger(__name__)


COUNTRIES_CITIES_URL = "https://countriesnow.space/api/v0.1/countries"
REST_COUNTRIES_URL = (
    "https://restcountries.com/v3.1/all"
    "?fields=cca2,cca3,name,currencies,idd"
)


class Command(BaseCommand):
    help = "Import countries and cities from public APIs into Country and City models."

    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("import_cities_started")
        self.stdout.write(self.style.MIGRATE_HEADING("Fetching country metadata (currencies, phone codes)..."))
        meta_by_iso2 = self._fetch_country_metadata()
        self.stdout.write(self.style.SUCCESS(f"Fetched metadata for {len(meta_by_iso2)} countries."))

        self.stdout.write(self.style.MIGRATE_HEADING("Fetching countries and cities..."))
        countries_data = self._fetch_countries_and_cities()
        self.stdout.write(self.style.SUCCESS(f"Fetched {len(countries_data)} countries with cities."))

        created_countries = 0
        updated_countries = 0
        created_cities = 0
        updated_cities = 0

        for item in countries_data:
            iso2 = (item.get("iso2") or "").upper()
            iso3 = (item.get("iso3") or "").upper()
            country_name = item.get("country") or ""
            cities = item.get("cities") or []

            if not iso2 or not iso3 or not country_name:
                continue

            meta = meta_by_iso2.get(iso2)
            if not meta:
                # Skip countries we cannot enrich with at least a currency code
                continue

            name = meta.get("name") or country_name
            currency_code = meta.get("currency")
            phone_code = meta.get("phone_code")

            if not currency_code:
                # Required field on Country model
                continue

            country, created = Country.all_objects.update_or_create(
                code=iso3,
                defaults={
                    "name": name,
                    "currency": currency_code,
                    "phone_code": phone_code,
                    "is_active": True,
                    "is_deleted": False,
                    "deleted_at": None,
                },
            )

            if created:
                created_countries += 1
            else:
                updated_countries += 1

            for city_name in cities:
                if not city_name:
                    continue

                city, city_created = City.all_objects.update_or_create(
                    name=city_name,
                    country=country,
                    defaults={
                        "latitude": None,
                        "longitude": None,
                        "timezone": None,
                        "is_popular": False,
                        "is_active": True,
                        "is_deleted": False,
                        "deleted_at": None,
                    },
                )

                if city_created:
                    created_cities += 1
                else:
                    updated_cities += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        self.stdout.write(
            f"Countries: {created_countries} created, {updated_countries} updated."
        )
        self.stdout.write(f"Cities: {created_cities} created, {updated_cities} updated.")

        logger.info(
            "import_cities_completed",
            created_countries=created_countries,
            updated_countries=updated_countries,
            created_cities=created_cities,
            updated_cities=updated_cities,
        )

    def _fetch_json(self, url: str) -> Any:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise CommandError(f"Failed to fetch {url}: HTTP {response.status}")
                raw = response.read()
        except (HTTPError, URLError) as exc:
            raise CommandError(f"Error fetching {url}: {exc}") from exc

        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON from {url}: {exc}") from exc

    def _fetch_country_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch metadata (name, currency, phone code) from restcountries API,
        keyed by ISO2 country code.
        """
        data = self._fetch_json(REST_COUNTRIES_URL)
        meta_by_iso2: Dict[str, Dict[str, Any]] = {}

        if not isinstance(data, list):
            raise CommandError("Unexpected response from restcountries API.")

        for item in data:
            if not isinstance(item, dict):
                continue

            iso2 = (item.get("cca2") or "").upper()
            if not iso2:
                continue

            name_info = item.get("name") or {}
            name_common = name_info.get("common")
            name_official = name_info.get("official")
            name = name_common or name_official

            currencies = item.get("currencies") or {}
            currency_code = None
            if isinstance(currencies, dict) and currencies:
                currency_code = next(iter(currencies.keys()), None)

            idd = item.get("idd") or {}
            root = idd.get("root") or ""
            suffixes = idd.get("suffixes") or []
            phone_code = None
            if root and isinstance(suffixes, list) and suffixes:
                phone_code = f"{root}{suffixes[0]}"

            meta_by_iso2[iso2] = {
                "name": name,
                "currency": currency_code,
                "phone_code": phone_code,
            }

        return meta_by_iso2

    def _fetch_countries_and_cities(self) -> List[Dict[str, Any]]:
        """
        Fetch list of countries with their cities from CountriesNow API.
        """
        payload = self._fetch_json(COUNTRIES_CITIES_URL)

        if not isinstance(payload, dict) or "data" not in payload:
            raise CommandError("Unexpected response from CountriesNow API.")

        if payload.get("error"):
            message = payload.get("msg") or "CountriesNow API returned an error."
            raise CommandError(message)

        data = payload.get("data") or []
        if not isinstance(data, list):
            raise CommandError("Unexpected data format from CountriesNow API.")

        return data

