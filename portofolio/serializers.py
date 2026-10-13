import yfinance as yf
from rest_framework import serializers
from .models import Asset, UserPortfolio, PortfolioPosition
from decimal import Decimal

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class PortfolioPositionSerializer(serializers.ModelSerializer):
    asset_details = AssetSerializer(source='asset', read_only=True)
    current_price = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    
    current_price_usd = serializers.SerializerMethodField()
    purchase_price_usd = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioPosition
        fields = ['id', 'portfolio', 'asset', 'asset_details', 'quantity', 'purchase_price', 'current_price', 'profit_loss', 'current_price_usd', 'purchase_price_usd']
    
    def get_exchange_rate(self, currency):
        if currency == 'USD':
            return 1.0
        try:
            fx_ticker = f"{currency}USD=X"
            rate = yf.Ticker(fx_ticker).fast_info['last_price']
            return float(rate)
        except Exception:
            return 1.0 

    def get_current_price_usd(self, obj):
        price = self.get_current_price(obj)
        if price:
            rate = self.get_exchange_rate(obj.asset.currency)
            return round(float(price) * rate, 2)
        return None

    def get_purchase_price_usd(self, obj):
        if obj.purchase_price:
            rate = self.get_exchange_rate(obj.asset.currency)
            return round(float(obj.purchase_price) * rate, 2)
        return None
    
    def get_current_price(self, obj):
        try:
            ticker_data = yf.Ticker(obj.asset.ticker)
            price = ticker_data.fast_info['last_price']
            return round(price, 2)
        except Exception:
            return None

    def get_profit_loss(self, obj):
        current_price = self.get_current_price(obj)
        if current_price and obj.purchase_price:
            buy_price = float(obj.purchase_price)
            if buy_price > 0:
                profit = ((float(current_price) - buy_price) / buy_price) * 100
                return round(profit, 2)
        return None
    
    def create(self, validated_data):
        portfolio = validated_data.get('portfolio')
        asset = validated_data.get('asset')
        new_quantity = validated_data.get('quantity')
        new_price = validated_data.get('purchase_price') or Decimal('0')

        existing_position = PortfolioPosition.objects.filter(portfolio=portfolio, asset=asset).first()

        if existing_position:
            old_quantity = existing_position.quantity
            old_price = existing_position.purchase_price or Decimal('0')

            total_value_old = old_quantity * old_price
            total_value_new = new_quantity * new_price
            
            final_quantity = old_quantity + new_quantity
            
            if final_quantity > 0:
                avg_price = (total_value_old + total_value_new) / final_quantity
            else:
                avg_price = Decimal('0')

            existing_position.quantity = final_quantity
            existing_position.purchase_price = round(avg_price, 2)
            existing_position.save()
            
            return existing_position
        
        return super().create(validated_data)

class PortfolioSerializer(serializers.ModelSerializer):
    positions = PortfolioPositionSerializer(many=True, read_only=True)

    class Meta:
        model = UserPortfolio   
        fields = ['id', 'name', 'description', 'target_allocation', 'positions']