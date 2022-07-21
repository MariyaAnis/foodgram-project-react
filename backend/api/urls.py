from django.urls import include, path
from rest_framework import routers
from djoser.views import UserViewSet

from api.views import RecipeViewSet, TagViewSet, IngredientViewSet, SubscriptionViewSet, SubscriptionCreateDeleteView

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
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}),  name='subscriptions'),
    path('users/<int:id>/subscribe/', SubscriptionCreateDeleteView.as_view(), name='subscribe'),
]

