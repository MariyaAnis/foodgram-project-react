from api.views import (IngredientViewSet,  # SubscriptionViewSet,
                       RecipeViewSet, SubscribeCreateDeleteView, TagViewSet,
                       UserViewSet)
from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', SubscribeCreateDeleteView.as_view(), name='subscribe'),
    # path('subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions')
]

