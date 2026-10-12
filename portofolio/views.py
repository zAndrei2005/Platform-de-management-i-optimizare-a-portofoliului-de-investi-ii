from rest_framework import viewsets
from .models import Asset, UserPortfolio, PortfolioPosition
from .serializers import AssetSerializer, PortfolioSerializer, PortfolioPositionSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = UserPortfolio.objects.all()
    serializer_class = PortfolioSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = PortfolioPosition.objects.all()
    serializer_class = PortfolioPositionSerializer