from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubnetRequestViewSet

router = DefaultRouter()
router.register(r'ping-requests', SubnetRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]