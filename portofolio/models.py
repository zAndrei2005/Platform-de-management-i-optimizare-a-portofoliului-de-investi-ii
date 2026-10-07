from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    ASSET_TYPES = [
        ('STOCK', 'Stock'),
        ('ETF', 'ETF'),
        ('CRYPTO', 'Cryptocurrency'),
        ('BOND', 'Bond'),
    ]
    ticker = models.CharField(max_length=15, unique=True) 
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    currency = models.CharField(max_length=3, default='USD')

    def __str__(self):
        return f"{self.ticker} ({self.name})"

class UserPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50) 
    description = models.TextField(blank=True, null=True)
    target_allocation = models.JSONField(default=dict) 

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('DIVIDEND', 'Dividend'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal')
    ]
    portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    date = models.DateTimeField()
    quantity = models.DecimalField(max_digits=18, decimal_places=8, default=0) 
    price_per_share = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    fees = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.asset} at {self.date.date()}"

class HistoricalPrice(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField()
    close_price = models.DecimalField(max_digits=18, decimal_places=4)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('asset', 'date')

    def __str__(self):
        return f"{self.asset.ticker} - {self.date}: {self.close_price}"