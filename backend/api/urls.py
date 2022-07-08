from django.urls import include, path
from rest_framework import routers

from api.views import RecipeViewSet, TagViewSet, FollowViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'subscriptions', FollowViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]