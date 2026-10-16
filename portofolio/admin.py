from django.contrib import admin
from .models import Asset, UserPortfolio, PortfolioPosition,Transaction

admin.site.register(Asset)
admin.site.register(UserPortfolio)
admin.site.register(PortfolioPosition)
admin.site.register(Transaction)