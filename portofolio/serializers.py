import yfinance as yf
from rest_framework import serializers
from .models import Asset, UserPortfolio, PortfolioPosition, Transaction
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
    
    transaction_type = serializers.ChoiceField(choices=['BUY', 'SELL'], write_only=True, default='BUY')
    last_realized_profit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    last_estimated_tax = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = PortfolioPosition
        fields = ['id', 'portfolio', 'asset', 'asset_details', 'quantity', 'purchase_price', 'current_price', 'profit_loss', 'current_price_usd', 'purchase_price_usd', 'transaction_type', 'last_realized_profit', 'last_estimated_tax']
    
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
        tx_type = validated_data.pop("transaction_type", "BUY")
        portfolio = validated_data.get('portfolio')
        asset = validated_data.get('asset')
        new_quantity = validated_data.get('quantity')
        new_price = validated_data.get('purchase_price') or Decimal('0')

        existing_position = PortfolioPosition.objects.filter(portfolio=portfolio, asset=asset).first()

        if existing_position and not Transaction.objects.filter(portfolio=portfolio, asset=asset, transaction_type='BUY').exists():
            Transaction.objects.create(
                portfolio=portfolio,
                asset=asset,
                transaction_type='BUY',
                quantity=existing_position.quantity,
                price_per_share=existing_position.purchase_price or Decimal('0'),
                remaining_quantity=existing_position.quantity
            )

        if tx_type == "BUY":
            Transaction.objects.create(
                portfolio=portfolio,
                asset=asset,
                transaction_type='BUY',
                quantity=new_quantity,
                price_per_share=new_price,
                remaining_quantity=new_quantity
            )

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

        elif tx_type == "SELL":
            if not existing_position or existing_position.quantity < new_quantity:
                raise serializers.ValidationError({
                    "detail": "Nu deții suficiente unități în portofoliu pentru a efectua această vânzare."
                })

            buy_lots = Transaction.objects.filter(
                portfolio=portfolio,
                asset=asset,
                transaction_type='BUY',
                remaining_quantity__gt=0
            ).order_by('date', 'id')

            qty_to_sell = new_quantity
            realized_profit = Decimal('0')

            for lot in buy_lots:
                if qty_to_sell <= 0:
                    break
                used_qty = min(lot.remaining_quantity, qty_to_sell)
                realized_profit += used_qty * (new_price - lot.price_per_share)

                lot.remaining_quantity -= used_qty
                lot.save()
                qty_to_sell -= used_qty

            estimated_tax = round(realized_profit * Decimal('0.10'), 2) if realized_profit > 0 else Decimal('0.00')
            realized_profit = round(realized_profit, 2)

            Transaction.objects.create(
                portfolio=portfolio,
                asset=asset,
                transaction_type='SELL',
                quantity=new_quantity,
                price_per_share=new_price,
                remaining_quantity=Decimal('0'),
                realized_profit=realized_profit,
                estimated_tax=estimated_tax
            )

            final_quantity = existing_position.quantity - new_quantity
            if final_quantity <= 0:
                pos_id = existing_position.id
                existing_position.delete()
                existing_position.id = pos_id
                existing_position.quantity = Decimal('0')
            else:
                remaining_lots = Transaction.objects.filter(
                    portfolio=portfolio,
                    asset=asset,
                    transaction_type='BUY',
                    remaining_quantity__gt=0
                )
                total_remaining_cost = sum(l.remaining_quantity * l.price_per_share for l in remaining_lots)
                existing_position.quantity = final_quantity
                existing_position.purchase_price = round(total_remaining_cost / final_quantity, 2)
                existing_position.save()

            existing_position.last_realized_profit = realized_profit
            existing_position.last_estimated_tax = estimated_tax
            return existing_position

class PortfolioSerializer(serializers.ModelSerializer):
    positions = PortfolioPositionSerializer(many=True, read_only=True)

    class Meta:
        model = UserPortfolio   
        fields = ['id', 'name', 'description', 'target_allocation', 'positions']