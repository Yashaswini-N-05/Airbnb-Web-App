from rest_framework import serializers
from .models import Country, City

class CountrySerializer(serializers.ModelSerializer):
    """Country serializer"""
    
    class Meta:
        model = Country
        fields = ["id", "name", "code", "currency", "phone_code", "is_active"]
        read_only_fields = ["id"]


class CitySerializer(serializers.ModelSerializer):
    """City serializer"""
    
    country_name = serializers.CharField(source="country.name", read_only=True)
    
    class Meta:
        model = City
        fields = ["id", "name", "country", "country_name", "latitude", "longitude", "timezone", "is_popular", "is_active"]
        read_only_fields = ["id"] 