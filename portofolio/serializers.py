from rest_framework import serializers
from .models import Asset, UserPortfolio, PortfolioPosition

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class PortfolioPositionSerializer(serializers.ModelSerializer):
    asset_details = AssetSerializer(source='asset', read_only=True)

    class Meta:
        model = PortfolioPosition
        fields = ['id', 'asset', 'asset_details', 'quantity', 'purchase_price']

class PortfolioSerializer(serializers.ModelSerializer):
    positions = PortfolioPositionSerializer(many=True, read_only=True)

    class Meta:
        model = UserPortfolio
        fields = ['id', 'name', 'description', 'target_allocation', 'positions']