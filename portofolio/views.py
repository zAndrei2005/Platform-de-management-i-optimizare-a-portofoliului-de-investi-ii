from rest_framework import viewsets
from .models import Asset, UserPortfolio
from .serializers import AssetSerializer, PortfolioSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = UserPortfolio.objects.all()
    serializer_class = PortfolioSerializer