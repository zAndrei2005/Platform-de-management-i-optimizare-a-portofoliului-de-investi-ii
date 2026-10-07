from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, PortfolioViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'portfolios', PortfolioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]