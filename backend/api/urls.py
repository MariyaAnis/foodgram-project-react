from django.urls import include, path
from rest_framework import routers
from djoser.views import UserViewSet

from api.views import RecipeViewSet, TagViewSet, IngredientViewSet, SubscriptionViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({'get': 'list'}),  name='subscribe'),
]
