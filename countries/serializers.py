from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id", "name", "capital", "region", "population",
            "currency_code", "exchange_rate", "estimated_gdp",
            "flag_url", "last_refreshed_at",
        ]

    def validate(self, data):
        errors = {}
        # name and population required (per validation rules)
        if not data.get("name"):
            errors["name"] = "is required"
        if data.get("population") is None:
            errors["population"] = "is required" 
        # currency_code can be null by spec for missing currencies
        if errors:
            raise serializers.ValidationError({"error": "validation failed", "details": errors})
        return data            