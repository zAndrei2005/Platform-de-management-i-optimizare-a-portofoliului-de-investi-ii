from rest_framework import serializers
from .models import Asset, UserPortfolio

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__' 

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPortfolio
        fields = ['id', 'name', 'description', 'target_allocation'] 