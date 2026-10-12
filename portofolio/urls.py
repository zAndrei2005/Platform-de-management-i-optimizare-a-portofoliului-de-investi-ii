from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, PortfolioViewSet, PositionViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'positions', PositionViewSet) 

urlpatterns = [
    path('', include(router.urls)),
]