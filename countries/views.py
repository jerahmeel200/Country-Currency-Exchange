import os
import random
from datetime import datetime, timezone

from django.db import transaction
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Country, RefreshStatus
from .serializers import CountrySerializer
from .utils import fetch_countries_data, fetch_exchange_rates, generate_summary_image


EXCHANGE_API_NAME = "Exchange rates (open.er-api)"
COUNTRIES_API_NAME = "Countries (restcountries.com)"


class RefreshCountriesView(APIView):
    """
    POST /countries/refresh
    Fetch countries and exchange rates, then insert/update DB and generate summary image.
    """

    def post(self, request):
        # Step 1: Fetch external data
        try:
            countries_raw = fetch_countries_data()
        except Exception:
            return Response(
                {
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from {COUNTRIES_API_NAME}",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            exchange_rates = fetch_exchange_rates()
        except Exception:
            return Response(
                {
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from {EXCHANGE_API_NAME}",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        updated_at = datetime.now(timezone.utc)
        processed_countries = []
        invalid_entries = []

        os.makedirs("cache", exist_ok=True)  # Ensure cache folder exists

        try:
            with transaction.atomic():
                for item in countries_raw:
                    name = item.get("name")
                    capital = item.get("capital")
                    region = item.get("region")
                    population = item.get("population")
                    flag_url = item.get("flag")

                    # Validate required fields
                    if not name or population is None:
                        invalid_entries.append(name or "Unknown")
                        continue

                    currencies = item.get("currencies") or []
                    if not currencies:
                        currency_code = None
                        exchange_rate = None
                        estimated_gdp = 0.0
                    else:
                        currency_code = currencies[0].get("code")
                        if not currency_code:
                            exchange_rate = None
                            estimated_gdp = 0.0
                        else:
                            rate = exchange_rates.get(currency_code)
                            if not rate or rate == 0:
                                exchange_rate = None
                                estimated_gdp = None
                            else:
                                exchange_rate = float(rate)
                                multiplier = random.uniform(1000.0, 2000.0)
                                estimated_gdp = (float(population) * multiplier) / exchange_rate

                    # Case-insensitive upsert
                    existing = Country.objects.filter(name__iexact=name).first()
                    if existing:
                        existing.name = name
                        existing.capital = capital
                        existing.region = region
                        existing.population = int(population)
                        existing.currency_code = currency_code
                        existing.exchange_rate = exchange_rate
                        existing.estimated_gdp = estimated_gdp
                        existing.flag_url = flag_url
                        existing.save()
                    else:
                        Country.objects.create(
                            name=name,
                            capital=capital,
                            region=region,
                            population=int(population),
                            currency_code=currency_code,
                            exchange_rate=exchange_rate,
                            estimated_gdp=estimated_gdp,
                            flag_url=flag_url,
                        )

                    processed_countries.append(
                        {"name": name, "estimated_gdp": estimated_gdp}
                    )

                # Update RefreshStatus
                status_obj, _ = RefreshStatus.objects.get_or_create(id=1)
                status_obj.last_refreshed_at = updated_at
                status_obj.total_countries = Country.objects.count()
                status_obj.save()

                # Generate summary image
                top5 = sorted(
                    [c for c in processed_countries if c["estimated_gdp"] is not None],
                    key=lambda x: x["estimated_gdp"],
                    reverse=True,
                )[:5]
                generate_summary_image(
                    status_obj.total_countries,
                    top5,
                    updated_at,
                    path=os.path.join("cache", "summary.png"),
                )

        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Refresh completed",
                "total_countries": len(processed_countries),
                "invalid_entries": invalid_entries,
                "last_refreshed_at": updated_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )


class CountriesListView(APIView):
    """
    GET /countries?region=Africa&currency=NGN&sort=gdp_desc
    """

    def get(self, request):
        qs = Country.objects.all()
        region = request.query_params.get("region")
        currency = request.query_params.get("currency")
        sort = request.query_params.get("sort")

        if region:
            qs = qs.filter(region__iexact=region)
        if currency:
            qs = qs.filter(currency_code__iexact=currency)

        # Sorting
        sort_options = {
            "gdp_desc": "-estimated_gdp",
            "gdp_asc": "estimated_gdp",
            "population_desc": "-population",
            "population_asc": "population",
            "name_asc": "name",
            "name_desc": "-name",
        }
        if sort in sort_options:
            qs = qs.order_by(sort_options[sort])

        serializer = CountrySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryDetailView(APIView):
    """
    GET /countries/:name
    DELETE /countries/:name
    """

    def get_object(self, name):
        return Country.objects.filter(name__iexact=name).first()

    def get(self, request, name):
        obj = self.get_object(name)
        if not obj:
            return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CountrySerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, name):
        obj = self.get_object(name)
        if not obj:
            return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"message": "Country deleted"}, status=status.HTTP_200_OK)


class StatusView(APIView):
    """
    GET /status
    """

    def get(self, request):
        try:
            obj = RefreshStatus.objects.get(id=1)
        except RefreshStatus.DoesNotExist:
            return Response(
                {"total_countries": 0, "last_refreshed_at": None},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "total_countries": obj.total_countries,
                "last_refreshed_at": obj.last_refreshed_at.isoformat()
                if obj.last_refreshed_at
                else None,
            },
            status=status.HTTP_200_OK,
        )


class SummaryImageView(APIView):
    """
    GET /countries/image
    Serve cache/summary.png if exists, else return JSON error.
    """

    def get(self, request):
        path = os.path.join(os.getcwd(), "cache", "summary.png")
        if not os.path.exists(path):
            return Response(
                {"error": "Summary image not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(open(path, "rb"), content_type="image/png")
