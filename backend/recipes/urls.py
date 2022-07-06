from . import views

from django.urls import path

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.recipe_create, name='recipe_create'),
    path('tag/<slug:slug>/', views.tag, name='tag_recipes_list'),
    path('recipes/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipes/download_shopping_cart/', views.download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/add_shopping_cart', views.add_shopping_cart, name='add_shopping_cart'),
    path('recipes/<int:recipe_id>/add_favorite', views.add_favorite, name='add_favorite'),


]
