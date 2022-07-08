# from django.core.paginator import Paginator
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
#
# from .models import Recipe
# from .forms import
# from foodgram.settings import COUNT_RECIPES_IN_PAGE
#
#
# def index(request):
#     recipe_list = Recipe.objects.all()
#     paginator = Paginator(recipe_list, COUNT_RECIPES_IN_PAGE)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     title = 'Последние обновления на сайте'
#     context = {
#         'page_obj': page_obj,
#         'title': title,
#     }
#     return render(request, 'posts/index.html', context)
