from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet,
                       SubscribeCreateDeleteView, TagViewSet, UserViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/',
         SubscribeCreateDeleteView.as_view(),
         name='subscribe'),
#     path('subscriptions/',
#          SubscribeCreateDeleteView.as_view(),
#          name='subscribe'),
# ]
]
